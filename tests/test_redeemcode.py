# coding:utf-8

from datetime import datetime, timedelta
from pytest import raises
from .framework import BaseTestCase
from mock import patch

from core.models.group.group import Group
from core.models.welfare.package.package import Package
from core.models.redeemcode.redeemcode import RedeemCode
from core.models.redeemcode.errors import (RedeemCodeExpiredError, RedeemCodeUsedError,
                                           RedemptionBeyondLimitPerCodeError,
                                           RedemptionBeyondLimitPerUserError)


class RedeemCodeTestCase(BaseTestCase):

    def setUp(self):
        super(RedeemCodeTestCase, self).setUp()
        self.user1 = self.add_account(mobile='13800000001')
        self.user2 = self.add_account(mobile='13800000002')
        self.user3 = self.add_account(mobile='13800000003')
        self.user4 = self.add_account(mobile='13800000004')
        self.user5 = self.add_account(mobile='13800000005')

    def create_redeem_code(self, effective_time, expire_time):
        redeem_code = RedeemCode.create(1, 1, u'测试', 1, None, effective_time, expire_time)
        return redeem_code

    def test_new_redeemcode(self):
        test_date = datetime.now()
        redeem_code = self.create_redeem_code(test_date, test_date)

        assert redeem_code.id_ > 0
        assert len(redeem_code.code) == 8
        assert redeem_code.activity_id == '1'
        assert isinstance(redeem_code.effective_time, datetime)
        assert isinstance(redeem_code.expire_time, datetime)
        assert redeem_code.max_usage_limit_per_code == 1
        assert redeem_code.description.decode('utf-8') == u'测试'
        assert redeem_code.status is RedeemCode.Status.validated
        assert redeem_code.source is RedeemCode.Source.manager

    def test_get_by_code(self):
        test_date = datetime.now()
        redeem_code = self.create_redeem_code(test_date, test_date)
        get_redeem_code = RedeemCode.get_by_code(redeem_code.code)

        assert isinstance(get_redeem_code, RedeemCode)
        assert redeem_code.id_ == get_redeem_code.id_

    def test_get_by_id(self):
        test_date = datetime.now()
        redeem_code = self.create_redeem_code(test_date, test_date)
        get_redeem_code = RedeemCode.get(redeem_code.id_)

        assert isinstance(get_redeem_code, RedeemCode)
        assert redeem_code.id_ == get_redeem_code.id_

    def test_invalidate(self):
        test_date = datetime.now()
        redeem_code = self.create_redeem_code(test_date, test_date)
        assert redeem_code.status is RedeemCode.Status.validated
        redeem_code.invalidate()
        assert redeem_code.status is RedeemCode.Status.invalidated

    def test_get_by_activity(self):
        test_date = datetime.now()
        self.create_redeem_code(test_date, test_date)
        activity_id = '1'
        activity_list = RedeemCode.get_by_activity_id(activity_id)

        assert isinstance(activity_list, list)
        for activity in activity_list:
            assert isinstance(activity, RedeemCode)

    @patch.object(Package, 'unpack')
    @patch.object(Group, 'add_member')
    def test_redeem1(self, group_add_member, package_unpack):
        test_date = datetime.now()
        delta = test_date + timedelta(days=1)
        code = self.create_redeem_code(test_date, delta)

        with raises(RedeemCodeUsedError):
            code.redeem(self.user1)
            code.redeem(self.user1)

    @patch.object(Package, 'unpack')
    @patch.object(Group, 'add_member')
    def test_redeem2(self, group_add_member, package_unpack):
        test_date = datetime.now()
        delta = test_date + timedelta(days=1)
        code1 = self.create_redeem_code(test_date, delta)
        code2 = self.create_redeem_code(test_date, delta)
        code3 = self.create_redeem_code(test_date, delta)

        with raises(RedemptionBeyondLimitPerUserError):
            code1.redeem(self.user4)
            code2.redeem(self.user4)
            code3.redeem(self.user4)

    @patch.object(Package, 'unpack')
    @patch.object(Group, 'add_member')
    def test_redeem3(self, group_add_member, package_unpack):
        test_date = datetime.now()
        delta = test_date + timedelta(days=1)
        code = self.create_redeem_code(test_date, delta)

        with raises(RedemptionBeyondLimitPerCodeError):
            code.redeem(self.user1)
            code.redeem(self.user2)

    @patch.object(Package, 'unpack')
    @patch.object(Group, 'add_member')
    def test_redeem4(self, group_add_member, package_unpack):
        test_date = datetime.now()
        code_expired = self.create_redeem_code(test_date, test_date)

        with raises(RedeemCodeExpiredError):
            code_expired.redeem(self.user1)
