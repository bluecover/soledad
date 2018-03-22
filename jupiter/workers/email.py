# coding: utf-8

from __future__ import absolute_import

from envcfg.json.solar import DEBUG

from jupiter.integration.mq import WorkerTaskError
from . import pool


@pool.async_worker('guihua_email')
def email_sender(mail_id):
    from core.models.mail.mail import Mail
    from core.models.mail.sender import get_sender_pool

    mail = Mail.get(mail_id)
    sender_pool = get_sender_pool()
    sender = sender_pool.get_sender(mail.kind.sender_type)
    r = False
    if not DEBUG:
        r = sender.send_mail(mail.kind.subject, mail.mail_body, mail.receiver,
                             mail.sender_name, priority=mail.kind.priority)
    if not r:
        raise WorkerTaskError('email', mail.receiver, mail.sender_name)
