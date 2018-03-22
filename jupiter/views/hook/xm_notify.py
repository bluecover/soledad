# coding: utf-8

from decimal import Decimal

from flask import Blueprint, jsonify

from core.models.hoard.xinmi import XMOrder, XMAsset
from core.models.utils import round_half_up
from jupiter.ext import xinmi, seasurf as csrf
from xmlib.consts import OrderStatus, RedeemStatus

bp = Blueprint('notify', __name__, url_prefix='/notify')


@csrf.exempt
@bp.route('/status.htm', methods=['POST'])
@xinmi.incoming_hook()
def status(data):
    app_order_id = data.get('app_order_id')
    order_id = data.get('order_id')
    order_status = data.get('order_status')
    stat = OrderStatus(order_status)

    order = XMOrder.get_by_order_code(order_code=order_id)

    if order:
        order.status = XMOrder.MUTUAL_STATUS_MAP[stat]

    return jsonify(app_order_id=app_order_id, receive_status='01'), 200


@csrf.exempt
@bp.route('/redeemPay.htm', methods=['POST'])
@xinmi.incoming_hook()
def redeem_status(data):
    # app_order_id = data.get('app_order_id')
    order_id = data.get('order_id')
    redeem_status = data.get('redeem_status')

    stat = RedeemStatus(redeem_status)

    asset = XMAsset.get_by_order_code(order_code=order_id)

    if asset:
        asset.synchronize(XMAsset.MUTUAL_STATUS_MAP[stat],
                          asset.current_amount,
                          asset.current_interest,
                          asset.bank_account)

    return jsonify(error_code=0, error=u'success', receive_status='01'), 200


@csrf.exempt
@bp.route('/payStatus.htm', methods=['POST'])
@xinmi.incoming_hook()
def pay_status(data):
    app_order_id = data.get('app_order_id')
    order_id = data.get('order_id')
    order_status = data.get('order_status')
    stat = OrderStatus(order_status)

    order = XMOrder.get_by_order_code(order_code=order_id)

    if order:
        order.status = XMOrder.MUTUAL_STATUS_MAP[stat]

    return jsonify(app_order_id=app_order_id, receive_status='01'), 200


@csrf.exempt
@bp.route('/redeemConfirm.htm', methods=['POST'])
@xinmi.incoming_hook()
def redeem_confirm(data):
    order_id = data.get('app_order_id')
    app_redeem_id = data.get('app_redeem_id')
    redeem_amount = float(data.get('redeem_amount'))

    order = XMOrder.get_by_order_code(order_code=order_id)
    if not order:
        return jsonify(app_order_id=order_id, app_redeem_id=app_redeem_id,
                       confirm_status=0, remark=u'获取订单失败')

    local_redeem_amount = order.amount + order.amount * order.original_annual_rate / 100 / 365
    if round_half_up(local_redeem_amount, 3) != round_half_up(redeem_amount, 3):
        remark = (u'订单赎回金额错误, 订单ID: {0}, 本地计算: {1}, 远端传回: {2}').format(
            order.id_, local_redeem_amount, redeem_amount)
        return jsonify(app_order_id=order_id, app_redeem_id=app_redeem_id,
                       confirm_status=0, remark=remark)

    rate_bonus = order.actual_annual_rate - order.original_annual_rate
    if rate_bonus > Decimal('5.0'):
        remark = (u'订单加息超限, 订单ID: {0}, 加息: {1}').format(
            order.id_, rate_bonus)
        return jsonify(app_order_id=order_id, app_redeem_id=app_redeem_id,
                       confirm_status=0, remark=remark)

    add_amount = order.amount * float(rate_bonus) * order.profit_period.value / 100 / 365

    return jsonify(app_order_id=order_id, app_redeem_id=app_redeem_id,
                   redeem_amount=redeem_amount, add_amount=add_amount,
                   confirm_status=1), 200
