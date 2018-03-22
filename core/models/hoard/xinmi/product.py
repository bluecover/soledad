# coding: utf-8

import datetime
from decimal import Decimal
from core.models.utils.switch import xm_offline_switch

from enum import Enum
from babel.numbers import format_number

from jupiter.integration.bearychat import BearyChat
from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.types import unicode_type, date_type
from core.models.utils import round_half_up
from .errors import InvalidProductError
from ..providers import xmpay
from ..common import ProfitPeriod
from xmlib.consts import ProductType, PeriodUnit
from werkzeug.utils import cached_property

bearychat = BearyChat('savings_xm')


class SaleMode(Enum):
    share = 'SHARE'
    mutex = 'MUTEX'


def get_next_work_day(start_date=None):
    for x in range(1, 7):
        delta_day = datetime.timedelta(days=x)
        if start_date:
            date = start_date + delta_day
        else:
            date = datetime.datetime.now() + delta_day
        if date.weekday() not in [5, 6]:
            return date


def get_work_day(delta=0):
    # 0 表示当天
    now = datetime.datetime.now()
    if delta < 0:
        return now
    if delta > 5:
        raise InvalidProductError('起息日间隔太长!')
    for x in range(delta):
        weekdays = get_weekday_range(now)
        if weekdays > 0:
            now += datetime.timedelta(days=weekdays)
        else:
            now += datetime.timedelta(days=1)
    return now


def get_weekday_range(today):
    weekday = today.weekday()
    if weekday > 3:
        return 7 - weekday
    return 0


class XMProduct(PropsMixin):
    class Type(Enum):
        classic = ProductType.dingqi.value

    Type.classic.label = u'定期产品'

    # 存储
    table_name = 'hoard_xm_product'
    cache_key = 'hoard:xm:product:v1:{product_id}'

    # 新米配置
    name = PropsItem('name', '', unicode_type)
    annual_rate = PropsItem('annual_rate', 0, Decimal)
    min_amount = PropsItem('min_amount', 0, Decimal)
    max_amount = PropsItem('max_amount', 0, Decimal)
    total_amount = PropsItem('total_amount', 0, Decimal)
    sold_amount = PropsItem('sold_amount', 0, Decimal)
    # 可用配额
    quota = PropsItem('quota', 0, Decimal)
    start_date = PropsItem('start_date', None, date_type)
    due_date = PropsItem('due_date', None, date_type)
    description = PropsItem('description', u'', unicode_type)
    blank_contract_url = PropsItem('blank_contract_url', '')

    expire_period_unit = PropsItem('expire_period_unit', PeriodUnit.day.value)
    expire_period = PropsItem('expire_period', 0, int)

    # 本地配置
    is_taken_down = PropsItem('is_taken_down', False)
    allocated_amount = PropsItem('allocated_amount', 0, Decimal)
    mix_sale_mode = PropsItem('mix_sale_mode', SaleMode.share.value)

    # 订单金额增量
    increasing_step = 1

    # 所属合作方
    provider = xmpay

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
        return 'xm:prodcut:{product_id}'.format(product_id=self.product_id)

    @property
    def unique_product_id(self):
        return self.product_id

    @property
    def is_sold_out(self):
        # 先根据新米数据判断是否售罄
        if self.quota < self.min_amount:
            return True
        return False

    @property
    def is_either_sold_out(self):
        # 先根据新米数据判断是否售罄
        if self.is_sold_out:
            return True
        return False

    @property
    def in_sale(self):
        return self.start_sell_date <= datetime.date.today() < self.end_sell_date

    @property
    def in_stock(self):
        # 是否可售状态决定于以下几种情况
        # 1. 根据好规划需求进行强制售罄
        # 2. 新米抢占额度导致条件1尚未满足时发生接口报告无债权可卖

        if self.is_sold_out or self.is_taken_down:
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

    @classmethod
    def get_product_annotations(cls, coupons, product):
        annotations = []
        matched_coupons = [c for c in coupons.deduplicated_available_coupons
                           if c.is_available_for_product(product)]
        if matched_coupons:
            annotations.append(u'有礼券可用')
            return annotations

    @classmethod
    def get_multi(cls, ids):
        # 过滤掉测试用的产品
        filter_products = ['2015122217504424733']
        if not xm_offline_switch.is_enabled:
            filter_products.append('2016022914051608191')
            filter_products.append('2016022914371312693')
            filter_products.append('2016032418441063493')
        return [cls.get(id_) for id_ in ids if id_ not in filter_products]

    @classmethod
    def get_all(cls):
        """获取所有可展示产品"""
        ids = cls.get_ids_by_date(datetime.date.today())
        return cls.get_multi(ids)

    @classmethod
    def get_ids_by_date(cls, date):
        assert isinstance(date, datetime.date)
        sql = ('select product_id from {.table_name} '
               'where start_sell_date <= %s and end_sell_date > %s '
               'order by creation_time desc').format(cls)
        rs = db.execute(sql, (date, date))
        return [r[0] for r in rs]

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
    def update_table(cls, pid, ptype, start_sell_date, end_sell_date):
        sql = ('insert into {.table_name} (product_id, product_type, start_sell_date, '
               'end_sell_date, creation_time) values (%s, %s, %s, %s, %s) '
               'on duplicate key update product_id=values(product_id), '
               'start_sell_date=values(start_sell_date), '
               'end_sell_date=values(end_sell_date)').format(cls)

        params = (pid, ptype.value, start_sell_date, end_sell_date, datetime.datetime.now())
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(pid)

    @classmethod
    def add(cls, product_info):
        pid = product_info.pop('product_id')
        ptype = product_info.pop('category')

        # 默认上架时间为开售时间。（上下架时间很可能不会传回来）
        start_sell_date = datetime.datetime.strptime(product_info.get('open_time'),
                                                     '%Y-%m-%d %H:%M:%S')
        end_sell_date = datetime.datetime.strptime(product_info.get('expire_date'),
                                                   '%Y-%m-%d %H:%M:%S')
        # 默认下架时间为开售1年后
        if not end_sell_date:
            end_sell_date = datetime.datetime.now() + datetime.timedelta(days=365)

        start_sell_date = start_sell_date.date()
        end_sell_date = end_sell_date.date()

        # 判断产品类型是否被支持
        try:
            ptype = cls.Type(ptype)
        except ValueError:
            raise InvalidProductError(ptype)

        quota = product_info.pop('quota', 0)
        product_name = product_info.pop('name', u'未知')

        # 将产品基本属性记入数据库
        existence = cls.get(pid)
        original_quota = 0
        if existence:
            original_quota = existence.quota
            checks = any([
                existence.start_sell_date != start_sell_date,
                existence.end_sell_date != end_sell_date,
            ])
            if checks:
                cls.update_table(pid, ptype, start_sell_date, end_sell_date)
                if existence.quota == quota:
                    return existence
        else:
            cls.update_table(pid, ptype, start_sell_date, end_sell_date)
            if bearychat.configured:
                bearychat.say(u'我们又加新产品啦 **{}** 额度: **{}** :clap:，请周知。'.format(
                    product_name, format_number(quota, locale='en_US')))

        instance = cls.get(pid)

        # 更新产品最新参数
        instance.product_id = pid
        instance._product_type = ptype.value
        instance.name = product_name
        instance.annual_rate = float(round_half_up(product_info.pop('return_rate', 0) * 100, 1))
        # 默认最小投资额为1元
        min_amount = product_info.pop('min_amount', 1)
        instance.min_amount = min_amount if min_amount > 1 else 1.00
        instance.max_amount = product_info.pop('max_amount', 0)

        instance.quota = quota
        instance.total_amount = product_info.pop('total_amount', 0)
        instance.sold_amount = product_info.pop('sold_amount', 0)

        # 临时性起息日跳过周六日
        effect_day = product_info.pop('effect_day', -1)
        effect_day_unit = product_info.pop('effect_day_unit', 1)
        if effect_day_unit != 1:
            raise InvalidProductError('未支持的起息日单位!')
        if effect_day > 0:
            start_date = get_work_day(delta=effect_day)
        else:
            start_date = get_next_work_day()
        instance.start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        instance.due_date = product_info.pop('expire_date', None)
        instance.description = product_info.pop('remark', u'')
        instance.blank_contract_url = product_info.pop('blank_contract_url', '')

        instance.expire_period_unit = product_info.pop('expire_period_unit', PeriodUnit.day.value)
        instance.expire_period = product_info.pop('expire_period', 0)

        # 当销售周期内产品额度不足时，发出BC通知
        if existence:
            if bearychat.configured:
                quota_txt = format_number(quota, locale='en_US')
                original_quota_txt = format_number(original_quota, locale='en_US')
                if quota < instance.min_amount:
                    txt = u'最近一笔：**￥{}**，当前额度：**￥{}**'.format(original_quota_txt, quota_txt)
                    attachment = bearychat.attachment(title=None,
                                                      text=txt,
                                                      color='#ffa500',
                                                      images=[])
                    bearychat.say(u'产品 **{}** **售罄** 啦，正在尝试释放未支付订单，请周知。'.format(
                        product_name), attachments=[attachment])
                if quota > original_quota + int(instance.min_amount):
                    txt = u'更新前额度：**￥{}**, 当前额度：**￥{}**'.format(original_quota_txt, quota_txt)
                    attachment = bearychat.attachment(title=None, text=txt, color='#a5ff00',
                                                      images=[])
                    bearychat.say(u'产品 **{}** **额度** 增加啦 :clap:，请周知。'.format(product_name),
                                  attachments=[attachment])

        return instance

    @classmethod
    def clear_cache(cls, product_id):
        mc.delete(cls.cache_key.format(product_id=product_id))


class XMFixedDuedayProduct(XMProduct):
    @property
    def local_name(self):
        return u'%s产品' % self.profit_period['min'].display_text

    @property
    def annual_rate_layers(self):
        return []

    @property
    def frozen_days(self):
        if PeriodUnit(self.expire_period_unit) is PeriodUnit.day:
            return self.expire_period
        if PeriodUnit(self.expire_period_unit) is PeriodUnit.month:
            return self.expire_period * 30

    @cached_property
    def profit_period(self):
        value = ProfitPeriod(self.frozen_days, 'day')
        return {'min': value, 'max': value}

    @cached_property
    def profit_annual_rate(self):
        return {'min': self.annual_rate, 'max': self.annual_rate}


PRODUCT_TYPE_CLS_MAP = {
    XMProduct.Type.classic: XMFixedDuedayProduct,
}
