# -*- coding: utf-8 -*-
from decimal import Decimal
from libs.cache import static_mc
from core.models.hoarder.signal import hoarder_order_succeeded
from .signals import yrd_order_confirmed, zw_order_succeeded, xm_order_succeeded

MC_SAVINGS_AMOUNT = 'hoard:savings:amount'
MC_SAVINGS_USERS = 'hoard:savings:users'
MC_SAVINGS_NEW_COEMR_PRODUCT = 'hoard:savings:new_comer_product'


def set_savings_amount(amount):
    static_mc.incrby(MC_SAVINGS_AMOUNT, int(amount))


def set_savings_new_comer_threshold(amount):
    static_mc.incrby(MC_SAVINGS_NEW_COEMR_PRODUCT, int(amount))


def get_savings_new_comer_product_threshold():
    return static_mc.get(MC_SAVINGS_NEW_COEMR_PRODUCT) or 0


def get_savings_amount():
    return Decimal(static_mc.get(MC_SAVINGS_AMOUNT) or 0)


def add_savings_users():
    static_mc.incrby(MC_SAVINGS_USERS, 1)


def get_savings_users():
    return static_mc.get(MC_SAVINGS_USERS) or 0


@yrd_order_confirmed.connect
def on_order_confirmed(sender):
    set_savings_amount(int(sender.order_amount))


@hoarder_order_succeeded.connect
@xm_order_succeeded.connect
@zw_order_succeeded.connect
def on_order_succeeded(sender):
    set_savings_amount(int(sender.amount))
