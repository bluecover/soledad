# coding: utf-8

import datetime
from decimal import Decimal

from arrow import Arrow
from enum import Enum
from werkzeug.utils import cached_property

from jupiter.ext import sentry
from jupiter.integration.bearychat import BearyChat
from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.types import unicode_type, date_type
from .consts import ZW_SAFE_RESERVATION_AMOUNT
from .errors import InvalidProductError, ImproperAmountAllocation
from .profit_hike import ProfitHikeMixin
from ..common import ProfitPeriod
from ..providers import zhiwang


bearychat = BearyChat('savings')


class SaleMode(Enum):
    share = 'SHARE'
    mutex = 'MUTEX'


class ZhiwangProduct(PropsMixin, ProfitHikeMixin):

    class Type(Enum):
        classic = 'PT_CLASSIC'
        fangdaibao = 'PT_FANGDAIBAO'

    Type.classic.label = u'定期产品'
    Type.fangdaibao.label = u'不定期产品'

    # 存储
    table_name = 'hoard_zhiwang_product'
    cache_key = 'hoard:zhiwang:product:v1:{product_id}'
    cache_ids_by_date_key = 'hoard:zhiwang:product:v1:{date}:ids'

    # 指旺配置
    name = PropsItem('name', '', unicode_type)
    annual_rate = PropsItem('annual_rate', 0, Decimal)
    min_amount = PropsItem('min_amount', 0, Decimal)
    max_amount = PropsItem('max_amount', 0, Decimal)
    total_amount = PropsItem('total_amount', 0, Decimal)
    sold_amount = PropsItem('sold_amount', 0, Decimal)
    is_sold_out = PropsItem('is_sold_out', False)
    start_date = PropsItem('start_date', None, date_type)
    due_date = PropsItem('due_date', None, date_type)
    description = PropsItem('description', u'', unicode_type)
    blank_contract_url = PropsItem('blank_contract_url', '')

    # 本地配置
    is_taken_down = PropsItem('is_taken_down', True)
    allocated_amount = PropsItem('allocated_amount', 0, Decimal)
    mix_sale_mode = PropsItem('mix_sale_mode', SaleMode.share.value)

    # 订单金额增量
    increasing_step = 1

    # 所属合作方
    provider = zhiwang

    # 接受用户使用礼券抵扣优惠
    is_accepting_bonus = True

    def __init__(self, product_id, product_type, start_sell_date,
                 end_sell_date, creation_time):
        self.product_id = product_id
        self._product_type = product_type
        self.start_sell_date = start_sell_date
        self.end_sell_date = end_sell_date
        self.creation_time = creation_time

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'zhiwang:prodcut:{product_id}'.format(product_id=self.product_id)

    # For mobile API
    # TODO (tonyseek) make a wrapper to unify the API of zhiwang / yixin

    @property
    def unique_product_id(self):
        return self.product_id

    @property
    def is_either_sold_out(self):
        from .order import ZhiwangOrder
        # 先根据指旺数据判断是否售罄
        if self.is_sold_out:
            return True

        # 再根据本地情况判断
        if self.sale_mode is SaleMode.share:
            local_sold = ZhiwangOrder.get_raw_product_sold_amount(self.product_id)
            up_limit = self.total_amount
        elif self.sale_mode is SaleMode.mutex:
            local_sold = ZhiwangOrder.get_wrapped_product_sold_amount(self.product_id)
            up_limit = self.allocated_amount
        return local_sold > up_limit - ZW_SAFE_RESERVATION_AMOUNT

    @property
    def in_sale(self):
        return self.start_sell_date <= datetime.date.today() < self.end_sell_date

    @property
    def in_stock(self):
        # 是否可售状态决定于以下几种情况
        # 1. 更新产品时发现指旺分配额度与该日销售总额差值小于1000即最小可购买值
        # 2. 根据好规划需求进行强制售罄
        # 3. 指旺抢占额度导致条件1尚未满足时发生接口报告无债权可卖

        if self.is_either_sold_out or self.is_taken_down:
            return False
        return self.in_sale

    @property
    def profit_period(self):
        raise NotImplementedError

    @property
    def profit_annual_rate(self):
        raise NotImplementedError

    @property
    def product_type(self):
        return self.Type(self._product_type)

    @property
    def wrapped_product_type(self):
        return

    @property
    def activity_type(self):
        return ''

    @property
    def wrapped_product_id(self):
        return ''

    @property
    def sale_mode(self):
        return SaleMode(self.mix_sale_mode)

    @sale_mode.setter
    def sale_mode(self, mode):
        assert isinstance(mode, SaleMode)
        self.mix_sale_mode = mode.value

    @property
    def is_updating(self):
        return self.start_date is None or self.due_date is None

    @classmethod
    def get_multi(cls, ids):
        return [o for o in (cls.get(id_) for id_ in ids) if not o.is_updating]

    @classmethod
    def get_all(cls):
        """获取所有可展示产品"""
        ids = cls.get_ids_by_date(datetime.date.today())
        return cls.get_multi(ids)

    @classmethod
    @cache(cache_ids_by_date_key)
    def get_ids_by_date(cls, date):
        assert isinstance(date, datetime.date)
        sql = ('select product_id from {.table_name} '
               'where start_sell_date <= %s and end_sell_date > %s '
               'order by creation_time desc').format(cls)
        rs = db.execute(sql, (date, date))
        return [r[0] for r in rs]

    @classmethod
    def get_product_annotations(cls, coupons, product):
        annotations = []
        matched_coupons = [c for c in coupons.deduplicated_available_coupons
                           if c.is_available_for_product(product)]
        if matched_coupons:
            annotations.append(u'有礼券可用')
            return annotations

    @classmethod
    @cache(cache_key)
    def get(cls, product_id):
        sql = ('select product_id, product_type, start_sell_date, end_sell_date, '
               'creation_time from {.table_name} where product_id=%s').format(cls)
        params = (product_id,)
        rs = db.execute(sql, params)
        if rs:
            return PRODUCT_TYPE_CLS_MAP[cls.Type(rs[0][1])](*rs[0])

    @classmethod
    def add(cls, product_info):
        from .wrapped_product import ZhiwangWrappedProduct
        from .wrapper_kind import WrapperKind

        pid = product_info.pop('product_id')
        ptype = product_info.pop('product_type')
        start_sell_date = product_info.pop('start_sell_date')
        end_sell_date = product_info.pop('end_sell_date')

        # 判断产品类型是否被支持
        try:
            ptype = cls.Type(ptype)
        except ValueError:
            raise InvalidProductError(ptype)

        # 将产品基本属性记入数据库
        existence = cls.get(pid)
        if existence:
            original_total_amount = existence.total_amount

        sql = ('insert into {.table_name} (product_id, product_type, start_sell_date, '
               'end_sell_date, creation_time) values (%s, %s, %s, %s, %s) '
               'on duplicate key update product_id=product_id').format(cls)
        params = (pid, ptype.value, start_sell_date, end_sell_date,
                  datetime.datetime.now())
        db.execute(sql, params)
        db.commit()

        cls.clear_cache(pid)
        cls.clear_cache_by_date(datetime.date.today())

        instance = cls.get(pid)

        # FIXME: 对不定期产品房贷宝的利率阶梯的数据加工应当在包中处理完毕
        if ptype is cls.Type.fangdaibao:
            detail_dict = {
                'last_due_date': product_info.detail_config.last_due_date,
                'annual_rate_layers': product_info.detail_config.annual_rate_layers,
            }
            product_info.update(detail_dict)
            vars(product_info).update(detail_dict)
            product_info.pop('detail_config')

        # 更新指旺产品最新参数
        for name in product_info:
            # 检查是否有未支持的属性
            if not isinstance(getattr(instance.__class__, name, None), PropsItem):
                sentry.captureMessage('Follow attribute is not supported', attr_name=name)
                continue

            value = getattr(product_info, name)
            if isinstance(value, Decimal) or isinstance(value, datetime.date):
                value = str(value)
            if isinstance(value, Arrow):
                value = value.isoformat()
            setattr(instance, name, value)

        # 当销售周期内产品额度发生变化时，发出BC通知
        if existence:
            increment = instance.total_amount - original_total_amount
            if increment > 0 and bearychat.configured:
                bearychat.say(u'指旺端刚刚为%s增加了%s额度，请周知。' % (
                    existence.local_name, increment))

        # 对于房贷宝产品还需创建包装产品和调整额度分配
        if instance.product_type is cls.Type.fangdaibao:
            if existence:
                # 当销售周期内产品总额度发生变化且销售模式为互斥时，将新增额度默认分配给主产品(自选到期产品)
                if existence.sale_mode is SaleMode.mutex and increment > 0:
                    instance.allocated_amount = str(instance.allocated_amount + increment)
            else:
                # 将房贷宝产品销售模式置为互斥模式
                instance.sale_mode = SaleMode.mutex
                # 房贷宝产品创建子产品
                wrappeds = [ZhiwangWrappedProduct.create(instance, k) for k in (
                    WrapperKind.get_multi_by_raw_product_type(instance.product_type))]
                # 根据既定规则及当前销售模式进行额度分配
                raw_allocation, sub_allocation = coordinate_fdb_allocation(instance, wrappeds)
                adjust_products_allocation(SaleMode.mutex, instance, raw_allocation, sub_allocation)
        return instance

    @classmethod
    def clear_cache(cls, product_id):
        mc.delete(cls.cache_key.format(product_id=product_id))

    @classmethod
    def clear_cache_by_date(cls, date):
        mc.delete(cls.cache_ids_by_date_key.format(date=date))


class ZhiwangLadderDuedayProduct(ZhiwangProduct):

    annual_rate_layers = PropsItem('annual_rate_layers', [], list)
    last_due_date = PropsItem('last_due_date', None, date_type)

    @property
    def first_due_date(self):
        return self.due_date

    @property
    def final_due_date(self):
        return self.last_due_date or self.due_date

    @property
    def local_name(self):
        return u'%s~%s不定期产品' % (
            self.profit_period['min'].display_text, self.profit_period['max'].display_text)

    @cached_property
    def profit_period(self):
        min_value = (self.first_due_date - self.start_date).days
        max_value = (self.final_due_date - self.start_date).days
        return {'min': ProfitPeriod(min_value, 'day'),
                'max': ProfitPeriod(max_value, 'day')}

    @cached_property
    def profit_annual_rate(self):
        rates = [layer['annual_rate'] for layer in self.annual_rate_layers]
        return {'min': Decimal(min(rates)), 'max': Decimal(max(rates))}

    def get_annual_rate_by_date(self, day):
        assert isinstance(day, datetime.date)
        return Decimal(self.get_annual_rate_by_days((day - self.start_date).days))

    def get_annual_rate_by_days(self, days):
        matched_layers = [
            layer['annual_rate'] for layer in self.annual_rate_layers
            if days >= layer['min_days']]
        return matched_layers[-1] if matched_layers else 0


class ZhiwangFixedDuedayProduct(ZhiwangProduct):

    @property
    def local_name(self):
        return u'%s产品' % self.profit_period['min'].display_text

    @property
    def annual_rate_layers(self):
        return []

    @property
    def frozen_days(self):
        return (self.due_date - self.start_date).days

    @cached_property
    def profit_period(self):
        value = ProfitPeriod(self.frozen_days, 'day')
        return {'min': value, 'max': value}

    @cached_property
    def profit_annual_rate(self):
        return {'min': self.annual_rate, 'max': self.annual_rate}


def coordinate_fdb_allocation(raw_product, wrapped_products):
    """自动协调计算父子产品的各自分配额度"""
    from .wrapper_kind import newcomer

    raw_total = raw_product.total_amount
    sub_allocations = {k: 0 for k in wrapped_products}

    if raw_product.sale_mode is SaleMode.share:
        return raw_total, sub_allocations
    elif raw_product.sale_mode is SaleMode.mutex:
        for wp in wrapped_products:
            if wp.kind is newcomer:
                """
                if raw_total >= max(FDB_ALLOCATION_MILESTONE):
                    # 父产品总额大于分配里程碑最大值时，给予新手标最大分配额度
                    sub_allocations[wp] = max(NEWCOMER_ALLOCATION_LADDER)
                elif raw_total >= min(FDB_ALLOCATION_MILESTONE):
                    # 父产品总额小于分配里程碑最大值时但大于最小值时，给予新手标最小分配额度。
                    # 反之，新手标无额度。
                    sub_allocations[wp] = min(NEWCOMER_ALLOCATION_LADDER)
                else:
                    # XXX 暂时这样设置
                    sub_allocations[wp] = raw_total / 2
                """
                sub_allocations[wp] = raw_total
            else:
                raise ValueError('invalid wrapper kind %s' % wp.kind)
        return raw_total - sum(sub_allocations.values()), sub_allocations
    else:
        raise ValueError('invalid sale mode %s' % raw_product.sale_mode)


def adjust_products_allocation(new_sale_mode, raw_product, raw_product_allocation_amount=0,
                               wrapped_products_allocation_map={}):
    """
    配额分配原则：
    1. 父子产品新配额与已售额之差至少大于产品要求单笔最低购买额度
    2. 父子产品新配额相加为总额度
    3. 所有子产品都必须参与分配

    :param new_sale_mode: The new sale mode of raw and wrappeds.
    :param raw_product: The adjusting raw product instance.
    :param raw_product_allocated_amount: Optional when new_sale_mode is SaleMode.share.
                                         The allocated amount of raw product,
    :param wrapped_products_allocation_map: Optional when new_sale_mode is SaleMode.share.
                                            The detailed allocation of wrapped products.
                                            Should be format like {wproduct:Decimal(10000)}
    """
    from .wrapped_product import ZhiwangWrappedProduct
    from .order import ZhiwangOrder

    assert isinstance(new_sale_mode, SaleMode)
    assert raw_product.in_sale

    wrapped_products = ZhiwangWrappedProduct.get_multi_by_raw(raw_product.product_id)

    if new_sale_mode is SaleMode.share:
        # 当目标销售模式为共享时，将父子产品分配额度调整为0（即不受限制）
        raw_product.allocated_amount = 0
        for wp in wrapped_products:
            wp.allocated_amount = 0
    elif new_sale_mode is SaleMode.mutex:
        # 当目标销售模式为互斥时，重分配额度
        if not wrapped_products or set([w.id_ for w in wrapped_products]) != set(
                [w.id_ for w in wrapped_products_allocation_map]):
            # 无对应包装产品或包装产品分配表不包含所有包装产品情况时报错
            raise ImproperAmountAllocation()

        wrappeds_status = [allocation - ZhiwangOrder.get_wrapped_product_sold_amount(
            raw_product.product_id, wp.id_) < wp.min_amount for (
            wp, allocation) in wrapped_products_allocation_map.items()]

        if any(wrappeds_status):
            raise ImproperAmountAllocation()

        if raw_product_allocation_amount + sum(
                wrapped_products_allocation_map.values()) != raw_product.total_amount:
            raise ImproperAmountAllocation()

        raw_product.allocated_amount = str(raw_product_allocation_amount)
        for wp, allocation in wrapped_products_allocation_map.items():
            wp.allocated_amount = str(allocation)
    else:
        raise ValueError('%s is not a valid mode' % new_sale_mode)

    raw_product.sale_mode = new_sale_mode


PRODUCT_TYPE_CLS_MAP = {
    ZhiwangProduct.Type.fangdaibao: ZhiwangLadderDuedayProduct,
    ZhiwangProduct.Type.classic: ZhiwangFixedDuedayProduct,
}
