# coding: utf-8

from werkzeug.utils import cached_property
from pkg_resources import SetuptoolsVersion

from jupiter.integration.jpush import jpush
from core.models.consts import Platform
from core.models.user.account import Account
from core.models.user.tag import UserTag, collect_user_tags
from .binding import DeviceBinding
from .consts import jpush_splitter_sub


class PushController(object):
    """The controller of pusher service"""

    def __init__(self, user_id):
        if not Account.get(user_id):
            raise ValueError('invalid user id %s' % user_id)

        self.user_id = user_id

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @property
    def device_bindings(self):
        return DeviceBinding.get_multi_by_user(self.user.id_)

    @classmethod
    def hook_up(cls, user_id, device_id, device_platform, device_app_version):
        """用户激活（注销后登录或时机触发）、新建（初次登录）、覆盖（设备发生新用户登录）绑定关系"""
        assert isinstance(device_platform, Platform)
        assert isinstance(device_app_version, SetuptoolsVersion)

        current_user = Account.get(user_id)
        if not current_user:
            raise ValueError('invalid user id %s' % user_id)

        if device_platform not in [Platform.ios, Platform.android]:
            raise ValueError('unsupported platform %s' % device_platform)

        binding = DeviceBinding.get_by_device(device_id)
        if binding:
            # 更新设备装载APP的版本信息
            binding.update_app_version(device_app_version)

            # 如果设备曾进行过注册
            if binding.user_id == current_user.id_:
                # 如果已有绑定用户与当前请求用户一致，认定为*用户激活*(注销后又登录)
                # 1. 激活设备绑定关系
                binding.activate()
                # 2. 为所有用户的设备同步用户标签
                cls(binding.user_id).synchronize_tags()
            else:
                # 如果已有绑定用户与当前请求用户不一致，认定为*覆盖登录*
                cls.switch_device_user(binding, current_user)
        else:
            # 如果设备从未注册
            cls.register_user_device(
                current_user, device_id, device_platform, device_app_version)

    @classmethod
    def register_user_device(cls, user, device_id, device_platform, device_app_version):
        # 校验检查
        DeviceBinding.check_before_create(user, device_id, device_platform, device_app_version)

        # 获取用户最新标签
        app_version_tag = jpush_splitter_sub(str(device_app_version))
        user_tags = collect_user_tags(user.id_)
        all_tags = tuple(user_tags) + (app_version_tag,)

        # 极光端注册设备（1. 确保设备原有信息清空；2.注册新信息）
        jpush.logoff_device(device_id)
        jpush.register_device(device_id, user.id_, user.mobile, all_tags)

        # 本地注册设备
        DeviceBinding.create(user, device_id, device_platform, device_app_version, _validate=False)
        # 本地添加标签
        UserTag.align_tags_by_user(user, user_tags)

    @classmethod
    def switch_device_user(cls, binding, new_user):
        # 获取用户最新标签
        user_tags = collect_user_tags(new_user.id_)
        all_tags = tuple(user_tags) + (binding.underscored_app_version,)

        # 极光端切换设备用户（1. 确保设备原有信息清空；2.注册新信息）
        jpush.logoff_device(binding.device_id)
        jpush.register_device(binding.device_id, new_user.id_, new_user.mobile, all_tags)

        # 修改设备所有者为新用户
        binding.change_owner(new_user)
        # 本地为新用户添加标签
        UserTag.align_tags_by_user(new_user, user_tags)

    def synchronize_tags(self):
        """刷新远端本地的标签与标签分配中心一致[InstantTagging]"""
        latest_tags = collect_user_tags(self.user_id)
        existed_tags = [t.tag for t in UserTag.get_multi_by_user(self.user.id_)]

        if set(latest_tags) == set(existed_tags):
            return

        # 为用户多设备添加多标签
        for binding in self.device_bindings:
            jpush.clear_device_tags(binding.device_id)
            jpush.add_device_tags(binding.device_id, latest_tags)

        UserTag.align_tags_by_user(self.user, latest_tags)

    def sleep_device(self, device_id):
        """设备休眠(当用户退出登录时触发)"""
        binding = DeviceBinding.get_by_user_and_device(self.user.id_, device_id)
        if binding:
            binding.deactivate()

    @classmethod
    def delete_site_tag(cls, tag):
        """删除全站标签"""
        if tag not in UserTag.get_all_tags():
            raise ValueError('tag %s does not exist' % tag)

        # 请求极光接口
        jpush.remove_site_tag(tag)

        # 本地删除所有对应该标签的记录
        UserTag.clear_by_tag(tag)

    @classmethod
    def multicast(cls, base_kind, subdivision_kind=None, audience=None):
        """通知(Notification)的组播(广播)

        适用于系统性、面向全站（支持分组）、与用户个体有关的通知，大体分为两类：
        1. 通知载体子类型决定推送配置（面向人群、内容等），如全站发礼包后的组播推送由礼包类型控制。
        2. 通知类型决定推送配置（无子类型），如日常检查礼券到期情况向用户提醒。
        """
        from core.models.notification import NotificationKind
        from .group_record import GroupPushRecord

        assert isinstance(base_kind, NotificationKind)

        if not base_kind.allow_push:
            raise ValueError('push is unsupported by kind')

        if base_kind.is_unicast_push_only:
            raise ValueError('multi push is unsupported by kind')

        if subdivision_kind:
            assert isinstance(subdivision_kind, base_kind.subdivision_kind_cls)
            if not subdivision_kind.allow_push:
                raise ValueError('push is unsupported by subdivision_kind')
            if subdivision_kind.is_unicast_push_only:
                raise ValueError('multi push is unsupported by subdivision_kind')
            # 推送人群暂只由推送载体子类型指定
            pack = subdivision_kind.make_push_pack()
        else:
            # 推送人群暂只由参数audience指定
            pack = base_kind.make_push_pack(audience)

        # TODO: move to mq
        record = GroupPushRecord.create(base_kind, subdivision_kind)
        response = jpush.push(**pack.payload)
        record.mark_as_pushed(response.msg_id)

    @classmethod
    def broadcast(cls, bulletin):
        """公告(Bulletin)的广播

        适用于系统性、面向全站（支持分组）、与用户个体无关的通知
        """
        from core.models.site.bulletin import Bulletin
        from .universe_record import UniversePushRecord

        assert isinstance(bulletin, Bulletin)

        if UniversePushRecord.get(bulletin.id_):
            raise ValueError('the broadcast has been pushed once')

        # TODO: move to mq
        pack = bulletin.make_push_pack()
        record = UniversePushRecord.create(bulletin)
        response = jpush.push(**pack.payload)
        record.mark_as_pushed(response.msg_id)
