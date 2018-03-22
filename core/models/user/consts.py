# coding: utf-8

from solar.utils.storify import storify

ACCOUNT_STATUS = storify(dict(
    NEED_VERIFY='0',
    NORMAL='1',
    BANNED='2',
    FAILED='3',
))

ACCOUNT_REG_TYPE = storify(dict(
    EMAIL='0',
    MOBILE='1',
    WEIXIN_OPENID='2',
    FIREWOOD_ID='3',  # 新增抵扣金账户ID
))

ACCOUNT_GENDER = storify(dict(
    UNKNOWN='0',
    FEMALE='1',
    MALE='2',
))

VERIFY_CODE_TYPE = storify(dict(
    REG='1',
    FORGOT_PASSWORD_EMAIL='2',
    REG_MOBILE='3',
    FORGOT_PASSWORD_MOBILE='4',
    CHILD_INSURE='5',
    BIND_MOBILE='6',
    REBATE_WITHDRAW='7',
    CHANGE_MOBILE_VERIFY_OLD='8',
    CHANGE_MOBILE_SET_NEW='9',
))


VERIFY_STATUS = storify(dict(
    NEED_VERIFY='0',
    VERIFIED='1',
))

VERIFY_VALIDATE_TIME = 2  # days
