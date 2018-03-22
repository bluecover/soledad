# coding: utf-8

from flask import jsonify, g, abort
from .blueprint import create_blueprint

from core.models.gift import LotteryGiftMgr, UserLottery
from core.models.welfare import FirewoodWorkflow


bp = create_blueprint('j.activity', __name__, url_prefix='/j/activity')
gift_dict = {}


@bp.before_request
def checkin():
    if not g.user:
        abort(401)
    g.firewood_flow = FirewoodWorkflow(g.user.id_)
    if not g.firewood_flow.account_uid:
        abort(401)


@bp.route('/do_lottery')
def do_lottery():
    user_id = g.user.id_

    # 检查是否有未发送的礼物
    if user_id in gift_dict:
        gift_id = gift_dict[user_id]
        gift_dict.pop(user_id)
        LotteryGiftMgr.send_gift_async(g.user.id_, gift_id)

    gift_id = LotteryGiftMgr.get_gift_id(user_id)

    # 礼物需要等请求后发送
    gift_dict[user_id] = gift_id

    user_lottery = UserLottery.get(user_id)
    remain_num = user_lottery.remain_num
    return jsonify(gift_id=gift_id,
                   remain_num=remain_num)


@bp.route('/get_lottery_num')
def get_lottery_num():
    user_id = g.user.id_
    user_lottery = UserLottery.get(user_id)
    return jsonify(remain_num=user_lottery.remain_num)


@bp.route('/get_gift')
def get_gift():
    user_id = g.user.id_
    if user_id in gift_dict:
        gift_id = gift_dict[user_id]
        gift_dict.pop(user_id)
        LotteryGiftMgr.send_gift_async(g.user.id_, gift_id)
        return jsonify(success=True)
    else:
        return jsonify(success=False)
