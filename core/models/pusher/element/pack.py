# coding: utf-8

from flask import current_app
from jpush_client.client import jpush_thrift_module as jthrift

from core.models.consts import Platform
from .notice import Notice
from .audience import Audience
from .style import IosStyle, AndroidStyle


class Pack(object):
    """推送配置，包括推送对象、平台信息、平台样式等"""

    def __init__(self, audience, notice, platforms, platform_styles=None,
                 target_link=None, needs_following_up=False):
        assert isinstance(notice, Notice)
        assert isinstance(audience, Audience)

        #: 推送报文
        self.notice = notice
        #: 推送平台
        self.platforms = frozenset(platforms)
        #: 推送平台通知栏样式
        self.platform_styles = platform_styles or []
        #: 推送听众
        self.audience = audience
        #: 推送生产环境/开发环境
        self.to_production = not current_app.debug
        #: 推送报文要求的额外参数1 - 报文跳转链接
        self.target_link = target_link
        #: 推送报文要求的额外参数2 - 是否跟踪推送接收和点击情况
        self.needs_following_up = needs_following_up

    @property
    def payload(self):
        body = {}

        # 设置推送目标、内容、平台
        body.update(audience=self.audience.payload)
        body.update(notice=jthrift.JNotice(**self.notice.payload))
        body.update(platforms=[p.name for p in self.platforms])

        # 设置通知栏样式
        styles = {p.platform: p for p in self.platform_styles}
        ios_style = styles.get(Platform.ios, IosStyle()).payload
        android_style = styles.get(Platform.android, AndroidStyle()).payload
        body.update(notice_ios_style=jthrift.JIosPushStyle(**ios_style))
        body.update(notice_android_style=jthrift.JAndroidPushStyle(**android_style))

        # 设置推送环境
        body.update(to_production=self.to_production)

        # 设置推送报文额外参数
        notice_extras = {
            'needs_following_up': self.needs_following_up,
            'target_link': self.target_link
        }
        body.update(extras=jthrift.JExtras(**notice_extras))
        return body
