# -*- coding:utf-8 -*-

from datetime import timedelta

from .framework import BaseTestCase
from core.models.user.verify import Verify


class VerifyTest(BaseTestCase):

    def test_add_verify(self):
        user_id = str(1)
        code_type = str(4)
        verify_delta = timedelta(hours=48)
        v = Verify.add(user_id, code_type, verify_delta)
        self.assertTrue(v)
        self.assertEqual(user_id, v.user_id)
        self.assertEqual(code_type, v.type)

    def test_get_verify(self):
        user_id = str(1)
        code_type = str(4)
        verify_delta = timedelta(hours=48)
        v = Verify.add(user_id, code_type, verify_delta)
        vid = v.id
        oldv = v
        v = Verify.get(vid)
        self.assertTrue(v)
        self.assertEqual(v.id, oldv.id)
        self.assertEqual(v.user_id, oldv.user_id)
        self.assertEqual(v.type, oldv.type)
        self.assertEqual(v.verify_time, oldv.verify_time)

    def test_get_verify_by_code(self):
        user_id = str(1)
        code_type = str(4)
        verify_delta = timedelta(hours=48)
        v = Verify.add(user_id, code_type, verify_delta)
        verify_code = v.code
        oldv = v
        v = Verify.gets_by_code(verify_code)[0]
        self.assertTrue(v)
        self.assertEqual(v.id, oldv.id)
        self.assertEqual(v.user_id, oldv.user_id)
        self.assertEqual(v.type, oldv.type)
        self.assertEqual(v.verify_time, oldv.verify_time)

    def test_delete_verify(self):
        user_id = str(1)
        code_type = str(4)
        verify_delta = timedelta(hours=48)
        v = Verify.add(user_id, code_type, verify_delta)
        v.delete()
        v = v.get(v.id)
        self.assertFalse(v)

    def test_validate_verify(self):
        user_id = str(1)
        code_type = str(4)
        verify_delta = timedelta(hours=48)
        v = Verify.add(user_id, code_type, verify_delta)
        v = Verify.validate(user_id, v.code, code_type)
        assert v is not None
