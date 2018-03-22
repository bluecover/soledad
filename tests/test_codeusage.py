# coding:utf-8

from datetime import datetime, timedelta

from core.models.redeemcode.usage import RedeemCodeUsage
from .framework import BaseTestCase


class RedeemCodeUsageTestCase(BaseTestCase):

    def setUp(self):
        super(RedeemCodeUsageTestCase, self).setUp()
        self.user = self.add_account(mobile='13800000001')

    def create_redeem_code(self):
        from core.models.redeemcode.redeemcode import RedeemCode

        effective_time = datetime.now()
        expire_time = effective_time + timedelta(days=1)
        redeem_code = RedeemCode.create(1, 1, u'测试', 1, None, effective_time, expire_time)
        return redeem_code

    def test_add_redeem_code_usage(self):
        redeem_code = self.create_redeem_code()
        redeem_code_usage = RedeemCodeUsage.add(redeem_code, self.user)

        assert redeem_code_usage.id_ > 0
        assert redeem_code_usage.code_id == redeem_code.id_
        assert redeem_code_usage.user_id == self.user.id_
        assert isinstance(redeem_code_usage.consumed_time, datetime)

    def test_get(self):
        redeem_code = self.create_redeem_code()
        redeem_code_usage = RedeemCodeUsage.add(redeem_code, self.user)
        get_code_usage = RedeemCodeUsage.get(redeem_code_usage.id_)

        assert isinstance(get_code_usage, RedeemCodeUsage)
        assert redeem_code_usage.id_ == get_code_usage.id_

    def test_get_by_code(self):
        redeem_code = self.create_redeem_code()
        redeem_code_usage = RedeemCodeUsage.add(redeem_code, self.user)
        get_usage_by_code = RedeemCodeUsage.get_multi_by_redeem_code(redeem_code_usage.code_id)

        assert isinstance(get_usage_by_code, list)
        if get_usage_by_code:
            redeem_code_usage_get_list = [item.id_ for item in get_usage_by_code if item]
            assert redeem_code_usage.id_ in redeem_code_usage_get_list

    def test_get_by_user(self):
        redeem_code = self.create_redeem_code()
        redeem_code_usage = RedeemCodeUsage.add(redeem_code, self.user)
        get_usage_by_code = RedeemCodeUsage.get_multi_by_user(redeem_code_usage.user_id)

        assert isinstance(get_usage_by_code, list)
        if get_usage_by_code:
            redeem_code_usage_get_list = [item.id_ for item in get_usage_by_code if item]
            assert redeem_code_usage.id_ in redeem_code_usage_get_list

    def test_get_by_user_and_activity(self):
        redeem_code = self.create_redeem_code()
        redeem_code_usage = RedeemCodeUsage.add(redeem_code, self.user)
        get_usage_by_user = RedeemCodeUsage.get_multi_by_user_and_activity(
            redeem_code_usage.user_id, 1)

        assert isinstance(get_usage_by_user, list)
        if get_usage_by_user:
            redeem_code_usage_get_list = [item.id_ for item in get_usage_by_user if item]
            assert redeem_code_usage.id_ in redeem_code_usage_get_list

    def test_get_by_redeem_code_and_user(self):
        redeem_code = self.create_redeem_code()
        redeem_code_usage = RedeemCodeUsage.add(redeem_code, self.user)
        get_usage_by_code_user = RedeemCodeUsage.get_by_code_and_user(redeem_code_usage.code_id,
                                                                      redeem_code_usage.user_id)

        assert get_usage_by_code_user.code_id == redeem_code.id_
        assert get_usage_by_code_user.user_id == self.user.id_
