# coding: utf-8

from flask import url_for
from weakref import WeakValueDictionary

from core.models.base import EntityModel
from core.models.consts import Platform
from core.models.welfare.package.kind import PackageKind
from core.models.pusher import PushSupport
from core.models.pusher.element import (
    Pack, Notice, Audience, PlatformDisplayStyle, IosStyle, AndroidStyle)


class NotificationKind(EntityModel, PushSupport):
    """通知消息类型

    通知消息类型是通知系统的重要组成部分，在添加新的需求前，请仔细阅读以下说明：

    * 通知的单组播行为
        C1. 单播消息都将先生成notification记录以方便用户在通知中心查阅，后生成notification的推送记录
           （user_push_record）以跟踪推送的用户行为（收揽和浏览情况）。

        C2. 组播消息只生成组播推送记录(group_push_record)以记录组播行为。

    * 通知记录的显示条件
        当单播行为生成了notification记录后，用户并未可以在WEB和APP端都可以看到，类型中的display_scopes
        参数帮助设定了可见的平台范围。组播行为不会生成notification记录，无需指定display_scopes。

    * 通知创建及推送执行的触发条件
        T1. 用户行为触发，如购买订单成功后，进行单组播行为C1。

        T2. 系统定时触发
           2.1 如每日收集即将到期的礼券，进行单组播行为C1。
           2.2 如每日收集不活跃用户，进行单组播行为C2。

        T3. 系统脚本触发，如向指定群体发放礼包（并创建notification），进行单组播行为C2。

    * 通知的应用场景
        S1. 通知载体（如订单）无子类型区分(STRAIGHT)且只进行单播，如用户购买订单成功后系统向用户单播购买
           成功消息。单播推送的人群、内容等元素均可由通知载体生成（如Notification继承了PushSupport）。

        S2. 通知载体（如订单）无子类型区分(STRAIGHT)且只进行组播，如通知全部有11月到期订单的用户注意延迟
           到账。

        S3. 通知载体（如礼包）有子类型区分(SUBDEVIDED)且有单播+组播可能，如用户触发性获得特定优惠礼包构
           成单播场景，而运营活动向全部用户发放新年礼包构成组播场景。单播推送元素可由具体礼包生成（退化为
           S1），组播推送元素则需由子类型决定如礼包种类生成（如PackageKind继承了PushSupport）。
    """

    storage = WeakValueDictionary()

    def __init__(self, id_, title=None, content=None, is_once_only=True, icon_name=None,
                 template_name=None, app_target_link=None, web_target_link_config=None,
                 display_scopes=None, allow_push=True, is_unicast_push_only=True,
                 push_platforms=None, platform_styles=None, subdivision_kind_cls=None):

        id_ = str(id_)
        if id_ in self.storage:
            raise ValueError('id_ %s has been used' % id_)

        if not (content or template_name):
            # N1、N3的单播使用模板生成消息内容，N2组播使用参数content生成消息内容
            # N3组播由载体子类型生成消息内容
            raise ValueError('no content source provided')

        # 默认允许生成的通知记录可在全平台显示
        display_scopes = frozenset(display_scopes or [Platform.web, Platform.ios, Platform.android])

        # 消息允许推送(至少是允许单播)
        if allow_push:
            # 默认向全平台推送
            platforms = set(push_platforms or (Platform.ios, Platform.android))
            push_platforms = frozenset(platforms - set([Platform.web]))
            styles = set(platform_styles or (IosStyle(), AndroidStyle()))
            platform_styles = frozenset([s for s in styles if s.platform in push_platforms])
            assert all(isinstance(p, Platform) for p in push_platforms)
            assert all(isinstance(p, PlatformDisplayStyle) for p in platform_styles)

            if subdivision_kind_cls and is_unicast_push_only:
                raise ValueError('cast scope conflict with subdivision support')
        else:
            if is_unicast_push_only:
                raise ValueError('enable unicast push should enable allow_push switch firstly')

        self.id_ = id_
        #: 消息默认标题
        self.title = title
        #: 消息默认内容
        self.content = content
        #: 消息是否只可为指定用户创建一次
        self.is_once_only = is_once_only
        #: 消息通知的图标文件名
        self.icon_name = icon_name
        #: 消息通知的模板文件名
        self.template_name = template_name
        #: 消息点击后APP跳转页面
        self.app_target_link = app_target_link
        #: 消息点击后WEB跳转页面
        self.web_target_link_config = web_target_link_config
        #: 消息显示平台
        self.display_scopes = display_scopes
        #: 消息通知是否需要推送
        self._allow_push = allow_push
        #: 消息通知是否只支持单播(TODO: 用传播范围集合来表示支持范围)
        self._is_unicast_push_only = is_unicast_push_only
        #: 消息通知的推送平台，为空时不进行推送
        self._push_platforms = push_platforms
        #: 消息通知的推送平台样式等配置
        self.platform_styles = platform_styles
        #: 消息通知的子类型类
        self.subdivision_kind_cls = subdivision_kind_cls

        self.storage[id_] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(str(id_))

    @property
    def web_target_link(self):
        """推送跳转链接"""
        if self.web_target_link_config:
            return url_for(**self.web_target_link_config)

    @property
    def common_template_location(self):
        """单消息渲染模板"""
        if self.template_name:
            return 'notification/common_templates/%s.html' % self.template_name

    @property
    def popout_template_location(self):
        """多消息合并弹窗模板"""
        if self.template_name:
            return 'notification/popout_templates/%s.html' % self.template_name

    @property
    def allow_push(self):
        return self._allow_push

    @property
    def is_unicast_push_only(self):
        return self._is_unicast_push_only

    @property
    def push_platforms(self):
        return self._push_platforms

    def make_push_pack(self, audience):
        """创建组播通知，组播人群由调用方提供"""
        assert isinstance(audience, Audience)

        if self.allow_push:
            if self.is_unicast_push_only:
                raise ValueError('only work for multicast push')
        else:
            raise ValueError('push is forbidden')

        notice = Notice(self.content, title=self.title)
        return Pack(audience, notice, self.push_platforms, target_link=self.app_target_link)

    def can_display(self, user_agent, user=None):
        """消息是否在指定平台的通知中心里显示"""
        if user_agent.app_info:
            if user_agent.app_info.platform in ('iphone', 'ipad'):
                return Platform.ios in self.display_scopes
            if user_agent.app_info.platform == 'android':
                return Platform.android in self.display_scopes
        else:
            return Platform.web in self.display_scopes


welfare_gift_notification = NotificationKind(
    id_=1,
    is_once_only=False,
    icon_name='gift',
    template_name='welfare_gift',
    app_target_link='guihua://open/coupon',
    web_target_link_config=dict(endpoint='welfare.index', _anchor='coupon'),
    is_unicast_push_only=False,
    subdivision_kind_cls=PackageKind
)  # S3

spring_gift_reserved_notification = NotificationKind(
    id_=2,
    icon_name='gift',
    template_name='spring_gift_reserved',
    display_scopes=[Platform.web],
    web_target_link_config=dict(endpoint='welfare.index', _anchor='coupon')
)  # S1

spring_gift_obtained_notification = NotificationKind(
    id_=3,
    icon_name='gift',
    template_name='spring_gift_obtained',
    display_scopes=[Platform.web],
    web_target_link_config=dict(endpoint='savings.mine.index', _anchor='springfestival')
)  # S1

coupon_expiring_notification = NotificationKind(
    id_=4,
    icon_name='gift',
    template_name='coupon_expiring',
    app_target_link='guihua://open/coupon',
    web_target_link_config=dict(endpoint='welfare.index', _anchor='coupon'),
)  # S1

lazy_saver_notification = NotificationKind(
    id_=5,
    title=u'好规划理财',
    content=u'您可以享受收益率10%的新手产品，还有礼包可用，快来攒钱吧',
    is_unicast_push_only=False
)  # S2
