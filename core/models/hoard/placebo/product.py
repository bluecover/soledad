# coding: utf-8

from __future__ import absolute_import

import collections
import datetime

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from ..common import ProfitPeriod


class StrategyStorage(dict):
    """体验金领取策略池."""

    #: 体验金领取策略
    Strategy = collections.namedtuple('Strategy', [
        'id_', 'name', 'target'])

    def register(self, id_, name, target=None):
        """注册体验金策略.

        :param id_: 策略唯一 ID
        :param name: 策略名称, 用于显示
        :param target: 可选的策略目标 (函数或其他可调用对象). 当本参数为
                       ``None`` 时本方法为装饰器.
        """
        id_ = str(id_)

        def wrapper(wrapped):
            self[id_] = self.Strategy(id_, name, wrapped)
            return self[id_]

        if target is None:
            return wrapper
        else:
            return wrapper(target)


class PlaceboProduct(EntityModel):
    """攒钱助手体验金产品."""

    table_name = 'hoard_placebo_product'
    cache_key = 'hoard:placebo:product:{id_}'
    cache_all_ids_key = 'hoard:placebo:product:ids'
    cache_by_strategy_key = 'hoard:placebo:product:strategy:{strategy_id}:ids'

    strategy_storage = StrategyStorage()

    def __init__(self, id_, strategy_id, min_amount, max_amount,
                 start_sell_date, end_sell_date, frozen_days, annual_rate,
                 creation_time):
        self.id_ = str(id_)
        self.strategy_id = str(strategy_id)
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.start_sell_date = start_sell_date
        self.end_sell_date = end_sell_date
        self.frozen_days = frozen_days
        self.annual_rate = annual_rate
        self.creation_time = creation_time

    @cached_property
    def strategy(self):
        return self.strategy_storage[self.strategy_id]

    @cached_property
    def profit_period(self):
        value = ProfitPeriod(self.frozen_days, 'day')
        return {'min': value, 'max': value}

    @cached_property
    def profit_annual_rate(self):
        return {'min': self.annual_rate, 'max': self.annual_rate}

    @property
    def in_stock(self):
        return self.start_sell_date <= datetime.date.today() < self.end_sell_date

    def make_exiting_date(self, creation_date):
        return creation_date + datetime.timedelta(days=self.frozen_days)

    @classmethod
    def get_product_annotations(cls, coupons, product):
        return []

    @classmethod
    def add(cls, strategy, min_amount, max_amount, start_sell_date,
            end_sell_date, frozen_days, annual_rate):
        sql = (
            'insert into {0} (strategy_id, min_amount, max_amount,'
            ' start_sell_date, end_sell_date, frozen_days, annual_rate,'
            ' creation_time) '
            'values (%s, %s, %s, %s, %s, %s, %s, %s)').format(cls.table_name)
        params = (
            strategy.id_, min_amount, max_amount, start_sell_date,
            end_sell_date, frozen_days, annual_rate, datetime.datetime.now())
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_strategy(strategy.id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, strategy_id, min_amount, max_amount, start_sell_date,'
            ' end_sell_date, frozen_days, annual_rate, creation_time '
            'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_all_ids_key)
    def get_all_ids(cls):
        """获取所有产品 ID 列表."""
        sql = 'select id from {0} order by id desc'.format(cls.table_name)
        rs = db.execute(sql)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi(cls, ids, user_id=None):
        """获取产品列表.

        :param ids: 产品 ID 列表
        :param user_id: 用户 ID, 不为 ``None`` 时执行策略过滤产品.
        """
        products = (cls.get(id_) for id_ in ids)
        if user_id is None:
            return list(products)
        else:
            return [p for p in products if p.strategy.target(user_id)]

    @classmethod
    @cache(cache_by_strategy_key)
    def get_ids_by_strategy(cls, strategy_id):
        """根据策略 ID 获取产品 ID 列表."""
        sql = (
            'select id from {0} where strategy_id = %s '
            'order by id desc').format(cls.table_name)
        params = (strategy_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))
        mc.delete(cls.cache_all_ids_key)

    @classmethod
    def clear_cache_by_strategy(cls, strategy_id):
        mc.delete(cls.cache_by_strategy_key.format(**locals()))
