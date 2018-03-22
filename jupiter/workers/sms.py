# coding: utf-8

from __future__ import absolute_import
from jupiter.integration.mq import WorkerTaskError
from . import pool


@pool.async_worker('guihua_sms')
def sms_sender(sms_uuid):
    from core.models.sms import ShortMessage

    sms = ShortMessage.get(sms_uuid)
    result = sms.send()
    if not result:
        raise WorkerTaskError('sms', sms.receiver_mobile, sms.sms_args)
