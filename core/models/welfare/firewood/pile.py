# coding: utf-8

import uuid
from datetime import datetime
from decimal import Decimal

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.utils import round_half_up
from core.models.base import EntityModel
from core.models.user.account import Account


class FirewoodPiling(EntityModel):
    """抵扣金账户充值记录

    当用户通过不同途径获得抵扣金红包后，将会向对应的抵扣金账户进行充值操作，
    以便后续抵扣使用。
    """

    table_name = 'firewood_piling'
    cache_key = 'firewood:piling:{id_}:v4'
    cache_by_user_id_key = 'firewood:piling:user:{user_id}:v4'

    def __init__(self, id_, user_id, amount, welfare_package_id,
                 remote_transaction_id, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        # 充值红包金额
        self.amount = amount
        # 发放该红包的礼包ID
        self.welfare_package_id = welfare_package_id
        # 抵扣金服务端交易ID
        self._remote_transaction_id = remote_transaction_id
        self.creation_time = creation_time

    def __str__(self):
        return '<FirewoodPiling %s>' % self.id_

    @property
    def display_remark(self):
        return self.wrapper.introduction

    @property
    def display_amount(self):
        return u'+%s元' % round_half_up(self.amount, 2)

    @property
    def simplified_display_amount(self):
        return u'+%s' % round_half_up(self.amount, 2)

    @property
    def signed_amount(self):
        return self.amount

    @property
    def remote_transaction_id(self):
        return uuid.UUID(self._remote_transaction_id)

    @cached_property
    def wrapper(self):
        """充值红包的配置信息"""
        from core.models.welfare import Package
        return Package.get(self.welfare_package_id).kind.firewood_wrapper

    @classmethod
    def add(cls, user, amount, welfare_package, remote_transaction_id):
        """创建抵扣金账户充值记录"""
        from core.models.welfare import Package

        assert isinstance(user, Account)
        assert isinstance(amount, Decimal)
        assert isinstance(welfare_package, Package)

        sql = ('insert into {.table_name} (user_id, amount, welfare_package_id, '
               'remote_transaction_id, creation_time) values (%s, %s, %s, %s, %s)').format(cls)
        params = (user.id_, amount, welfare_package.id_, remote_transaction_id, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache_by_user_id_key(user.id_)
        return cls.get(id_)

    @classmethod
    def delete(cls, id_):
        """删除抵扣金账户充值记录"""
        record = cls.get(id_)
        if not record:
            raise ValueError('deleting record %s is not found' % id_)

        sql = ('delete from {.table_name} where id=%s').format(cls)
        params = (id_,)
        db.execute(sql, params)
        db.commit()

        rsyslog.send('\t'.join([record.id_, record.user_id, str(record.amount),
                                str(record.welfare_package_id)]),
                     tag='solar_firewood_charging_record_deletion')

        cls.clear_cache(id_)
        cls.clear_cache_by_user_id_key(record.user_id)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, amount, welfare_package_id, remote_transaction_id, '
               'creation_time from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_by_user_id_key)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s'.format(cls)
        params = (user_id, )
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        id_list = cls.get_ids_by_user(user_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_user_id_key(cls, user_id):
        mc.delete(cls.cache_by_user_id_key.format(**locals()))
