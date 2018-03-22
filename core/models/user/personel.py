# -*- coding: utf-8 -*-

from datetime import datetime

from weakref import WeakValueDictionary
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.types import date_type
from .account import Account


class PersonelGroup(PropsMixin):
    storage = WeakValueDictionary()

    # the users dict stored
    users = PropsItem('users', default={}, secret=True)
    update_time = PropsItem('update_time', None, date_type)

    def __init__(self, name):
        self.name = name
        if name in self.storage:
            raise ValueError('name %r has been used' % name)
        self.storage[name] = self

    @classmethod
    def get(cls, name):
        return cls.storage.get(name)

    def get_uuid(self):
        return 'group:{name}'.format(name=self.name)

    def get_db(self):
        return 'personel'

    def add_personel(self, user_id, user_name):
        group = self.users
        account = Account.get(user_id)
        if not account:
            raise ValueError('%s is not existed' % user_id)
        if user_id in group:
            raise KeyError('key %s conflicted' % user_id)
        group.update({user_id: user_name})
        self.update_props_items({
            'users': group,
            'update_time': str(datetime.now())
        })

    def del_personel(self, user_id):
        group = self.users
        group.pop(user_id, None)
        self.update_props_items({
            'users': group,
            'update_time': str(datetime.now())
        })

    def update_personel(self, user_id, user_name):
        group = self.users
        if user_id in group:
            group[user_id] = user_name
            self.update_props_items({
                'users': group,
                'update_time': str(datetime.now())
            })

staff = PersonelGroup('staff')
