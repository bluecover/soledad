# coding:utf-8

from flask import Blueprint, request, g, jsonify, url_for

from core.models.redeemcode.redeemcode import RedeemCode
from core.models.redeemcode.errors import (NotFoundError, RedeemCodeUsedError,
                                           RedemptionBeyondLimitPerUserError,
                                           RedemptionBeyondLimitPerCodeError,
                                           RedeemCodeIneffectiveError, RedeemCodeExpiredError)


bp = Blueprint('redeemcode', __name__, url_prefix='/j/redeemcode')


@bp.route('/code', methods=['GET', 'POST'])
def redeem():
    if request.method == 'POST':
        redeem_code = request.form['redeem_code'].upper()
        redeem_code = RedeemCode.get_by_code(redeem_code)
        if redeem_code:
            try:
                redeem_code.redeem(g.user)
                welfare_info = redeem_code.activity.reward_welfare_package_kind.welfare_summary
                anchor = None if welfare_info.firewood_info else 'coupon'
                welfare_info = {
                    'coupon_info': [vars(item) for item in welfare_info.coupon_info],
                    'firewood_info': [vars(item) for item in welfare_info.firewood_info]}
                welfare_detail = {'redirect_url': url_for('welfare.index', _anchor=anchor),
                                  'welfare_info': welfare_info}
                return jsonify(welfare_detail=welfare_detail)
            except (NotFoundError, RedeemCodeUsedError, RedeemCodeExpiredError,
                    RedeemCodeIneffectiveError, RedemptionBeyondLimitPerCodeError,
                    RedemptionBeyondLimitPerUserError, RedemptionBeyondLimitPerUserError) as e:
                message = unicode(e)
        else:
            message = u'您输入的兑换码不存在'
        return jsonify(error=message), 403
