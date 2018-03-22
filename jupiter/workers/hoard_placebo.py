# coding: utf-8

from __future__ import absolute_import

import datetime

from flask import url_for
from yxpay.response import RemoteError

from jupiter.ext import yxpay
from core.models.utils import round_half_up
from core.models.profile.identity import Identity
from . import pool


YXPAY_ACQ_ID = '01'                   # web
YXPAY_ACCOUNT_FLAG = '0'              # 卡
YXPAY_PAYMENT_TYPE = '04'             # 单笔代付
YXPAY_PAYMENT_CHANNEL_TYPE = 'THIRD'  # 第三方
YXPAY_BUSINESS_TYPE = '04'            # 回款
YXPAY_INDENTITY_TYPE = '111'          # 身份证
YXPAY_DATETIME_FORMAT = '%Y%m%d%H%M%S'


class PlaceboOrderExitError(Exception):
    pass


@pool.async_worker('guihua_placebo_order_exiting')
def placebo_order_exiting(order_id):
    from core.models.hoard.placebo import PlaceboOrder

    order = PlaceboOrder.get(order_id)

    if order.status is PlaceboOrder.Status.running:
        order.transfer_status(PlaceboOrder.Status.exiting)
        response = pay_for_order(order)
        order.mark_as_exited(response)

    if order.status is PlaceboOrder.Status.exiting:
        response = track_for_order(order)
        order.mark_as_exited(response)


def pay_for_order(order):
    payment_time = datetime.datetime.now().strftime(YXPAY_DATETIME_FORMAT)
    payment_amount = round_half_up(order.calculate_profit_amount(), 2)
    identity = Identity.get(order.user_id)
    notify_url = url_for('savings.hook.yxpay_placebo_notify', _external=True)
    return yxpay.query.single_pay(
        YXPAY_ACQ_ID, order.biz_id, YXPAY_PAYMENT_TYPE, YXPAY_BUSINESS_TYPE,
        YXPAY_ACCOUNT_FLAG, payment_time, order.bankcard.bank.yxpay_id,
        payment_amount, YXPAY_INDENTITY_TYPE, identity.person_ricn,
        identity.person_name, order.bankcard.card_number,
        order.bankcard.province_id, order.bankcard.city_id,
        YXPAY_PAYMENT_CHANNEL_TYPE, notify_url)


def track_for_order(order):
    from core.models.hoard.placebo import YixinPaymentStatus

    sent_time = order.creation_time.strftime(YXPAY_DATETIME_FORMAT)
    try:
        response = yxpay.query.single_pay_query(order.biz_id, sent_time)
    except RemoteError as e:
        remote_status = YixinPaymentStatus(int(e.args[0]))
        if remote_status is YixinPaymentStatus.NOT_FOUND:
            return pay_for_order(order)
        raise PlaceboOrderExitError(e, 'order_id:%s' % order.id_)
    return response
