# -*- coding: utf-8 -*-

from core.models.mail.mail import Mail
from core.models.mail.kind import insurance_guide_mail
from .framework import BaseTestCase


mail_template_args = {
    'ins_title': 'test',
    'product_url': 'http://www.guihua.com'
}


class MailTest(BaseTestCase):
    def test_send_mail(self):
        mail = Mail.create('test@guihua.com', insurance_guide_mail, **mail_template_args)
        self.assertEqual(mail.kind, insurance_guide_mail)
        self.assertEqual(mail.kind.subject, insurance_guide_mail.subject)

    def test_delete_mail(self):
        mail = Mail.create('test@guihua.com', insurance_guide_mail, **mail_template_args)
        mid = mail.id_
        self.assertEqual(mail.kind.subject, insurance_guide_mail.subject)
        mail.delete()
        mail = Mail.get(mid)
        self.assertFalse(mail)
