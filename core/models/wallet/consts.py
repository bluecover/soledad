# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from zslib.errors import BusinessError


SMS_BINDING_BANKCARD = (
    '本次验证码为 %s，正在好规划零钱包服务中绑定尾号为 '
    '{bankcard.tail_card_number} 的银行卡，如非本人操作请及时联系微信客服')
SMS_PURCHASE = (
    '本次验证码为 %s，正在将 {amount} 元存入好规划零钱包，如非本人操作请及时联'
    '系微信客服')
SMS_REDEEMING = (
    '本次验证码为 %s，正在从好规划零钱包取出 {amount} 元，如非本人操作请及时联'
    '系微信客服')

# 验证码失败提示
SMS_CODE_INCORECT_FOR_TRANSACTION = u'验证码错误，请您重新进行交易'
SMS_CODE_INCORECT_FOR_BINDING = u'验证码错误，请返回选择该银行卡重新绑定'

# See also: http://www.tuluu.com/guihua/solar/wikis/wallet#错误提示文案
# Schema: ``{kind: (description, is_unexpected)}``
ZSLIB_ERROR_PAIRS = {
    BusinessError.kinds.unknown: (
        '抱歉，当前服务遇到问题，请稍后重试或联系微信客服'
        ' ({error_code})', True),
    BusinessError.kinds.account_missing: (
        '您的账户尚未开通零钱包服务，请联系微信客服'
        ' ({error_code})', True),
    BusinessError.kinds.account_inactive: (
        '您的账户尚未开通零钱包服务，请联系微信客服'
        ' ({error_code})', True),
    BusinessError.kinds.sms_code_expired: (
        '验证码已过期，请申请重新发送', False),
    BusinessError.kinds.sms_code_incorrect: (
        '验证码错误，请确认后重试', False),
    BusinessError.kinds.invalid_person_ricn: (
        '申请开通零钱包购买服务遇到问题，请联系微信客服'
        ' ({error_code})', True),
    BusinessError.kinds.invalid_mobile_phone: (
        '申请开通零钱包购买服务遇到问题，请联系微信客服'
        ' ({error_code})', True),
    BusinessError.kinds.balance_exhausted: (
        '当前银行卡中金额不足，请修改金额或换卡重试', False),
    BusinessError.kinds.invalid_bankcard_number: (
        '您所输入的银行卡卡号无效，请确认后重试或联系微信客服', False),
    BusinessError.kinds.bankcard_owner_mismatched: (
        '当前用户个人信息与该银行卡持卡人信息不一致，'
        '请修改后重试或联系微信客服 ({error_code})', True),
    # BusinessError.kinds.bankcard_issuer_unsupported: (
    #     '零钱包服务暂不支持该银行，请使用其他银行卡重试', False),
    BusinessError.kinds.bankcard_type_unsupported: (
        '暂不支持当前银行卡类型，请修改后重试或联系微信客服', False),
    # BusinessError.kinds.bankcard_lost: (
    #     '该银行卡已挂失，请换卡重试或联系开卡银行', False),
    # BusinessError.kinds.bankcard_inactive: (
    #     '该银行卡暂未激活，请换卡重试或联系开卡银行', False),
    # BusinessError.kinds.bankcard_locked: (
    #     '该银行卡暂不可用，请换卡重试或联系开卡银行', False),
}
