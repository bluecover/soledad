# coding: utf-8

from flask import jsonify, request

from core.models.hoard.manager import SavingsManager
from core.models.wallet.account import WalletAccount
from core.models.wallet.providers import zhongshan
from core.models.wallet import UserDashboard
from ..blueprint import create_blueprint_v2, conditional_for
from ..decorators import require_oauth
from .schema.mine import AssetProfile

bp = create_blueprint_v2('mine', 'v2', __name__, url_prefix='/mine')


@bp.route('/asset_profile', methods=['GET'])
@require_oauth(['savings_r'])
def asset_profile():
    """用户资产概况

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.AssetProfile`
    """
    savings_manager = SavingsManager(request.oauth.user.id_)
    hoard_total = savings_manager.total_invest_amount
    hoard_daily_profit = savings_manager.daily_profit
    hoard_yesterday_profit = savings_manager.yesterday_profit

    wallet_total = 0
    wallet_yesterday_profit = 0
    wallet_account = WalletAccount.get_by_local_account(request.oauth.user, zhongshan)
    if wallet_account:
        dashboard = UserDashboard.today(wallet_account)
        wallet_total = dashboard.balance
        wallet_yesterday_profit = dashboard.latest_profit_amount

    profile = {
        'total_amount': float(hoard_total) + float(wallet_total),
        'total_yesterday_profit': float(hoard_yesterday_profit) + float(wallet_yesterday_profit),
        'hoard_amount': hoard_total,
        'hoard_daily_profit': hoard_daily_profit,
        'hoard_yesterday_profit': hoard_yesterday_profit,
        'wallet_amount': wallet_total,
        'wallet_yesterday_profit': wallet_yesterday_profit
    }

    conditional_for([
        unicode(profile['total_amount']),
        unicode(profile['total_yesterday_profit']),
        unicode(profile['hoard_amount']),
        unicode(profile['hoard_daily_profit']),
        unicode(profile['hoard_yesterday_profit']),
        unicode(profile['wallet_amount']),
        unicode(profile['wallet_yesterday_profit'])
    ])

    schema = AssetProfile()
    return jsonify(success=True, data=schema.dump(profile).data)
