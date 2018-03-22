# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from datetime import datetime

from core.models.fund.fund import Fund
from core.models.fund.group import Group


class FundTest(BaseTestCase):
    def test_add_fund(self):
        code = u'123456'
        name = u'基金123456'
        fund = Fund.add(code, name)
        self.assertTrue(fund)
        self.assertEqual(fund.code, code)
        self.assertEqual(fund.name, name)

    def test_get_fund(self):
        code = u'654321'
        name = u'基金654321'
        fund = Fund.add(code, name)
        fcode = fund.code
        old_fund = fund
        fund = Fund.get(fcode)
        self.assertTrue(fund)
        self.assertEqual(fund.code, old_fund.code)
        self.assertEqual(fund.name, old_fund.name)


class GroupTest(BaseTestCase):
    def test_add_group(self):
        subject = u'组名'
        subtitle = u'子标题'
        subtitle2 = u'首页子标题'
        description = u'描述'
        create_time = datetime.now()
        update_time = datetime.now()
        reason = u'组合理由'
        highlight = u'组合亮点'
        reason_update = u'更新理由'
        related = u'相关说明'
        group = Group.add(subject,
                          subtitle,
                          subtitle2,
                          description,
                          create_time,
                          update_time,
                          reason,
                          highlight,
                          reason_update,
                          related)
        self.assertTrue(group)
        self.assertEqual(group.subject, subject)
        self.assertEqual(group.subtitle, subtitle)
        self.assertEqual(group.subtitle2, subtitle2)
        self.assertEqual(group.description, description)
        self.assertEqual(group.create_time.date(), create_time.date())
        self.assertEqual(group.update_time.date(), update_time.date())
        self.assertEqual(group.reason, reason)
        self.assertEqual(group.highlight, highlight)
        self.assertEqual(group.reason_update, reason_update)
        self.assertEqual(group.related, related)
