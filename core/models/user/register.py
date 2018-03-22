# -*- coding: utf-8 -*-

from core.models import errors
from core.models.utils import randbytes, pwd_hash
from core.models.user.account import Account
from core.models.user.consts import ACCOUNT_STATUS, ACCOUNT_REG_TYPE
from core.models.user.change_password import change_password
from core.models.sms import ShortMessage
from core.models.sms.kind import register_sms
from core.models.user.signals import user_register_completed


def _register_user(alias, password, reg_type, status):
    user = Account.get_by_alias(alias)
    salt = randbytes(4)
    passwd_hash = pwd_hash(salt, password)

    if user and user.need_verify():
        user.change_passwd_hash(salt, passwd_hash)
        return Account.get_by_alias(alias)
    elif user:
        return

    return Account.add(alias, passwd_hash, salt,
                       generate_nickname(alias, reg_type),
                       reg_type, status=status)


def register_without_confirm(alias, password, reg_type):
    return _register_user(alias, password, reg_type,
                          status=ACCOUNT_STATUS.NORMAL)


def register_with_confirm(alias, password, reg_type):
    user = _register_user(alias, password, reg_type,
                          status=ACCOUNT_STATUS.NEED_VERIFY)
    if not user:
        return

    if reg_type == ACCOUNT_REG_TYPE.MOBILE:
        sms = ShortMessage.create(alias, register_sms, user_id=user.id_)
        sms.send()
    else:
        return
    return user


def confirm_register(uid):
    user = Account.get(uid)
    if user and user.status != ACCOUNT_STATUS.NEED_VERIFY:
        if ACCOUNT_REG_TYPE.MOBILE in user.reg_type:
            return errors.err_invalid_mobile_user_status
        return errors.err_invalid_user_status
    user.update_status(ACCOUNT_STATUS.NORMAL)
    return errors.err_ok


def generate_nickname(alias, reg_type):
    if reg_type == ACCOUNT_REG_TYPE.EMAIL:
        return alias.split('@')[0]
    elif reg_type == ACCOUNT_REG_TYPE.MOBILE:
        return alias[:3] + '*' * 4 + alias[7:]
    raise ValueError('unknown reg_type')


def initial_new_user(uid, password):
    user = Account.get(uid)
    change_password(user.id_, password)
    user_register_completed.send(user)
    return user
