# -*- coding: utf-8 -*-

import datetime

from .framework import BaseTestCase

from core.models.hoard import HoardProfile


class HoardProfileTest(BaseTestCase):

    local_user_info = ('foo@guihua.dev', 'foobar', 'Foo')

    def setUp(self):
        super(HoardProfileTest, self).setUp()
        self.local_account = self.add_account(*self.local_user_info)

    def test_create_profile(self):
        profile = HoardProfile.get(self.local_account.id)
        assert profile is None

        profile = HoardProfile.add(self.local_account.id)
        assert profile.account_id == self.local_account.id

        # add again
        profile = HoardProfile.add(self.local_account.id)
        assert profile.account_id == self.local_account.id

        profile = HoardProfile.get(self.local_account.id)
        assert profile.account_id == self.local_account.id

    def test_profile_attrs(self):
        profile = HoardProfile.add(self.local_account.id)
        assert profile.plan_amount == 0

        profile.plan_amount = 10000

        profile = HoardProfile.get(self.local_account.id)
        assert profile.plan_amount == 10000
        assert profile.creation_time <= datetime.datetime.now()
