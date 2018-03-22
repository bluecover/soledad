# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.plan.plan import Plan


class PlanTest(BaseTestCase):
    def test_add_plan(self):
        a = self.add_account()
        plan = Plan.add(a.id)
        self.assertTrue(plan)
        self.assertEqual(plan.user_id, a.id)

    def test_get_plan(self):
        a = self.add_account()
        plan = Plan.add(a.id)
        self.assertTrue(plan)
        self.assertEqual(plan.user_id, a.id)

        pid = plan.id
        plan = Plan.get(pid)

        self.assertTrue(plan)
        self.assertEqual(plan.id, pid)

    def test_get_plan_by_user(self):
        a = self.add_account()
        plan = Plan.add(a.id)
        self.assertTrue(plan)
        self.assertEqual(plan.user_id, a.id)

        pid = plan.id
        plan = Plan.get_by_user_id(a.id)

        self.assertTrue(plan)
        self.assertEqual(plan.id, pid)

    def test_plan_steps(self):
        a = self.add_account()
        plan = Plan.add(a.id)
        pid = plan.id
        self.assertEqual(plan.step, 1)
        plan.update_step(2)
        plan = Plan.get(pid)
        self.assertEqual(plan.step, 2)

    def test_plan_secret_data_with_big_data(self):
        a = self.add_account()
        plan = Plan.add(a.id)
        plan.data.update(key='value',
                         haha='this is a very long text',
                         content='100' * 1000,
                         int_data=100,
                         some_key='some_key',
                         some_chinese_key='你好',
                         some_photo='asd' * 1024)
        plan.data.update(some_dict=dict(key='value'),
                         some_list=[1, 2])
        self.assertFalse(plan.data.invalid)
        self.assertEqual(plan.data.key, 'value')
        self.assertEqual(plan.data.some_chinese_key, '你好')
        self.assertEqual(plan.data.some_photo, 'asd' * 1024)
        self.assertEqual(plan.data.some_dict.get('key'), 'value')
        self.assertTrue(1 in plan.data.some_list)
        self.assertTrue(2 in plan.data.some_list)
