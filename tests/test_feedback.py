# -*- coding:utf-8 -*-

from .framework import BaseTestCase

from core.models.feedback.feedback import Feedback


class FeedbackTest(BaseTestCase):
    def test_add_feedback(self):
        contact = '1234@qq.com'
        content = 'content'
        feedback = Feedback.add(contact, content)
        self.assertTrue(feedback)
        self.assertEqual(feedback.contact, contact)
        self.assertEqual(feedback.content, content)

    def test_get_feedback(self):
        contact = '1234@qq.com'
        content = 'content'
        feedback = Feedback.add(contact, content)
        fid = feedback.id
        old_feedback = feedback
        feedback = Feedback.get(fid)
        self.assertTrue(feedback)
        self.assertEqual(feedback.id, old_feedback.id)
        self.assertEqual(feedback.contact, old_feedback.contact)
        self.assertEqual(feedback.content, old_feedback.content)
