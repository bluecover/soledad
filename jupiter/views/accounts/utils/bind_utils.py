# -*- coding: utf-8 -*-
from flask import g

from libs.logger.rsyslog import rsyslog

from core.models import errors
from core.models.errors import BindError
from core.models.user.account import Account

from core.models.utils.validator import validate_phone
from core.models.user.bind import request_bind


def pre_bind(mobile, is_send_sms=True):
    user = Account.get_by_alias(mobile)

    if validate_phone(mobile) != errors.err_ok:
        raise BindError(u'非法的手机号')

    if user and user.is_normal_account():
        raise BindError(u'手机号已被使用')

    request_bind(g.user.id, mobile, is_send_sms)
    return True


def log_binding(uid, request, mobile):
    dcm = request.args.get('dcm', request.cookies.get('dcm', '0'))
    dcs = request.args.get('dcs', request.cookies.get('dcs', '0'))
    referer = request.cookies.get('next', request.environ.get('HTTP_REFERER'))
    ip = request.remote_addr
    bid = request.bid

    msg = '\t'.join([uid, dcm, dcs, str(referer), ip, mobile, bid])
    rsyslog.send(msg, tag='mobile_binding_success')
