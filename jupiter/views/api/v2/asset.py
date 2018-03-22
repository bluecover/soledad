# coding: utf-8
from __future__ import absolute_import, unicode_literals

from flask import jsonify, json, request

from jupiter.views.api.decorators import require_oauth
from core.models.hoarder.asset import Asset
from core.models.hoarder.vendor import Vendor, Provider
from ..blueprint import create_blueprint_v2, conditional_for_v2
from .schema.asset import AssetResponseSchema

bp = create_blueprint_v2('assets', 'v2', __name__, url_prefix='/assets')


@bp.route('/sxb', methods=['GET'])
@require_oauth(['wallet_w'])
def sxb_asset():
    """绑定账户.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 200: 资产信息, :class:`.AssetResponseSchema`
    """
    schema = AssetResponseSchema(strict=True)
    assets = Asset.gets_by_user_id(request.oauth.user.id_)
    vendor = Vendor.get_by_name(Provider.sxb)
    asset_response = dict(uid=-1, yesterday_profit=0, hold_amount=0, hold_profit=0,
                          actual_annual_rate=0, rest_hold_amount=0, rest_redeem_amount=0,
                          residual_redemption_times=0)
    for asset in assets:
        if asset.product.vendor.id_ == vendor.id_:
            asset_response['uid'] = asset.id_
            asset_response['yesterday_profit'] += asset.yesterday_profit
            asset_response['hold_amount'] += asset.total_amount
            asset_response['hold_profit'] += asset.hold_profit
            asset_response['yesterday_profit'] += asset.yesterday_profit
            asset_response['rest_redeem_amount'] += asset.remaining_amount_today
            asset_response['residual_redemption_times'] += asset.residual_redemption_times
            if asset_response['rest_hold_amount'] == 0:
                asset_response[
                    'rest_hold_amount'] = asset.product.total_buy_amount - asset.total_amount
            else:
                asset_response['rest_hold_amount'] -= asset.total_amount
    data, errors = schema.dump(asset_response)
    conditional_for_v2(json.dumps(data))
    return jsonify(success=True, data=data, errors=errors)
