# coding:utf-8

from weakref import WeakValueDictionary

from core.models.base import EntityModel
from .consts import HIGH_PRIORITY, NORMAL_PRIORITY, SenderType


class MailKind(EntityModel):

    storage = WeakValueDictionary()

    def __init__(self, id_, subject, priority, sender_type, template):
        if id_ in self.storage:
            raise ValueError('id_ %s has been used' % id_)

        self.id_ = id_
        self.subject = subject
        self.priority = priority
        self.sender_type = sender_type
        self.template = template
        self.storage[self.id_] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(id_)


insurance_guide_mail = MailKind(
    id_=1,
    subject=u'您在好规划感兴趣的产品如下，建议使用电脑访问',
    priority=HIGH_PRIORITY,
    sender_type=SenderType.normal,
    template='email/email_tmpl.html'
)

feedback_mail = MailKind(
    id_=2,
    subject=u'好规划网回复了您的反馈',
    priority=HIGH_PRIORITY,
    sender_type=SenderType.normal,
    template='email/feedback.html'
)

reset_password_mail = MailKind(
    id_=3,
    subject=u'请重设您的好规划密码',
    priority=HIGH_PRIORITY,
    sender_type=SenderType.normal,
    template='email/reset_password.html'
)

reset_wechat_mail = MailKind(
    id_=4,
    subject=u'微信关注好规划网  享理财师贴身服务',
    priority=HIGH_PRIORITY,
    sender_type=SenderType.multi,
    template='email/wechat.html'
)

spring_interview_mail = MailKind(
    id_=5,
    subject=u'新年有奖用户访谈',
    priority=NORMAL_PRIORITY,
    sender_type=SenderType.multi,
    template='email/interview.html'
)
