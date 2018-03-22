# -*- coding: utf-8 -*-

from flask import url_for

from core.models import errors
from core.models.errors import (
    PasswordValidationError, MismatchedError,
    FormatError, AccountAliasValidationError, AccountInactiveError,
    AccountNotFoundError, UnsupportedAliasError, InsecureEmailError)
from core.models.mail.kind import reset_password_mail
from core.models.mail.mail import Mail
from core.models.user.account import Account
from core.models.user.alias import get_reg_type_from_alias
from core.models.user.verify import Verify
from core.models.user.consts import (ACCOUNT_STATUS, ACCOUNT_REG_TYPE, VERIFY_CODE_TYPE)
from core.models.user.change_password import change_password
from core.models.utils.validator import validate_email, validate_phone, validate_password


INSECURE_EMAIL_DOMAINS = (
    '163.com',
    '126.com',
    '188.com',
    'yeah.net',
)


def validate_reset_password_asker(alias):
    if not alias:
        raise AccountAliasValidationError()

    reg_type = get_reg_type_from_alias(alias)
    if reg_type == ACCOUNT_REG_TYPE.EMAIL:
        if validate_email(alias) != errors.err_ok:
            raise UnsupportedAliasError()
        if alias.strip().endswith(INSECURE_EMAIL_DOMAINS):
            raise InsecureEmailError()

    elif reg_type == ACCOUNT_REG_TYPE.MOBILE:
        if validate_phone(alias) != errors.err_ok:
            raise UnsupportedAliasError()
    else:
        raise UnsupportedAliasError()

    user = Account.get_by_alias(alias)
    if not user:
        raise AccountNotFoundError()

    if user.status != ACCOUNT_STATUS.NORMAL:
        raise AccountInactiveError()

    return reg_type


def send_reset_password_mail(user):
    if user.email.strip().endswith(INSECURE_EMAIL_DOMAINS):
        raise InsecureEmailError()

    v = Verify.add(user.id, VERIFY_CODE_TYPE.FORGOT_PASSWORD_EMAIL)
    mail_template_args = {
        'name': user.name,
        'uid': user.id,
        'url': url_for(
            'accounts.password.reset_for_mail_user', user_id=user.id_,
            code=v.code, _external=True, _scheme='https')
    }
    mail = Mail.create(user.email, reset_password_mail, **mail_template_args)
    mail.send()


def reset_password(user, new_password, confirmed_password, old_password=None):
    # 账号设置里重置密码，需验证原密码正确性
    # 找回密码时重置密码，需预先验证手机号的真实性
    if old_password is not None:
        if not user.verify_password(old_password):
            raise PasswordValidationError

    if not new_password:
        raise PasswordValidationError
    if new_password != confirmed_password:
        raise MismatchedError
    if validate_password(new_password) != errors.err_ok:
        raise FormatError

    change_password(user.id_, new_password)
    user.clear_session()
