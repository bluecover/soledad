# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.hoard import YixinAccount


class HoardAccountTest(BaseTestCase):

    local_user_info = ('foo@guihua.dev', 'foobar', 'Foo')
    remote_user_info = ('13800138000', '496c0f0e148d6573097d01a6578cca2a')
    alternative_user_info = ('18500185000', 'd3b07384d113edec49eaa6238ad5ff00')

    def setUp(self):
        super(HoardAccountTest, self).setUp()
        self.local_account = self.add_account(*self.local_user_info)

    def test_bind_once(self):
        remote_account = YixinAccount.get_by_local(self.local_account.id)
        assert remote_account is None

        YixinAccount.bind(self.local_account.id, *self.remote_user_info)
        remote_account = YixinAccount.get_by_local(self.local_account.id)
        assert remote_account is not None

        assert remote_account.account_id == self.local_account.id
        assert remote_account.p2p_account == self.remote_user_info[0]
        assert remote_account.p2p_token == self.remote_user_info[1]

    def test_bind_twice(self):
        remote_account = YixinAccount.get_by_local(self.local_account.id)
        assert remote_account is None

        YixinAccount.bind(self.local_account.id, *self.alternative_user_info)
        remote_account = YixinAccount.get_by_local(self.local_account.id)
        assert remote_account.p2p_account == self.alternative_user_info[0]
        assert remote_account.p2p_token == self.alternative_user_info[1]

        # the last bound information should be overrided
        YixinAccount.bind(self.local_account.id, *self.remote_user_info)
        remote_account = YixinAccount.get_by_local(self.local_account.id)
        assert remote_account.p2p_account == self.remote_user_info[0]
        assert remote_account.p2p_token == self.remote_user_info[1]
