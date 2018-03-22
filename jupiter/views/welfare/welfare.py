# coding: utf-8

from operator import attrgetter

from flask import Blueprint, redirect, url_for, g, request
from flask_mako import render_template

from core.models.group import welfare_reminder_group
from core.models.welfare import CouponManager, FirewoodWorkflow, FirewoodPiling, FirewoodBurning
from core.models.promotion.festival.christmas import ChristmasGift
from core.models.profile.identity import has_real_identity
from core.models.notification import Notification
from core.models.notification.kind import welfare_gift_notification


bp = Blueprint('welfare', __name__, url_prefix='/welfare')


@bp.before_request
def initialize():
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.path))

    # 圣诞游戏获取红包的用户如果没有身份信息则跳转
    game_gift = ChristmasGift.get_by_mobile_phone(g.user.mobile)
    if not has_real_identity(g.user) and game_gift and game_gift.rank.award.firewood_wrapper:
        return redirect(url_for('profile.auth.supply', next=request.path))

    # 礼券管理
    g.coupon_manager = CouponManager(g.user.id_)
    # 为用户创建抵扣金账户
    g.firewood_flow = FirewoodWorkflow(g.user.id_)
    # 用户浏览任意福利相关页，则关闭福利提醒提示
    welfare_reminder_group.remove_member(g.user.id_)

    # 用户红包记录
    pileds = FirewoodPiling.get_multi_by_user(g.user.id_)
    burneds = FirewoodBurning.get_multi_by_user(g.user.id_)
    g.records = sorted(pileds + burneds, key=attrgetter('creation_time'), reverse=True)

    # 临时:用户访问该页面时默认将相关通知置为已读
    unread_notices = Notification.get_multi_unreads_by_user(g.user.id_)
    unread_notices = [n for n in unread_notices if n.kind is welfare_gift_notification]
    for un in unread_notices:
        un.mark_as_read()


@bp.route('/')
def index():
    return render_template('welfare/home.html')


@bp.route('/coins')
def record():
    return render_template('welfare/coins.html')
