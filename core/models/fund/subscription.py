# -*- coding: utf-8 -*-

'''
用户关注
'''

from warnings import warn
from datetime import datetime
from libs.cache import cache, mc
from libs.db.store import db

from core.models.mixin.props import PropsMixin

_FUND_LIKE_CACHE_PREFIX = 'fund_like:'
FUND_LIKE_CACHE_KEY = _FUND_LIKE_CACHE_PREFIX + '%s'
FUND_LIKE_USER_CACHE_KEY = _FUND_LIKE_CACHE_PREFIX + 'user:%s'
FUND_LIKE_USERCOUNT_CACHE_KEY = _FUND_LIKE_CACHE_PREFIX + 'usercount'


class Subscription(PropsMixin):

    def __init__(self, id, group_id, user_id, create_time, start_date=None):
        self.id = str(id)
        self.group_id = group_id
        self.user_id = user_id
        self.create_time = create_time
        self._start_date = start_date

    def get_db(self):
        return 'like'

    def get_uuid(self):
        return 'like:%s' % self.id

    @classmethod
    @cache(FUND_LIKE_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, group_id, user_id, create_time, start_date '
                        ' from funcombo_userlike '
                        'where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def all(cls):
        """ 系统每天一次的crons查询，非线上方法 """
        rs = db.execute('select id '
                        ' from funcombo_userlike ')
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def is_like(cls, group_id, user_id):
        user_likes = cls.get_by_user(user_id)
        return any(int(ul.group_id) == int(group_id) for ul in user_likes)

    @classmethod
    def like_group(cls, group_id, user_id):
        from .group import Group
        group = Group.get(group_id)
        if not group:
            warn('group %d not found' % (group_id,))
            return False

        if Subscription.is_like(group_id, user_id):
            return False

        id = db.execute('insert into funcombo_userlike '
                        ' (group_id, user_id, create_time) '
                        ' values '
                        ' (%s, %s, %s)', (group_id, user_id, datetime.now()))
        db.commit()
        mc.delete(FUND_LIKE_USER_CACHE_KEY % (user_id,))
        mc.delete(FUND_LIKE_USERCOUNT_CACHE_KEY)
        return id

    @classmethod
    @cache(FUND_LIKE_USER_CACHE_KEY % '{user_id}')
    def get_by_user(cls, user_id):
        rs = db.execute('select id, group_id, user_id, create_time '
                        ' from funcombo_userlike '
                        'where user_id=%s', (user_id,))
        return [cls(*r) for r in rs]

    @property
    def group(self):
        from .group import Group
        return Group.get(self.group_id)

    @classmethod
    @cache(FUND_LIKE_USERCOUNT_CACHE_KEY)
    def get_user_count(cls):
        return db.execute('select count(distinct user_id) from funcombo_userlike')[0][0]

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        if not value or self._start_date:
            return

        self._start_date = value

        sql = ('update funcombo_userlike set start_date=%s'
               ' where user_id=%s and group_id=%s and start_date is NULL')
        params = (self._start_date, self.user_id, self.group_id)
        db.execute(sql, params)
        db.commit()
        mc.delete(FUND_LIKE_USER_CACHE_KEY % (self.user_id,))
