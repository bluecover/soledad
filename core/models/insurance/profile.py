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

_INSURE_PROFILE_CACHE_KEY_PREFIX = 'insure:ins:v3'
INSURE_PROFILE_CACHE_KEY = _INSURE_PROFILE_CACHE_KEY_PREFIX + ':{account_id}'


class Profile(PropsMixin):
    table_name = 'insurance_profile'

    user_will = PropsItem('user_will', default=0, secret=True)
    baby_birthday = PropsItem('baby_birthday',
                              default=datetime.now(), secret=True)
    baby_gender = PropsItem('baby_gender', default='', secret=True)
    child_medicare = PropsItem('child_medicare', default='')
    childins_supplement = PropsItem('childins_supplement', default='')
    child_genetic = PropsItem('child_genetic', default='')
    child_edu = PropsItem('child_edu', default='')
    project = PropsItem('project', default='')

    is_six = PropsItem('is_six', default=False)

    result_data = PropsItem('result_data', default={}, secret=True)

    def __init__(self, account_id, create_time):
        self.user_id = account_id
        self.create_time = create_time

    def get_db(self):
        return 'insurance_profile'

    def get_uuid(self):
        return 'insurance_profile:insurance:%s' % self.user_id

    @classmethod
    def add(cls, account_id):
        if not Account.get(account_id):
            raise InsuranceNotFoundError(account_id, Account)

        existent = cls.get(account_id)
        if existent:
            return existent

        sql = ('insert into {.table_name} (account_id, create_time) '
               'values ( %s, %s)').format(cls)

        params = (account_id, datetime.now())
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(account_id)
        return cls.get(account_id)

    @classmethod
    @cache(INSURE_PROFILE_CACHE_KEY)
    def get(cls, account_id):
        sql = ('select account_id, create_time '
               'from {.table_name} where account_id= %s').format(cls)
        param = account_id
        rs = db.execute(sql, param)
        if rs:
            return cls(*rs[0])

    @classmethod
    def clear_cache(cls, account_id):
        mc.delete(INSURE_PROFILE_CACHE_KEY.format(account_id=account_id))
