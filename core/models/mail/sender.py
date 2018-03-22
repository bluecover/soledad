# -*- coding: utf-8 -*-

import socket
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from core.models.consts import SITE_NAME_CN
from .consts import HIGH_PRIORITY, NORMAL_PRIORITY, SenderType


TIMEOUT = 3

SMTP_SERVER = 'smtpcloud.sohu.com:25'

HMAIL = 'service@mail.guihua.com'
MAIL = 'service@email.guihua.com'

mail_split = '--split--'


def default_callback(mail):
    print mail


def default_error_handler(mail):
    print mail


class SenderPool(object):

    _senders = {}

    def get_sender(self, sender_type):
        _sender = None
        if sender_type is SenderType.normal:
            _sender = Sender()
        else:
            _sender = MultiSender()
        if not self._senders.get(sender_type.value):
            if _sender:
                self._senders[sender_type.value] = _sender
        return self._senders[sender_type.value]


def get_sender_pool():
    if not getattr(get_sender_pool, '_pool', None):
        get_sender_pool.singleton = SenderPool()
    return get_sender_pool.singleton


class Sender(object):
    connected = False

    USER_NAME = 'postmaster@haoguihua.sendcloud.org'
    PASSWORD = 'o3XucEj6pa4Oe3ai'

    def __init__(self):
        self.smtp = None
        self.smtp_conf = ''

    def connect(self):
        self.smtp = smtplib.SMTP(SMTP_SERVER)
        self.smtp.login(self.USER_NAME, self.PASSWORD)
        self.smtp_conf = MAIL
        self.connected = True

    def reconnect(self):
        self.disconnect()
        self.connect()

    def disconnect(self):
        try:
            if self.smtp:
                self.smtp.quit()
                self.smtp.close()
            self.connected = False
        except smtplib.SMTPServerDisconnected:
            pass

    def send_mail(self, subject, body, recipient, recipient_name='',
                  sender=MAIL, sender_name=SITE_NAME_CN,
                  priority=NORMAL_PRIORITY):
        socket.setdefaulttimeout(TIMEOUT)
        if priority == HIGH_PRIORITY:
            sender = HMAIL
        msg = MIMEMultipart('alternative')
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8')
        msg['Subject'] = subject
        msg['From'] = formataddr((str(Header(sender_name, 'utf-8')),
                                  sender))
        msg['To'] = formataddr((str(Header(recipient_name, 'utf-8')),
                                recipient))

        part = MIMEText(body, 'html', 'utf-8')
        msg['Accept-Language'] = 'zh-CN'
        msg['Accept-Charset'] = 'ISO-8859-1,utf-8'
        msg.attach(part)

        if not self.smtp:
            self.connect()

        max_try = 3
        r = False

        while(max_try):
            try:
                self.smtp.sendmail(sender, recipient, msg.as_string())
                r = True
                break
            except (smtplib.SMTPServerDisconnected, socket.timeout):
                if max_try == 1:
                    raise
                self.reconnect()
            finally:
                max_try -= 1

        return r


class MultiSender(Sender):
    USER_NAME = 'postmaster@haoguihua-multi.sendcloud.org'

    def __repr__(self):
        return '<MultiSender>'
