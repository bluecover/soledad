# coding:utf-8

from core.models.mail.kind import MailKind
from core.models.mail.consts import HIGH_PRIORITY, SenderType
from .framework import BaseTestCase


class MailKindTest(BaseTestCase):
    def setUp(self):
        super(MailKindTest, self).setUp()

        self.id_ = 0
        self.subject = u'测试mail_kind'
        self.priority = HIGH_PRIORITY
        self.template = 'email/email_tmpl.html'

        self.test_mail_kind = MailKind(
            id_=self.id_,
            subject=self.subject,
            priority=self.priority,
            sender_type=SenderType.normal,
            template='email/email_tmpl.html'
        )

    def test_mail_kind(self):
        test_mail_kind = MailKind.get(0)
        assert isinstance(test_mail_kind, MailKind)
        assert test_mail_kind is self.test_mail_kind
        assert test_mail_kind.id_ == self.id_
        assert test_mail_kind.priority == self.priority
        assert test_mail_kind.template == self.template
