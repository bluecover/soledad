# coding: utf-8

from __future__ import absolute_import

from flask_script import Manager
from gunicorn.app.wsgiapp import WSGIApplication

from jupiter.ext import sentry, yixin, zslib, zhiwang, xinmi
from jupiter.wsgi import app
from jupiter.workers import pool as mq_pool
from jupiter.managers.oauth import manager as oauth_manager
from jupiter.managers.yixin import manager as yixin_manager
from jupiter.managers.wallet import manager as wallet_manager
from jupiter.managers.zhiwang import manager as zhiwang_manager
from jupiter.managers.xinmi import manager as xinmi_manager
from jupiter.managers.sxb import manager as sxb_manager
from libs.cache import mc
from libs.db.store import db


manager = Manager(app)
manager.add_command('oauth', oauth_manager)
manager.add_command('yixin', yixin_manager)
manager.add_command('wallet', wallet_manager)
manager.add_command('zhiwang', zhiwang_manager)
manager.add_command('xinmi', xinmi_manager)
manager.add_command('sxb', sxb_manager)


@manager.shell
def make_shell_context():
    return {'db': db, 'app': app, 'yixin': yixin, 'zslib': zslib,
            'zwlib': zhiwang, 'xmlib': xinmi, 'sentry': sentry, 'mc': mc}


@manager.command
def runserver(host=None, port=None, workers=None):
    """Runs the app within Gunicorn."""
    host = host or app.config.get('HTTP_HOST') or '0.0.0.0'
    port = port or app.config.get('HTTP_PORT') or 5000
    workers = workers or app.config.get('HTTP_WORKERS') or 1
    use_evalex = app.config.get('USE_EVALEX', app.debug)

    if app.debug:
        app.run(host, int(port), use_evalex=use_evalex)
    else:
        gunicorn = WSGIApplication()
        gunicorn.load_wsgiapp = lambda: app
        gunicorn.cfg.set('bind', '%s:%s' % (host, port))
        gunicorn.cfg.set('workers', workers)
        gunicorn.cfg.set('pidfile', None)
        gunicorn.cfg.set('accesslog', '-')
        gunicorn.cfg.set('errorlog', '-')
        gunicorn.chdir()
        gunicorn.run()


@manager.command
def runworker():
    """Runs workers to consume offline tasks."""
    mq_pool.spawn_all()


def main():
    manager.run()


if __name__ == '__main__':
    main()
