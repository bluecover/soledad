# coding:utf-8

from datetime import datetime

import MySQLdb

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from .errors import (RedemptionBeyondLimitPerCodeError, RedeemCodeUsedError,
                     RedemptionBeyondLimitPerUserError)


class RedeemCodeUsage(EntityModel):
    """兑换码使用记录

    用来记录用户使用兑换码的情况

    :param code_id: 兑换码id
    :param user_id: 使用兑换码的用户id
    :param activity_id: 兑换码所属活动的id
    :param consumed_time: 使用兑换码的时间
    """

    table_name = 'redeem_code_usage'
    cache_key = 'redeem_code_usage:{id_}'
    cache_ids_by_user_and_activity_id_key = ('redeem_code_usage:ids_user_activity:'
                                             '{user_id}:{activity_id}')
    cache_ids_by_code_id_key = 'redeem_code_usage:code_id:{code_id}'
    cache_ids_by_user_id_key = 'redeem_code_usage:user_id:{user_id}'
    cache_count_by_code_id_key = 'redeem_code_usage:count:{code_id}'
    cache_count_by_user_and_activity_id_key = ('redeem_code_usage:count_user_activity:'
                                               '{user_id}:{activity_id}')

    def __init__(self, id_, code_id, user_id, activity_id, consumed_time):
        self.id_ = str(id_)
        self.code_id = str(code_id)
        self.user_id = str(user_id)
        self.activity_id = str(activity_id)
        self.consumed_time = consumed_time

    @classmethod
    def add(cls, redeem_code, user):
        sql = ('insert into {.table_name} (code_id, user_id, activity_id, consumed_time)'
               ' values(%s, %s, %s, %s)').format(cls)
        params = (redeem_code.id_, user.id_, redeem_code.activity.id_, datetime.now())
        try:
            id_ = db.execute(sql, params)
        except MySQLdb.IntegrityError:
            raise RedeemCodeUsedError()
        code_used_times = cls.count_by_code_id(redeem_code.id_)
        code_usage = cls.get(id_)

        #: 超出兑换码本身使用次数限制时抛出异常
        if code_used_times > redeem_code.max_usage_limit_per_code:
            code_usage.delete_by_id(code_usage.id_)
            raise RedemptionBeyondLimitPerCodeError()
        usage_used_times = cls.count_by_user_and_activity(user.id_, redeem_code.activity.id_)

        #: 用户在本次活动中使用兑换码数量超过活动限制时抛出异常
        if usage_used_times > redeem_code.activity.max_usage_limit_per_user:
            code_usage.delete_by_id(code_usage.id_)
            raise RedemptionBeyondLimitPerUserError()
        else:
            db.commit()

        #: 清除缓存
        cls.clear_cache(id_)
        cls.clear_cache_by_user_id(user.id_)
        cls.clear_cache_by_user_and_activity_id(user.id_, redeem_code.activity.id_)
        cls.clear_cache_by_code_id(redeem_code.id_)

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, code_id, user_id, activity_id, consumed_time'
               ' from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(str(id_)) for id_ in ids]

    def delete_by_id(self, id_):
        sql = 'delete from {.table_name} where id=%s'.format(self)
        params = (id_,)
        db.execute(sql, params)
        db.commit()

        # 清除缓存
        self.clear_cache(id_)
        self.clear_cache_by_user_id(self.user_id)
        self.clear_cache_by_user_and_activity_id(self.user_id, self.activity_id)
        self.clear_cache_by_code_id(self.code_id)

    @classmethod
    @cache(cache_ids_by_user_and_activity_id_key)
    def get_ids_by_user_and_activity(cls, user_id, activity_id):
        sql = 'select id from {.table_name} where user_id=%s and activity_id=%s'.format(cls)
        params = (user_id, activity_id)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_user_and_activity(cls, user_id, activity_id):
        ids = cls.get_ids_by_user_and_activity(user_id, activity_id)
        return cls.get_multi(ids)

    @classmethod
    @cache(cache_ids_by_code_id_key)
    def get_ids_by_code(cls, code_id):
        sql = 'select id from {.table_name} where code_id=%s'.format(cls)
        params = (code_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_redeem_code(cls, code_id):
        ids = cls.get_ids_by_code(code_id)
        return cls.get_multi(ids)

    @classmethod
    @cache(cache_ids_by_user_id_key)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s'.format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        ids = cls.get_ids_by_user(user_id)
        return cls.get_multi(ids)

    @classmethod
    def get_by_code_and_user(cls, code_id, user_id):
        sql = ('select id, code_id, user_id, consumed_time'
               ' from {.table_name} where code_id=%s and user_id=%s').format(cls)
        params = (code_id, user_id)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    @cache(cache_count_by_code_id_key)
    def count_by_code_id(cls, code_id):
        sql = 'select count(code_id) from redeem_code_usage where code_id=%s'.format(cls)
        params = (code_id,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    @cache(cache_count_by_user_and_activity_id_key)
    def count_by_user_and_activity(cls, user_id, activity_id):
        sql = ('select count(user_id) from redeem_code_usage'
               ' where user_id=%s and activity_id=%s').format(cls)
        params = (user_id, activity_id)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_user_id(cls, user_id):
        mc.delete(cls.cache_ids_by_user_id_key.format(user_id=user_id))

    @classmethod
    def clear_cache_by_code_id(cls, code_id):
        mc.delete(cls.cache_ids_by_code_id_key.format(code_id=code_id))
        mc.delete(cls.cache_count_by_code_id_key.format(code_id=code_id))

    @classmethod
    def clear_cache_by_user_and_activity_id(cls, user_id, activity_id):
        mc.delete(cls.cache_count_by_user_and_activity_id_key.format(
            user_id=user_id, activity_id=activity_id))
        mc.delete(cls.cache_ids_by_user_and_activity_id_key.format(
            user_id=user_id, activity_id=activity_id))
