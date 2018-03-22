# coding: utf-8

'''
Profile class
'''

from datetime import datetime
from libs.db.store import db
from libs.cache import cache, mc
from core.models.user.account import Account
from core.models.mixin.props import PropsMixin, PropsItem
from .errors import InsuranceNotFoundError

_INSURE_61_CACHE_KEY_PREFIX = 'insure:ins:61:v1'
INSURE_61_CACHE_KEY = _INSURE_61_CACHE_KEY_PREFIX + ':{account_id}'


class Activity61(PropsMixin):
    table_name = 'insurance_61'

    phone_number = PropsItem('phone_number', default='')
    recommend = PropsItem('recommend', default=[])

    def __init__(self, account_id):
        self.user_id = account_id

    def get_db(self):
        return 'insurance_61'

    def get_uuid(self):
        return 'insurance_61:insurance:%s' % self.user_id

    @classmethod
    def add(cls, account_id):
        if not Account.get(account_id):
            raise InsuranceNotFoundError(account_id, Account)

        existent = cls.get(account_id)
        if existent:
            return existent

        sql = ('insert into {.table_name} (account_id, create_time) '
               'values (%s, %s)').format(cls)

        params = (account_id, datetime.now())
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(account_id)
        return cls.get(account_id)

    @classmethod
    @cache(INSURE_61_CACHE_KEY)
    def get(cls, account_id):
        sql = ('select account_id from {.table_name} where account_id= %s').format(cls)
        param = account_id
        rs = db.execute(sql, param)
        if rs:
            return cls(*rs[0])

    @classmethod
    def clear_cache(cls, account_id):
        mc.delete(INSURE_61_CACHE_KEY.format(account_id=account_id))
