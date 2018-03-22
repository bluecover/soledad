# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from wtforms import StringField
from wtforms.validators import DataRequired, Length, Optional

from jupiter.integration.wtforms import validators
from jupiter.integration.wtforms.fields import BankField, DivisionField
from core.models.bank import Partner
from core.models.hoard.zhiwang.utils import iter_banks as iter_banks_of_zw
from core.models.hoard.xinmi.utils import iter_banks as iter_banks_of_xm
from core.models.wallet.utils import iter_banks as iter_banks_of_zs


def bankcard_mixin(bank_partner):
    # TODO (tonyseek) very 不轻盈, 这个东西日后得换成移动 API 同款

    def decorator(cls):
        cls.card_number = StringField(
            validators=[DataRequired(message=u'请填写银行卡号'), validators.BankCardNumber()])
        # TODO (tonyseek) 表单里不检查银行的话, 应该在具体产品线下订单时检查
        cls.bank_id = BankField(
            validators=[DataRequired(message=u'请选择银行')], partner=bank_partner)
        cls.province_id = DivisionField(
            validators=[DataRequired(message=u'请选择银行卡开户省份')], level='province',
            label='银行卡开户省份')
        cls.city_id = DivisionField(
            validators=[DataRequired(message=u'请选择银行卡开户城市')], level='prefecture',
            label='银行卡开户城市')
        return bankcard_editing_mixin(cls)

    return decorator


def bankcard_editing_mixin(cls):
    cls.mobile_phone = StringField(
        validators=[DataRequired(message=u'请填写银行预留手机号'), validators.MobilePhone()])
    cls.bank_branch_name = StringField(
        validators=[Optional(), Length(4, 30, '支行名称应为4~30个中文汉字，请确认后重试')])
    return cls


def bankcard_to_dict(bankcard, partner, user_id, bound_checker=None):
    assert isinstance(partner, Partner)

    if partner in bankcard.bank.available_in:
        if bound_checker is None or bound_checker(bankcard):
            status = 'valid'
        else:
            status = 'unbound'
    else:
        status = 'invalid'

    if partner is Partner.zs:
        bank_limits = dict(iter_banks_of_zs(user_id))
    elif partner is Partner.zw:
        bank_limits = dict(iter_banks_of_zw(user_id))
    elif partner is Partner.xm:
        bank_limits = dict(iter_banks_of_xm(user_id))
    else:
        bank_limits = {}

    return {
        'card_id': bankcard.id_,
        'mobile_phone': bankcard.mobile_phone,
        'card_number': bankcard.card_number,
        'bank_name': bankcard.bank_name,
        'display_card_number': bankcard.display_card_number,
        'display_mobile_phone': bankcard.display_mobile_phone,
        'bank_id': bankcard.bank_id,
        'bank_branch_name': bankcard.local_bank_name,
        'city_id': bankcard.city_id,
        'icon_url': bankcard.bank.icon_url,
        'bank_limit': bank_limits.get(bankcard.bank),
        'local_name': ''.join(d.name for d in bankcard.prefecture.stack()),
        'tail_card_number': bankcard.tail_card_number,
        'province_id': bankcard.province_id,
        'status': status,
    }
