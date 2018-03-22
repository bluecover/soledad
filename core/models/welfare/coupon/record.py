# coding: utf-8

from datetime import datetime

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.base import EntityModel
from core.models.hoard.providers import ProductProvider, zhiwang


class CouponUsageRecord(EntityModel):

    class Status(Enum):
        hooked = 'H'  # 将订单与礼券预绑定
        settled = 'S'  # 订单成功使用了礼券

    table_name = 'coupon_usage_record'
    cache_key = 'coupon:usage_record:v3:{id_}'
    cache_record_ids_by_user_key = 'coupon:usage_record:v3:user:{user_id}'
    cache_record_ids_by_coupon_key = 'coupon:usage_record:v3:coupon:{coupon_id}'
    cache_record_by_partner_order_key = (
        'coupon:usage_record:v3:provider:{provider_id}:order:{order_id}')

    def __init__(self, id_, coupon_id, user_id, provider_id, order_id, status, creation_time):
        self.id_ = str(id_)
        self.coupon_id = str(coupon_id)
        self.user_id = str(user_id)
        self.provider_id = provider_id
        self.order_id = order_id
        self._status = status
        self.creation_time = creation_time

    @cached_property
    def status(self):
        return self.Status(self._status)

    @cached_property
    def coupon(self):
        from .coupon import Coupon
        return Coupon.get(self.coupon_id)

    @cached_property
    def provider(self):
        return ProductProvider.get(self.provider_id)

    @classmethod
    def add(cls, coupon, user, provider, order):
        """与礼券预绑定（发生在用礼券认购产品后）"""
        if not (user.id_ == coupon.user_id == order.user_id):
            raise ValueError('invalid owner validation')

        sql = ('insert into {.table_name} (coupon_id, user_id, provider_id, order_id, '
               'status, creation_time) values (%s, %s, %s, %s, %s, %s)').format(cls)
        params = (coupon.id_, user.id_, provider.id_, order.id_,
                  cls.Status.hooked.value, datetime.now())
        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_record_ids_by_coupon_key(coupon.id_)
        cls.clear_cache_record_ids_by_user_key(user.id_)
        cls.clear_cache_record_by_partner_order(provider.id_, order.id_)
        return cls.get(id_)

    def commit(self):
        # 确认所记录礼券已被成功使用
        if self.provider is zhiwang:
            from core.models.hoard.zhiwang import ZhiwangOrder
            order = ZhiwangOrder.get(self.order_id)
            if order.status is not ZhiwangOrder.Status.success:
                raise ValueError('bound order %s has not succeeded' % self.order_id)

        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.settled.value, self.id_)
        db.execute(sql, params)
        db.commit()

        rsyslog.send('%s\t%s\t%s' % (
            self.provider.shortcut, self.order_id, self.id_), tag='coupon_usage')

        self.clear_cache(self.id_)
        self.clear_cache_record_ids_by_coupon_key(self.coupon_id)
        self.clear_cache_record_ids_by_user_key(self.user_id)
        self.clear_cache_record_by_partner_order(self.provider_id, self.order_id)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, coupon_id, user_id, provider_id, order_id, status, creation_time '
               'from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    @cache(cache_record_ids_by_coupon_key)
    def get_ids_by_coupon(cls, coupon_id):
        sql = 'select id from {.table_name} where coupon_id=%s'.format(cls)
        params = (coupon_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_coupon_id(cls, coupon_id):
        id_list = cls.get_ids_by_coupon(coupon_id)
        return cls.get_multi(id_list)

    @classmethod
    @cache(cache_record_ids_by_user_key)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s'.format(cls)
        params = (user_id, )
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_user_id(cls, user_id):
        id_list = cls.get_ids_by_user(user_id)
        return cls.get_multi(id_list)

    @classmethod
    @cache(cache_record_by_partner_order_key)
    def get_by_partner_order(cls, provider_id, order_id):
        sql = 'select id from {.table_name} where provider_id=%s and order_id=%s'.format(cls)
        params = (provider_id, order_id)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_record_ids_by_coupon_key(cls, coupon_id):
        mc.delete(cls.cache_record_ids_by_coupon_key.format(coupon_id=coupon_id))

    @classmethod
    def clear_cache_record_ids_by_user_key(cls, user_id):
        mc.delete(cls.cache_record_ids_by_user_key.format(user_id=user_id))

    @classmethod
    def clear_cache_record_by_partner_order(cls, provider_id, order_id):
        mc.delete(cls.cache_record_by_partner_order_key.format(
            provider_id=provider_id, order_id=order_id))
