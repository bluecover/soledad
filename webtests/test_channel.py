# coding: utf-8

from __future__ import absolute_import

import time

from core.models.user.account import Account
from .framework import BaseTestCase


class ChannelTest(BaseTestCase):

    def test_channel_tracking(self):
        self.browser.visit(self.url_for('home.home'))
        self.browser.cookies.delete('channel')
        assert 'channel' not in self.browser.cookies.all()

        self.browser.visit(self.url_for('home.home', ch='west'))

        time.sleep(2)
        assert 'channel' in self.browser.cookies.all()
        assert self.browser.cookies.all()['channel'] == 'west'

    def test_channel_register(self):
        self.browser.visit(self.url_for('home.home', ch='west'))

        mobile, password = self.register_mobile()
        time.sleep(2)

        user = Account.get_by_alias(mobile)
        assert user.mobile == mobile
        assert user.channel.name == u'西方记者'
        assert user.channel.tag == u'west'
