# coding: utf-8

from uuid import UUID
from decimal import Decimal

from arrow import Arrow

from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.utils.types import arrow_type, unicode_type
from .common import ProfitPeriod
from .providers import yirendai


class YixinService(PropsMixin):
    """The entity of Yixin P2P services."""

    table_name = 'hoard_yixin_service'
    cache_key = 'hoard:yixin:service:{uuid}'

    amount = PropsItem('amount', None, Decimal)
    begin_sale_time = PropsItem('begin_sale_time', None, arrow_type)
    exist_amount = PropsItem('exist_amount', None, Decimal)
    expected_income = PropsItem('expected_income', None, Decimal)
    for_new_user = PropsItem('for_new_user')
    frozen_time = PropsItem('frozen_time')
    increment = PropsItem('increment', None, Decimal)
    invest_max_amount = PropsItem('invest_max_amount', None, Decimal)
    invest_min_amount = PropsItem('invest_min_amount', None, Decimal)
    is_home_page = PropsItem('is_home_page')
    keyword = PropsItem('keyword')
    p2pservice_name = PropsItem('p2pservice_name', None, unicode_type)
    p2pservice_no = PropsItem('p2pservice_no', None, unicode_type)
    p2pservice_type = PropsItem('p2pservice_type', None, unicode_type)
    product_id = PropsItem('product_id', None, unicode_type)
    product_sub_id = PropsItem('product_sub_id', None, UUID)
    sale_status = PropsItem('sale_status')
    server_time = PropsItem('server_time', None, arrow_type)
    service_sub_image_url = PropsItem('service_sub_image_url')

    sell_out = PropsItem('sell_out', False)
    take_down = PropsItem('take_down', False)
    is_hidden = PropsItem('is_hidden', False)

    # 购买增加
    increasing_step = 1000

    def __init__(self, uuid, creation_time):
        self.uuid = UUID(uuid)
        self.creation_time = creation_time

    def get_uuid(self):
        return 'yixin:service:{uuid}'.format(uuid=self.uuid.hex)

    def get_db(self):
        return 'hoard'

    @classmethod
    def get_all(cls):
        sql = ('select uuid from {.table_name} '
               'order by creation_time desc').format(cls)
        uuid_list = [rs[0] for rs in db.execute(sql)]
        return list(map(cls.get, uuid_list))

    @classmethod
    @cache(cache_key)
    def get(cls, uuid):
        if isinstance(uuid, UUID):
            raise ValueError('Please "YixinService.get(uuid.hex)" instead.')

        sql = ('select uuid, creation_time from {.table_name} '
               'where uuid = %s').format(cls)
        params = (uuid,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @property
    def start_date(self):
        return None

    @classmethod
    def iter_by_period(cls, period):
        services = cls.get_all()
        for service in services:
            if service.frozen_time == int(period):
                yield service

    @classmethod
    def add(cls, service_info):
        """Creates or overrides a service record.

        :param service_info: instance of :class:`yxlib.structures.ServiceInfo`.
        """
        data = dict(service_info.typed())
        uuid = data.pop('id').hex

        sql = ('insert into {.table_name} (uuid) values (%s) '
               'on duplicate key update uuid = %s').format(cls)
        params = (uuid, uuid)

        db.execute(sql, params)
        db.commit()

        cls.clear_cache(uuid)
        instance = cls.get(uuid)

        for name, value in data.iteritems():
            if not isinstance(getattr(cls, name, None), PropsItem):
                raise ValueError('%s is not PropsItem' % name)
            if isinstance(value, UUID):
                value = value.hex
            if isinstance(value, Arrow):
                value = value.isoformat()
            if isinstance(value, Decimal):
                value = str(value)
            setattr(instance, name, value)

        return instance

    @classmethod
    def clear_cache(cls, uuid):
        if isinstance(uuid, UUID):
            uuid = uuid.hex
        mc.delete(cls.cache_key.format(uuid=uuid))

    @property
    def in_sale(self):
        # 产品是否在售
        return self.sale_status == 2

    @property
    def in_stock(self):
        if self.sell_out or self.take_down:
            return
        return self.in_sale

    # For mobile API
    # TODO (tonyseek) make a wrapper to unify the API of zhiwang / yixin

    provider = yirendai

    @property
    def profit_period(self):
        return {'min': ProfitPeriod(int(self.frozen_time), 'month'),
                'max': ProfitPeriod(int(self.frozen_time), 'month')}

    @property
    def annual_rate_layers(self):
        return []

    @property
    def activity_type(self):
        return ''

    @property
    def wrapped_product_id(self):
        return ''

    @property
    def min_amount(self):
        return self.invest_min_amount

    @property
    def max_amount(self):
        return self.invest_max_amount

    @property
    def profit_annual_rate(self):
        return {'min': Decimal(int(self.expected_income)),
                'max': Decimal(int(self.expected_income))}

    @property
    def unique_product_id(self):
        return self.uuid.hex

    @property
    def is_sold_out(self):
        return self.sell_out or self.sale_status != 2

    @property
    def is_taken_down(self):
        return self.take_down
