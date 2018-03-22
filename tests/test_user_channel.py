# coding: utf-8

from pytest import raises

from core.models.user.account import Account
from core.models.user.channel import ChannelExistedError
from .framework import BaseTestCase


class UserChannelTest(BaseTestCase):

    def setUp(self):
        super(UserChannelTest, self).setUp()
        self.user = self.add_account('foo@guihua.dev', 'foobar', 'Foo')
        self.channel = self.user.channel_class.add(u'西方记者', 'west')

    def test_assign_blackhole(self):
        assert self.user.channel is None
        self.user.assign_channel_via_tag('nothing')
        assert self.user.channel is None

        user = Account.get(self.user.id_)
        assert user.channel is None

    def test_assign_channel(self):
        assert self.user.channel is None
        self.user.assign_channel_via_tag('west')
        assert self.user.channel == self.channel

        user = Account.get(self.user.id_)
        assert user.channel == self.channel

    def test_assign_twice(self):
        self.user.channel_class.add(u'香港记者', 'hk')
        self.user.assign_channel_via_tag('west')
        with raises(ChannelExistedError):
            self.user.assign_channel_via_tag('hk')

    def test_channel_stats(self):
        channel_west = self.channel
        channel_hk = self.user.channel_class.add(u'香港记者', 'hk')

        user_foo = self.user
        user_bar = self.add_account('bar@guihua.dev', 'barbaz', 'Bar')
        user_baz = self.add_account('baz@guihua.dev', 'bazfoo', 'Baz')

        user_foo.assign_channel_via_tag('west')
        user_bar.assign_channel_via_tag('west')
        user_baz.assign_channel_via_tag('hk')

        assert Account.count_by_channel(channel_west) == 2
        assert Account.count_by_channel(channel_hk) == 1

        assert Account.get_multi_by_channel(channel_west) == [user_foo, user_bar]
        assert Account.get_multi_by_channel(channel_hk) == [user_baz]

        assert Account.get_multi_by_channel(channel_west, 0, 1) == [user_foo]
