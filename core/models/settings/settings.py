# -*- coding: utf-8 -*-

'''
全站或第三方合作开关配置，免得上线
'''

from solar.utils.storify import storify

from core.models.mixin.props import SecretPropsMixin


SETTINGS = storify(dict(
    XYZ='xyz_insure',
))


class Settings(SecretPropsMixin):

    def __init__(self, settting_name):
        self.settting_name = settting_name

    def get_db(self):
        return 'settings'

    def get_uuid(self):
        return 'settings_%s' % self.settting_name

    @classmethod
    def get(cls, settting_name):
        assert settting_name in SETTINGS.values()
        return cls(settting_name)

    @property
    def settings(self):
        return self.data


xyz = Settings.get(SETTINGS.XYZ)
