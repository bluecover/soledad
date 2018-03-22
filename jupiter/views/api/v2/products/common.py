# coding: utf-8

from core.models.bank import Partner
from core.models.welfare import Coupon
from .errors import BankCardNotExistedError, UnsupportedBankCardError, CouponOwnershipError
from jupiter.views.api.v1.savings import warning


def obtain_bankcard(bankcard_id, g):
    bankcard = g.bankcard_manager.get(bankcard_id)
    if not bankcard:
        warning('用户访问不存在的银行卡', bankcard_id=bankcard_id)
        raise BankCardNotExistedError()
    if Partner.xm not in bankcard.bank.available_in:
        raise UnsupportedBankCardError()
    return bankcard


def obtain_coupon(coupon_id, user):
    coupon = Coupon.get(coupon_id)
    if not coupon:
        return
    if not coupon.is_owner(user):
        raise CouponOwnershipError()
    return coupon
