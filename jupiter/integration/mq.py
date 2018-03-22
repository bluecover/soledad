# coding: utf-8

import logging
import multiprocessing

from beanstalkc import Connection
from werkzeug.urls import url_parse
from werkzeug.utils import cached_property
from caoe import install as install_caoe

from jupiter.app import create_app
from jupiter.ext import sentry
from libs.utils.log import bcolors


class MessageQueuePool(object):
    """The connection pool of beanstalkd."""

    def __init__(self, dsn, queue_class=None, worker_class=None):
        self.dsn = dsn
        self.queues = {}
        self.queue_class = MessageQueue if queue_class is None else queue_class
        self.worker_class = Worker if worker_class is None else worker_class
        self.workers = set()

    def __repr__(self):
        return 'MessageQueuePool(%r)' % (self.dsn)

    def make_connection(self):
        dsn = url_parse(self.dsn)
        if dsn.scheme != 'beanstalkd':
            raise ValueError('invalid beanstalkd dsn')
        return Connection(host=dsn.host, port=dsn.port)

    def get_by_tube(self, tube):
        if tube not in self.queues:
            self.queues[tube] = self.queue_class(self, tube)
        return self.queues[tube]

    def async_worker(self, tube):
        """The decorator to wrap a function into a worker."""
        def decorator(target):
            worker = self.worker_class(target, tube, self)
            worker.register()
            return worker
        return decorator

    def spawn_all(self):
        """Spawns processes to consume jobs."""
        install_caoe()  # kill all children processes when the parent dies
        processes = [
            multiprocessing.Process(target=w.loop) for w in self.workers]
        for process in processes:
            process.start()


class MessageQueue(object):
    """The broker of beanstalkd."""

    def __init__(self, pool, tube):
        self.pool = pool
        self.tube = tube

    def __repr__(self):
        return 'MessageQueue(%r, %r)' % (self.pool, self.tube)

    def __getattr__(self, name):
        if name != 'connection' and not name.startswith('_'):
            return getattr(self.connection, name)
        return object.__getattribute__(self, name)

    @cached_property
    def connection(self):
        connection = self.pool.make_connection()
        connection.ignore('default')
        connection.use(self.tube)
        connection.watch(self.tube)
        return connection


class Worker(object):
    """The consumer of a message queue."""

    def __init__(self, target, tube, mq_pool):
        self.target = target
        self.tube = tube
        self.mq_pool = mq_pool

    def __repr__(self):
        return 'Worker(%s, %r, %r)' % (
            self.target.__name__, self.tube, self.mq_pool)

    def loop(self):
        app = create_app()
        with app.app_context():
            bcolors.run('Worker start at mq tube [%s]...' % self.tube)
            try:
                while True:
                    self.consume()
            except KeyboardInterrupt:
                bcolors.success(
                    'Worker at mq tube [%s] success stopped.' % self.tube)

    def register(self):
        self.mq_pool.workers.add(self)

    def get_broker(self):
        return self.mq_pool.get_by_tube(self.tube)

    def produce(self, body, delay=0):
        broker = self.get_broker()
        return broker.put(body, delay=delay)

    def consume(self):
        broker = self.get_broker()
        job = broker.reserve()
        if job is None:
            return
        bcolors.success('Get job %s' % job.jid)
        self._send_log('get job %s' % job.jid)

        try:
            self.target(job.body)
        except KeyboardInterrupt:
            job.bury()
            raise
        except WorkerTaskError:
            sentry.captureException(level=logging.WARNING)
            job.bury()
        except Exception as e:
            sentry.captureException()
            bcolors.fail('job %s failed and bury. %s' % (
                job.jid, unicode(e).encode('utf-8')))
            self._send_log(
                'job %s failed and buried because %s' %
                (job.jid, unicode(e).encode('utf-8')))
            job.bury()
        else:
            bcolors.success('Job process success.')
            job.delete()
            self._send_log('job %s deleted' % job.jid)

    def _send_log(self, text):
        from libs.logger.rsyslog import rsyslog
        rsyslog.send(text, tag='mq_' + self.tube)


class WorkerTaskError(Exception):
    pass
