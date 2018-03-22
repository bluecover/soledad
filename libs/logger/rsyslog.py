from logging import Formatter
from logging.handlers import SocketHandler

from solar.logger.rsyslog import RSYSLog
from solar.logger.rsyslog.context import init_context


__all__ = ['RsyslogHandler', 'rsyslog']


class RsyslogHandler(SocketHandler):

    terminator = '\n'

    def makePickle(self, record):  # noqa: override
        message = self.format(record)
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        message = message.replace(self.terminator, '\t')
        return message + self.terminator


def make_rsyslog():
    context = init_context('solar')
    return RSYSLog.init_by_context(context)


def make_rsyslog_handler(host, port):
    rsyslog_formatter = Formatter(
        '%(name)s:%(asctime)s\t%(levelname)s\t%(message)s', '%H:%M:%S')
    rsyslog_handler = RsyslogHandler(host, port)
    rsyslog_handler.setFormatter(rsyslog_formatter)
    return rsyslog_handler


rsyslog = make_rsyslog()
rsyslog_handler = make_rsyslog_handler(rsyslog.host, rsyslog.port)
