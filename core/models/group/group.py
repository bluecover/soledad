# coding: utf-8

from libs.cache import mc


class Group(object):

    base_key = 'group:%s'
    storage = set()

    def __init__(self, name):
        self.name = self.base_key % name
        if self.name in self.storage:
            raise ValueError('name %r has been used' % name)

        self.storage.add(self.name)

    def is_member(self, user_id):
        return mc.sismember(self.name, user_id)

    def add_member(self, user_id):
        mc.sadd(self.name, user_id)

    def remove_member(self, user_id):
        mc.srem(self.name, user_id)


welfare_reminder_group = Group('welfare:reminder')
invitation_reminder_group = Group('invitation:inviter')
