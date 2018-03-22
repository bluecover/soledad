# coding: utf-8

from __future__ import absolute_import

from flask import jsonify, json, request, abort
from yxpay.response import make_response
from yxpay.structures import SinglePaymentResult

from jupiter.ext import zhiwang, sentry
from core.models.hoard.placebo import PlaceboOrder, YixinPaymentStatus
from core.models.hoard.zhiwang.asset import ZhiwangAsset
from ._blueprint import create_blueprint


bp = create_blueprint('hook', __name__, url_prefix='/hook', for_anonymous=True)


@bp.route('/z/echo', methods=['POST'])
@zhiwang.incoming_hook()
def zhiwang_echo(data):
    return jsonify(success=True, data=data)


@bp.route('/z/asset/details', methods=['POST'])
@zhiwang.incoming_hook('asset_details')
def zhiwang_asset_details(data):
    asset = ZhiwangAsset.get_by_order_code(data.order_code)
    if not asset:
        return jsonify(success=False, error='asset_not_found'), 404
    asset.synchronize(data.status, data.current_amount,
                      data.current_interest, data.user_bank_account)
    return jsonify(success=True, data=data)


@bp.route('/yxpay/placebo/notify')
def yxpay_placebo_notify():
    if request.remote_addr not in ['111.207.203.195', '219.143.6.195']:
        abort(403)

    try:
        response = make_response(
            json.loads(request.form['msg']), SinglePaymentResult)
        status = YixinPaymentStatus(int(response.state))
    except (ValueError, TypeError):
        abort(400)

    order = PlaceboOrder.get_by_biz_id(response.biz_id)
    if not order:
        abort(404)

    if status is YixinPaymentStatus.SUCCESS:
        order.mark_as_exited(response)
    else:
        sentry.captureMessage('体验金订单回款失败', extra={
            'order_id': order.id_,
            'biz_id': response.biz_id,
            'status': status,
        })

    return '', 204
