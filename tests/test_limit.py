# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.utils.limit import Limit


class LimitTest(BaseTestCase):
    def test_limit_touch(self):
        l = Limit.get('test')
        self.assertEqual(l.num, 0)
        l.touch()
        self.assertEqual(l.num, 1)

    def test_limit(self):
        l = Limit.get('test', limit=5)
        for i in range(6):
            l.touch()
        self.assertTrue(l.is_limited())
