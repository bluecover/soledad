# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from decimal import Decimal

from wtforms.fields.core import DecimalField
from wtforms.validators import DataRequired, Optional


def transaction_mixin(cls):
    cls.order_amount = DecimalField(
        validators=[DataRequired(message=u'请填写订单金额')])
    cls.pay_amount = DecimalField(
        validators=[DataRequired(message=u'未提交支付金额')])
    cls.pocket_deduction_amount = DecimalField(
        validators=[Optional()],
        default=Decimal('0'))  # TODO: DataRequired but allow it be 0
    return cls
