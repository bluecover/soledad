# coding: utf-8

from __future__ import unicode_literals

from enum import Enum


class ScopeEnum(Enum):
    """The basic class for scope items."""

    def __new__(cls, name, label, description=''):
        instance = object.__new__(cls)
        instance._value_ = name
        instance.label = label
        instance.description = description
        return instance


class OAuthScope(ScopeEnum):
    basic = ('basic', '基本信息', '读取您的用户 ID')
    user_info = ('user_info', '用户信息',
                 '替您绑定手机号、实名身份信息或银行卡，查看您可用的优惠券')
    savings_r = ('savings_r', '攒钱助手', '读取您的攒钱助手使用状况')
    savings_w = ('savings_w', '攒钱助手', '在攒钱助手攒钱')
    wallet_r = ('wallet_r', '零钱包', '读取您的零钱包使用状况')
    wallet_w = ('wallet_w', '零钱包', '在零钱包存钱')


class InvisibleScope(ScopeEnum):
    read_password = ('read_password', '', '读取或修改您的密码')
