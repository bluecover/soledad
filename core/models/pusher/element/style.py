# coding: utf-8

from core.models.consts import Platform


class PlatformDisplayStyle(object):
    pass


class AndroidStyle(PlatformDisplayStyle):
    """安卓推送平台定制化样式"""

    platform = Platform.android

    def __init__(self, builder_id=1):
        self.builder_id = builder_id

    @property
    def payload(self):
        return {'builder_id': self.builder_id}


class IosStyle(PlatformDisplayStyle):
    """IOS推送平台定制化样式"""

    platform = Platform.ios

    def __init__(self, sound=None, badge=1, content_available=True):
        self.sound = str(sound) if sound else None
        self.badge = int(badge)
        self.content_available = content_available

    @property
    def payload(self):
        return {
            'sound': self.sound,
            'badge': self.badge,
            'content_available': self.content_available
        }
