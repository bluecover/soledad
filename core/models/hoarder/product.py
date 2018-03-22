# -*- coding: utf-8 -*-

from decimal import Decimal
from datetime import datetime, timedelta, date

from enum import Enum
from babel.numbers import format_number

from jupiter.integration.bearychat import BearyChat
from libs.db.store import db
from libs.cache import mc, cache
from core.models.hoard.stats import get_savings_new_comer_product_threshold
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.types import unicode_type
from core.models.utils.cal_date import get_effect_date
from .consts import (
    NEW_COMER_PRODUCT_GIFT_PERIOD_VALUE, NEW_COMER_PRODUCT_EFFECTIVE_AMOUNT_LIMIT,
    NEW_COMER_PRODUCT_OPERATION_NUM)
from .vendor import Vendor
from .errors import ProductDeprecatedError, ProductLowQuotaError, ProductDuplicateSaleModeError

bearychat = BearyChat('savings_xm')


class PeriodUnit(Enum):
    """期限单位"""

    month = 1
    weekday = 2
    day = 3


class Product(PropsMixin):
    """产品"""

    table_name = 'hoarder_product'
    cache_key = 'hoarder:product:v1:{product_id}'
    cache_by_vendor = 'hoarder:products:v1:{vendor_id}'

    class Status(Enum):
        """产品状态"""
        # 在售
        on_sell = 'S'
        # 废弃
        deprecated = 'D'

    class Type(Enum):
        """产品期限分类"""
        # 固定期限类
        classic = 'C'
        # 不定期限类
        dynamic = 'D'
        # 不限期限类
        unlimited = 'U'

    class RedeemType(Enum):
        """赎回类型"""
        # 到期自动赎回
        auto = '2'
        # 用户申请赎回
        user = '1'

    class Kind(Enum):
        """父子产品分类"""
        # 父产品
        father = 'F'
        # 子产品
        child = 'C'

    # 产品名称
    name = PropsItem('name', u'', unicode_type)
    # 产品可用配额
    quota = PropsItem('quota', 0, Decimal)
    # 产品总配额
    total_quota = PropsItem('total_quota', 0, Decimal)
    # 产品当日配额
    today_quota = PropsItem('today_quota', 0, Decimal)
    # 产品累计交易额
    total_amount = PropsItem('total_amount', 0, Decimal)
    # 客户最大可购买 金额(客户对产品 购买的最大累计 金额)
    total_buy_amount = PropsItem('total_buy_amount', 0, Decimal)
    # 最小赎回金额(针对允许用户主动 发起赎回的产品, 例如活期类日日盈产品等)
    min_redeem_amount = PropsItem('min_redeem_amount', 0, Decimal)
    # 最大赎回金额
    max_redeem_amount = PropsItem('max_redeem_amount', 0, Decimal)
    # 每日赎回限额
    day_redeem_amount = PropsItem('day_redeem_amount', 0, Decimal)
    # 加息年化利率
    interest_rate_hike = PropsItem('interest_rate_hike', 0, Decimal)
    # 备注信息
    description = PropsItem('description', u'', unicode_type)
    # 上架下架控制
    is_taken_down = PropsItem('is_taken_down', True, bool)
    # 预售控制
    is_pre_sale = PropsItem('is_pre_sale', False, bool)
    # 预售时间
    pre_hour = PropsItem('pre_hour')

    expire_period_unit = PropsItem('expire_period_unit', PeriodUnit.day.value, int)
    expire_period = PropsItem('expire_period', 0, int)

    is_accepting_bonus = False

    def __init__(self, product_id, remote_id, status, product_type, kind, min_amount, max_amount,
                 rate_type, rate, effect_day_condition, effect_day, effect_day_unit, redeem_type,
                 start_sell_date, end_sell_date, update_time, creation_time, vendor_id):
        self.id_ = product_id
        self.remote_id = remote_id
        self._status = status
        self._type = product_type
        self._kind = kind
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.rate_type = rate_type
        self.rate = rate
        self.effect_day_condition = effect_day_condition
        self.effect_day = effect_day
        self.effect_day_unit = effect_day_unit
        # 赎回类型
        self.redeem_type = redeem_type
        self.start_sell_date = start_sell_date
        self.end_sell_date = end_sell_date
        self.update_time = update_time
        self.creation_time = creation_time
        self.vendor_id = vendor_id

    def get_db(self):
        return 'hoarder'

    def get_uuid(self):
        return 'product:{product_id}'.format(product_id=self.id_)

    @property
    def status(self):
        return self.Status(self._status)

    @property
    def ptype(self):
        return self.Type(self._type)

    @property
    def kind(self):
        return self.Kind(self._kind)

    @property
    def product_type(self):
        return self.ptype

    @property
    def can_redeem(self):
        """是否可手动赎回"""
        t = self.RedeemType(self.redeem_type)
        if t is self.RedeemType.auto:
            return False
        # TODO:增加其他不可赎回限制条件

        return True

    @property
    def value_date(self):
        """预期起息日"""
        start_time = datetime.now() + timedelta(days=1)
        return get_effect_date(start_time)

    @property
    def check_benefit_date(self):
        if self.ptype is self.Type.unlimited:
            start_time = datetime(self.value_date.year, self.value_date.month, self.value_date.day)
            return get_effect_date(start_time + timedelta(days=1))
        return self.value_date

    @property
    def expect_due_date(self):
        """预期到期日"""
        if self.ptype is not self.Type.unlimited:
            start_time = datetime(self.value_date.year, self.value_date.month, self.value_date.day)
            return get_effect_date(start_time + timedelta(days=self.frozen_days))

    @property
    def is_sold_out(self):
        from .order import HoarderOrder
        if self.kind is self.Kind.father:
            local_daily_sold_amount = HoarderOrder.get_product_daily_sold_amount_by_now(self.id_)
            if local_daily_sold_amount >= self.quota - get_savings_new_comer_product_threshold():
                return True
        if self.quota < self.min_amount:
            return True
        return False

    @property
    def is_in_sale_period(self):
        return self.start_sell_date <= date.today() < self.end_sell_date

    @property
    def is_on_sale(self):
        if self.is_taken_down or self.is_sold_out:
            return False
        if self.status is self.Status.deprecated:
            return False
        return True

    @classmethod
    @cache(cache_key)
    def get(cls, product_id):
        sql = ('select id, remote_id, status, type, kind, min_amount, max_amount, rate_type, rate,'
               ' effect_day_condition, effect_day, effect_day_unit, redeem_type,'
               ' start_sell_date, end_sell_date, update_time, creation_time, vendor_id'
               ' from {.table_name} where id=%s').format(cls)
        params = (product_id,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def add_or_update(cls, vendor_id, remote_id, name, quota, total_quota, today_quota,
                      total_amount, total_buy_amount, min_redeem_amount, max_redeem_amount,
                      day_redeem_amount, interest_rate_hike, description, product_type,
                      min_amount, max_amount, rate_type, rate, effect_day_condition, effect_day,
                      effect_day_unit, redeem_type, start_sell_date, end_sell_date, expire_period=1,
                      expire_period_unit=PeriodUnit.day.value, is_child_product=False):
        assert isinstance(product_type, cls.Type)
        sql = ('insert into {.table_name} (remote_id, status, type, kind, min_amount, max_amount,'
               'rate_type, rate, effect_day_condition, effect_day, effect_day_unit,'
               'redeem_type, start_sell_date, end_sell_date, update_time,'
               'creation_time, vendor_id) '
               'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
               'on duplicate key update rate=values(rate), update_time=values(update_time)').format(
            cls)
        kind = cls.Kind.child.value if is_child_product else cls.Kind.father.value
        params = (remote_id, cls.Status.on_sell.value, product_type.value, kind, min_amount,
                  max_amount, rate_type, rate, effect_day_condition, effect_day, effect_day_unit,
                  redeem_type, start_sell_date, end_sell_date, datetime.now(),
                  datetime.now(), vendor_id)

        rs = db.execute(sql, params)
        db.commit()

        if rs:
            cls.clear_cache(rs)

        p = cls.get_by_remote_id(vendor_id, remote_id)
        original_quota = p.quota
        if p:
            p.name = name
            p.quota = quota
            p.total_quota = total_quota
            p.today_quota = today_quota
            p.total_amount = total_amount
            p.total_buy_amount = total_buy_amount
            p.min_redeem_amount = min_redeem_amount
            p.max_redeem_amount = max_redeem_amount
            p.day_redeem_amount = day_redeem_amount
            p.interest_rate_hike = interest_rate_hike
            p.description = description
            p.expire_period = expire_period
            p.expire_period_unit = expire_period_unit
            # 当销售周期内产品额度调整时，发出BC通知

            if bearychat.configured:
                quota_txt = format_number(quota, locale='en_US')
                original_quota_txt = format_number(original_quota, locale='en_US')
                if quota < p.min_amount:
                    txt = u'最近一笔：**￥{}**，当前额度：**￥{}**'.format(original_quota_txt, quota_txt)
                    attachment = bearychat.attachment(title=None,
                                                      text=txt,
                                                      color='#ffa500',
                                                      images=[])
                    bearychat.say(u'产品 **{}** **售罄** 啦，正在尝试释放未支付订单，请周知。'.format(
                        name), attachments=[attachment])
                if quota > int(original_quota) + int(p.min_amount):
                    txt = u'更新前额度：**￥{}**, 当前额度：**￥{}**'.format(original_quota_txt, quota_txt)
                    attachment = bearychat.attachment(title=None, text=txt, color='#a5ff00',
                                                      images=[])
                    bearychat.say(u'产品 **{}** **额度** 增加啦 :clap:，请周知。'.format(name),
                                  attachments=[attachment])
        return p

    @classmethod
    @cache(cache_by_vendor)
    def get_product_ids_by_vendor_id(cls, vendor_id):
        sql = 'select id from {.table_name} where vendor_id=%s'.format(cls)
        params = (vendor_id,)
        rs = db.execute(sql, params)
        return [p[0] for p in rs if rs]

    @classmethod
    def get_products_by_vendor_id(cls, vendor_id):
        return [cls.get(id_) for id_ in cls.get_product_ids_by_vendor_id(vendor_id)]

    @classmethod
    def get_by_remote_id(cls, vendor_id, remote_id):
        sql = 'select id from {.table_name} where vendor_id=%s and remote_id=%s'.format(cls)
        params = (vendor_id, remote_id,)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0]) if rs else None

    def go_on_sale(self):
        """上架"""
        if not self.is_taken_down:
            raise ProductDuplicateSaleModeError()
        if self.status is self.Status.deprecated:
            raise ProductDeprecatedError()
        if self.quota < self.min_amount:
            raise ProductLowQuotaError()
        self.is_taken_down = False

    def go_off_sale(self):
        """下架"""
        self.is_taken_down = True

    @classmethod
    def get_products_on_sale(cls):
        vendors = Vendor.get_all()
        for vendor in vendors:
            for p in cls.get_products_by_vendor_id(vendor.id_):
                if p.is_on_sale:
                    yield p

    @property
    def vendor(self):
        return Vendor.get(self.vendor_id)

    @classmethod
    def clear_cache(cls, product_id):
        mc.delete(cls.cache_key.format(product_id=product_id))
        p = cls.get(product_id)
        if p:
            mc.delete(cls.cache_by_vendor.format(vendor_id=p.vendor_id))

    @property
    def frozen_days(self):
        if PeriodUnit(self.expire_period_unit) is PeriodUnit.day:
            return self.expire_period
        if PeriodUnit(self.expire_period_unit) is PeriodUnit.month:
            return self.expire_period * 30

    @property
    def profit_period(self):
        from core.models.hoard.common import ProfitPeriod
        value = ProfitPeriod(self.frozen_days, 'day')
        return {'min': value, 'max': value}


class NewComerProduct(Product):

    cache_key = 'hoarder:new_comer_product:{product_id}'
    cache_by_vendor = 'hoarder:new_comer_products:{vendor_id}'

    @property
    def effective_amount_limit(self):
        return NEW_COMER_PRODUCT_EFFECTIVE_AMOUNT_LIMIT

    @property
    def operation_num(self):
        return NEW_COMER_PRODUCT_OPERATION_NUM

    @property
    def profit_period(self):
        from core.models.hoard.common import ProfitPeriod
        value = ProfitPeriod(NEW_COMER_PRODUCT_GIFT_PERIOD_VALUE, 'day')
        return {'min': value, 'max': value}

    @classmethod
    @cache(cache_key)
    def get(cls, product_id):
        sql = ('select id, remote_id, status, type, kind, min_amount, max_amount, rate_type, rate,'
               ' effect_day_condition, effect_day, effect_day_unit, redeem_type,'
               ' start_sell_date, end_sell_date, update_time, creation_time, vendor_id'
               ' from {.table_name} where id=%s').format(cls)
        params = (product_id,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_father_product_by_vendor_id(cls, vendor_id):
        products = cls.get_products_by_vendor_id(vendor_id)
        father_products = [p for p in products if p.kind is cls.Kind.father]
        return father_products[0]
