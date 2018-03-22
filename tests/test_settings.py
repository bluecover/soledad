# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.settings.settings import (
    SETTINGS, Settings, xyz
)


class SettingsTest(BaseTestCase):

    def test_setttings(self):
        settings = Settings.get(SETTINGS.XYZ)
        settings.data.update(ips=['1.1.1.1'])
        assert settings.data.ips
        assert settings.settings.ips
        assert settings.data.ips == ['1.1.1.1']
        assert settings.settings.ips == ['1.1.1.1']

        assert xyz.settings.ips
        assert xyz.settings.ips == ['1.1.1.1']
