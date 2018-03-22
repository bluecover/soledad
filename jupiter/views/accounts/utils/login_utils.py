# -*- coding: utf-8 -*-

import collections

from core.models.user.account import Account
from core.models.user.consts import ACCOUNT_STATUS, ACCOUNT_REG_TYPE
from core.models import errors

from jupiter.views.accounts.utils.session import login_user


def default_err_msg():
    return '登录失败，请联系客服处理'


login_err_msg_dict = collections.defaultdict(default_err_msg, {
    errors.err_invalid_email: '账号或密码错误',
    errors.err_no_such_user: '账号或密码错误',
    errors.err_wrong_password: '账号或密码错误',
    errors.err_invalid_user_status: '您的账号尚未激活',
    errors.err_invalid_mail_user_status: '您的账号尚未激活，请您查看激活邮件',
    errors.err_invalid_mobile_user_status: '您输入的账号尚未完成注册，请重新注册并注意填写短信验证码',
})


def login(alias, password, remember):
    # TODO deprecate this
    user = Account.get_by_alias(alias)
    if not user:
        return errors.err_no_such_user

    if user.status == ACCOUNT_STATUS.NEED_VERIFY:
        if ACCOUNT_REG_TYPE.MOBILE in user.reg_type:
            return errors.err_invalid_mobile_user_status
        if ACCOUNT_REG_TYPE.EMAIL in user.reg_type:
            return errors.err_invalid_mail_user_status
        else:
            return errors.err_invalid_user_status

    if not user.is_normal_account():
        return
    if not user.verify_password(password):
        return errors.err_wrong_password

    user = login_user(user, remember)
    return errors.err_ok
