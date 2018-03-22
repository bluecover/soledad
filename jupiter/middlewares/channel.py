# coding: utf-8

"""
    商务合作渠道
    ~~~~~~~~~~~~

    新用户从商务合作渠道注册时，记录下渠道标识。
    之后该用户产生的任何交易，予以渠道方分成。
"""

from __future__ import absolute_import

import datetime

from flask import Blueprint, request, after_this_request, g

from core.models.user.signals import user_register_completed
from core.models.utils.switch import app_download_banner_switch
from libs.logger.rsyslog import rsyslog


bp = Blueprint('middlewares.channel', __name__)


@bp.before_app_request
def track_for_channel():
    if not request.endpoint or request.endpoint.startswith('api'):
        return

    tag = request.args.get('ch', type=bytes)   # ascii only

    if not tag or len(tag) > 21:
        has_channel = 'channel' in request.cookies
    else:
        @after_this_request
        def set_cookie(response):
            expires = datetime.datetime.now() + datetime.timedelta(days=365)
            response.set_cookie(
                key='channel', value=tag.decode('ascii'), httponly=True,
                expires=expires)
            return response
        has_channel = True

    # banner 显示的条件
    g.show_app_download_banner = all([
        # 开关开启
        app_download_banner_switch.is_enabled,

        # 不是来自上午合作渠道的未登录用户
        not (has_channel and not g.user),

        # 不是好规划和她理财的 App
        not (request.user_agent.is_guihua_app or request.user_agent.is_talicai_app),

        # 仅限移动端
        (request.user_agent.is_ios or request.user_agent.is_android),
    ])


@user_register_completed.connect
def assign_channel(user):
    if not request:
        return
    tag = request.cookies.get('channel', type=bytes)
    rsyslog.send('%s\t%s' % (user.id_, tag), tag='bd_channel')
    if tag:
        user.assign_channel_via_tag(tag)
