# coding: utf-8

from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.decorators import DelegatedProperty
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.types import unicode_type, date_type
from .consts import ZW_SAFE_RESERVATION_AMOUNT
from .errors import InvalidWrapRule
from .profit_hike import ProfitHikeMixin, ZhiwangOrderProfitHike
from ..providers import zhiwang


class ZhiwangWrappedProduct(PropsMixin, ProfitHikeMixin):
    """
    Wrapped product is partly reformed from the raw product provided by zhiwang to fit our use.
    """

    class Type(Enum):
        newcomer = 'GH_NEWCOMER'

    Type.newcomer.label = u'新手专享'

    # store
    table_name = 'hoard_zhiwang_wrapped_product'
    cache_key = 'hoard:zhiwang:wrapped_product:{id_}'
    all_ids_cache_key = 'hoard:zhiwang:wrapped_product:all_ids'
    product_ids_by_raw_id_cache_key = 'hoard:zhiwang:wrapped_product:raw_id:{raw_id}'
    product_by_kind_and_raw_id_cache_key = (
        'hoard:zhiwang:wrapped_product:kind_id:{kind_id}:raw_id:{raw_product_id}')

    # local attrs
    name = PropsItem('name', '', unicode_type)
    allocated_amount = PropsItem('allocated_amount', 0, Decimal)
    min_amount = PropsItem('min_amount', 0, Decimal)
    max_amount = PropsItem('max_amount', 0, Decimal)
    annual_rate = PropsItem('annual_rate', 0, Decimal)
    start_date = PropsItem('start_date', None, date_type)
    due_date = PropsItem('due_date', None, date_type)

    # local config
    is_taken_down = PropsItem('is_taken_down', True)

    # delegation
    sale_mode = DelegatedProperty('sale_mode', to='raw_product')
    product_type = DelegatedProperty('product_type', to='raw_product')

    # 合作方
    provider = zhiwang

    # 接受用户使用礼券抵扣优惠
    is_accepting_bonus = False

    def __init__(self, id_, kind_id, raw_product_id, creation_time):
        self.id_ = str(id_)
        self.kind_id = str(kind_id)
        self.raw_product_id = str(raw_product_id)
        self.creation_time = creation_time

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'zhiwang:wrapped_product:{id_}'.format(id_=self.id_)

    @cached_property
    def kind(self):
        from .wrapper_kind import WrapperKind
        return WrapperKind.get(self.kind_id)

    @cached_property
    def raw_product(self):
        from .product import ZhiwangProduct
        return ZhiwangProduct.get(self.raw_product_id)

    @property
    def display_privilege(self):
        raise NotImplementedError

    @property
    def wrapped_product_type(self):
        return self.kind.wrapped_product_type

    @property
    def is_either_sold_out(self):
        """是否已售罄"""
        from .product import SaleMode
        from .order import ZhiwangOrder

        # 首先判断基础产品总量是否售罄
        if self.raw_product.is_sold_out:
            return True

        # 当产品销售模式为共享时，取决于父产品的销售情况
        if self.sale_mode is SaleMode.share:
            return self.raw_product.is_either_sold_out
        elif self.sale_mode is SaleMode.mutex:
            local_sold_amount = ZhiwangOrder.get_wrapped_product_sold_amount(
                self.raw_product.product_id, self.id_)
            return local_sold_amount > (
                self.allocated_amount - ZW_SAFE_RESERVATION_AMOUNT)
        else:
            raise ValueError('invalid sale mode %s' % self.sale_mode)

    @property
    def in_sale(self):
        """是否在销售期内"""
        return self.raw_product.in_sale

    @property
    def in_stock(self):
        # 是否可售状态决定于以下几种情况
        # 1. 是否在销售期内
        # 2. 是否已售罄
        # 3. 是否因其他原因而被暂时设置为暂停销售

        if self.is_either_sold_out or self.is_taken_down:
            return False
        return self.in_sale

    @classmethod
    def create(cls, raw_product, wrapper_kind):
        # check the limit
        if (min(wrapper_kind.limit) < raw_product.min_amount or
                max(wrapper_kind.limit) > raw_product.max_amount):
            raise InvalidWrapRule(wrapper_kind.limit)

        # check the frozen time
        raw_days_period = [
            raw_product.profit_period['min'].value, raw_product.profit_period['max'].value]
        if not min(raw_days_period) <= wrapper_kind.frozen_days.value <= max(raw_days_period):
            raise InvalidWrapRule(wrapper_kind.id_)

        instance = cls.get_by_kind_and_raw_product_id(wrapper_kind.id_, raw_product.product_id)
        if instance is None:
            sql = ('insert into {.table_name} (kind_id, raw_product_id, '
                   'creation_time) values (%s, %s, %s)').format(cls)
            params = (wrapper_kind.id_, raw_product.product_id, datetime.now())
            id_ = db.execute(sql, params)
            db.commit()
            instance = cls.get(id_)
            instance.deploy(wrapper_kind)

            cls.clear_cache(id_)
            cls.clear_all_ids_cache()
            cls.clear_product_ids_by_raw_id_cache(raw_product.product_id)
            cls.clear_product_by_kind_and_raw_cache(wrapper_kind.id_, raw_product.product_id)
        return instance

    def deploy(self):
        raise NotImplementedError

    def is_qualified(self, user_id):
        raise NotImplementedError

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        from .wrapper_kind import WrapperKind
        sql = ('select id, kind_id, raw_product_id, creation_time from {.table_name} '
               'where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            kind = WrapperKind.get(rs[0][1]).wrapped_product_type
            # FIXME: 避免使用subclasses反射
            pcls = next(scls for scls in cls.__subclasses__() if scls.wrapped_product_kind is kind)
            return pcls(*rs[0])

    @classmethod
    def get_all(cls):
        """获取所有可展示子产品"""
        ids = cls.get_all_ids()
        products = (cls.get(id_) for id_ in ids)
        return [p for p in products if p.in_sale]

    @classmethod
    @cache(all_ids_cache_key)
    def get_all_ids(cls):
        sql = ('select id from {.table_name} order by creation_time desc').format(cls)
        rs = db.execute(sql)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_raw(cls, raw_id):
        product_ids = cls.get_ids_by_raw(raw_id)
        return [cls.get(product_id) for product_id in product_ids]

    @classmethod
    @cache(product_ids_by_raw_id_cache_key)
    def get_ids_by_raw(cls, raw_id):
        sql = ('select id from {.table_name} where raw_product_id=%s').format(cls)
        params = (raw_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(product_by_kind_and_raw_id_cache_key)
    def get_by_kind_and_raw_product_id(cls, kind_id, raw_product_id):
        sql = ('select id from {.table_name} where kind_id=%s and raw_product_id=%s').format(cls)
        params = (kind_id, raw_product_id)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_all_ids_cache(cls):
        mc.delete(cls.all_ids_cache_key)

    @classmethod
    def clear_product_ids_by_raw_id_cache(cls, raw_id):
        mc.delete(cls.product_ids_by_raw_id_cache_key.format(**locals()))

    @classmethod
    def clear_product_by_kind_and_raw_cache(cls, kind_id, raw_product_id):
        mc.delete(cls.product_by_kind_and_raw_id_cache_key.format(**locals()))


class ZhiwangNewComerProduct(ZhiwangWrappedProduct):
    wrapped_product_kind = ZhiwangWrappedProduct.Type.newcomer
    profit_hike_kind = ZhiwangOrderProfitHike.Kind.newcomer

    def has_profit_hike(self):
        """是否有优惠活动"""
        return True

    def get_profit_hike(self, user_id):
        """获取某用户的福利"""
        if self.is_qualified(user_id):
            return self.bonus_annual_rate

    def is_qualified(self, user_id):
        from ..manager import SavingsManager
        return SavingsManager(user_id).is_new_savings_user

    @property
    def local_name(self):
        return u'新手专享产品'

    @property
    def display_privilege(self):
        return u'独享%s%%超高收益率' % self.annual_rate

    @property
    def annual_rate_layers(self):
        return []

    @cached_property
    def profit_period(self):
        return {'min': self.kind.frozen_days, 'max': self.kind.frozen_days}

    @cached_property
    def profit_annual_rate(self):
        return {'min': self.annual_rate, 'max': self.annual_rate}

    @property
    def origin_annual_rate(self):
        return self.raw_product.get_annual_rate_by_date(self.due_date)

    @property
    def bonus_annual_rate(self):
        return self.annual_rate - self.origin_annual_rate

    def deploy(self, wrapper_kind):
        self.name = wrapper_kind.name
        self.min_amount, self.max_amount = wrapper_kind.limit
        self.annual_rate = str(wrapper_kind.annual_rate)
        self.start_date = str(self.raw_product.start_date)
        self.due_date = str(
            self.raw_product.start_date + timedelta(days=wrapper_kind.frozen_days.value))
