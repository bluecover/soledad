# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from collections import namedtuple
from decimal import Decimal

from .product import ZhiwangProduct
from .wrapped_product import ZhiwangWrappedProduct
from ..common import ProfitPeriod


class WrapperKind(namedtuple('WrapperKind', ['id_', 'name', 'raw_product_type',
                                             'wrapped_product_type', 'annual_rate',
                                             'frozen_days', 'limit'])):
    """
    The class that represents the kind of local re-assembled product.
    """

    storage = {}

    def __init__(self, id_, name, raw_product_type, wrapped_product_type,
                 annual_rate, frozen_days, limit):
        self.storage[int(id_)] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(int(id_))

    @classmethod
    def get_multi_by_raw_product_type(cls, raw_product_type):
        return [k for k in cls.get_all() if k.raw_product_type is raw_product_type]

    @classmethod
    def get_all(cls):
        return [cls.get(kind_id) for kind_id in cls.storage]


newcomer = WrapperKind(
    id_=1,
    name=u'新手标产品',
    raw_product_type=ZhiwangProduct.Type.fangdaibao,
    wrapped_product_type=ZhiwangWrappedProduct.Type.newcomer,
    annual_rate=Decimal(10.0),
    frozen_days=ProfitPeriod(25, 'day'),
    limit=(1000, 10000),
)
