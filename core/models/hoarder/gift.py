# coding: utf-8

from datetime import datetime
from enum import Enum

from libs.db.store import db
from libs.cache import mc, cache
from .product import Product
from .order import HoarderOrder


class GiftUsageRecord(object):

    table_name = 'hoarder_order_gift_usage_record'
    cache_key = 'hoarder:order_gift_usage:{id_}'
    cache_key_by_product_and_order_id = (
        'hoarder:order_gift_usage:product:{product_id}:order_id:{order_id}')

    class Status(Enum):
        # 处理中
        dealing = 'D'
        # 成功
        success = 'S'
        # 失败
        failure = 'F'

    def __init__(self, id_, product_id, order_id, gift_type, effective_amount,
                 status, effective_time, end_time, creation_time):
        self.id_ = str(id_)
        self.product_id = str(product_id)
        self.order_id = str(order_id)
        self.gift_type = gift_type
        self.effective_amount = effective_amount
        self._status = status
        self.effective_time = effective_time
        self.end_time = end_time
        self.creation_time = creation_time

    @property
    def product(self):
        return Product.get(self.product_id)

    @property
    def order(self):
        return HoarderOrder.get(self.order_id)

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, new_status):
        assert isinstance(new_status, self.Status)

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (new_status.value, self.id_)
        db.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)
        self.clear_cache_by_product_and_order_id(self.product_id, self.order_id)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, product_id, order_id, gift_type, effective_amount,'
            ' status, effective_time, end_time, creation_time'
            ' from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0])

    @classmethod
    @cache(cache_key_by_product_and_order_id)
    def get_by_product_and_order_id(cls, product_id, order_id):
        sql = 'select id from {.table_name} where product_id=%s and order_id=%s'.format(cls)
        params = (product_id, order_id)
        rs = db.execute(sql, params)

        return cls.get(rs[0][0]) if rs else None

    @classmethod
    def add(cls, product_id, order_id, gift_type,
            effective_amount, status, effective_time, end_time):
        assert isinstance(status, cls.Status)

        sql = (
            'insert into {.table_name} '
            ' (product_id, order_id, gift_type, effective_amount, status,'
            ' effective_time, end_time, creation_time)'
            ' values(%s, %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (
            product_id, order_id, gift_type, effective_amount,
            status.value, effective_time, end_time, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_product_and_order_id(product_id, order_id)

        return cls.get(id_)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_product_and_order_id(cls, product_id, order_id):
        mc.delete(
            cls.cache_key_by_product_and_order_id.format(product_id=product_id, order_id=order_id))
