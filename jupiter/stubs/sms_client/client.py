# coding:utf-8

from __future__ import absolute_import

from jupiter.integration.bearychat import BearyChat


class SMSClient(object):

    bearychat = BearyChat('staging')

    def __repr__(self):
        if self.bearychat.configured:
            return '<BearyChatSMSClient>'
        return '<FakeSMSClient>'

    @classmethod
    def send(cls, phones, text, tag, operator):
        if isinstance(phones, basestring):
            phones = [phones]

        for phone in phones:
            line = u'%s\t%s\t%s\t%s' % (phone, text, tag, operator)
            print line.encode('utf-8')
            if cls.bearychat.configured:
                cls.bearychat.say(line)
        return True

    @classmethod
    def asend(cls, phones, text, tag, operator):
        SMSClient.send(phones, text, tag, operator)
