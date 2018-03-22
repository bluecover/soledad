# -*- coding: utf-8 -*-
from libs.cache import mc

from core.models.errors import BindError
from core.models.user.account import Account
from core.models.user.alias import AliasException
from core.models.sms import ShortMessage
from core.models.sms.kind import mobile_bind_sms
from core.models.user.consts import ACCOUNT_STATUS, ACCOUNT_REG_TYPE, VERIFY_CODE_TYPE
from core.models.user.verify import Verify, VerifyCodeException

MC_BIND_MOBILE_BY_USER = 'account:bind:mobile:by:%s'


def request_bind(uid, mobile, is_send_sms=True):
    mc.set(MC_BIND_MOBILE_BY_USER % uid, mobile)
    if is_send_sms:
        sms = ShortMessage.create(mobile, mobile_bind_sms, user_id=uid)
        sms.send()


def verify_bind(user_id, code):
    try:
        v = Verify.validate(user_id, code, VERIFY_CODE_TYPE.BIND_MOBILE)
        v.delete()
    except VerifyCodeException as e:
        raise BindError(unicode(e))


def confirm_bind(uid, mobile):
    cached_mobile = mc.get(MC_BIND_MOBILE_BY_USER % uid)
    if mobile != cached_mobile:
        raise BindError(u'申请验证码与最终提交时的手机号不一致')
    mc.delete(MC_BIND_MOBILE_BY_USER % uid)
    return _confirm_bind(uid, mobile)


def confirm_bind_without_check(uid, mobile):
    return _confirm_bind(uid, mobile)


def _confirm_bind(uid, mobile):
    user = Account.get_by_alias(mobile)
    # handle the unverified mobile account firstly
    if user:
        if user.need_verify():
            o_uid = user.id
            user.update_status(ACCOUNT_STATUS.FAILED)
            user = Account.get(o_uid)
            is_alias_removed = user.remove_alias(
                ACCOUNT_REG_TYPE.MOBILE, mobile)
            if not is_alias_removed:
                raise BindError(u'手机号绑定失败，请联系客服处理')

    # handle current user secondly
    user = Account.get(uid)
    try:
        user.add_alias(mobile)
    except AliasException:
        raise BindError(u'手机号绑定失败，请联系客服处理')
    return user
