# coding: utf-8

import decimal

from weakref import WeakValueDictionary

from core.models.base import EntityModel
from .regulation import (
    CouponRegulation, AnnualRateSupplementRegulation, QuotaDeductionRegulation)


class CouponKind(EntityModel):

    storage = WeakValueDictionary()

    def __init__(self, id_, regulation):
        assert isinstance(regulation, CouponRegulation)

        if id_ in self.storage:
            raise ValueError('id %r has been used' % id_)

        self.id_ = id_
        # 礼券规则，管理获益方式与产品、订单的适用性检查
        self.regulation = regulation
        self.storage[id_] = self

    @property
    def name(self):
        return self.regulation.kind.value

    @property
    def display_text(self):
        """礼券文案"""
        return ''.join([self.regulation.display_usage_requirement, self.regulation.display_benefit])

    @classmethod
    def get(cls, id_):
        return cls.storage.get(int(id_))

    @classmethod
    def get_all(cls):
        return [cls.get(kid) for kid in cls.storage]


# 满减类
deduction_1000_cut_5 = CouponKind(
    id_=1001,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('1000'), deduct_quota=decimal.Decimal('5')),
)

deduction_5000_cut_30 = CouponKind(
    id_=1002,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('5000'), deduct_quota=decimal.Decimal('30')),
)

deduction_30000_cut_180 = CouponKind(
    id_=1003,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('30000'), deduct_quota=decimal.Decimal('180')),
)

deduction_50000_cut_260 = CouponKind(
    id_=1004,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('50000'), deduct_quota=decimal.Decimal('260')),
)

deduction_10000_cut_10 = CouponKind(
    id_=1005,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('10000'), deduct_quota=decimal.Decimal('10')),
)

deduction_20000_cut_20 = CouponKind(
    id_=1006,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('20000'), deduct_quota=decimal.Decimal('20')),
)

deduction_30000_cut_60 = CouponKind(
    id_=1007,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('30000'), deduct_quota=decimal.Decimal('60')),
)

deduction_30000_cut_40 = CouponKind(
    id_=1008,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('30000'), deduct_quota=decimal.Decimal('40')),
)

deduction_50000_cut_80 = CouponKind(
    id_=1009,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('50000'), deduct_quota=decimal.Decimal('80')),
)

deduction_20000_cut_40 = CouponKind(
    id_=1010,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('20000'), deduct_quota=decimal.Decimal('40')),
)

deduction_50000_cut_100 = CouponKind(
    id_=1011,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('50000'), deduct_quota=decimal.Decimal('100')),
)

deduction_500_cut_10 = CouponKind(
    id_=1012,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('500'), deduct_quota=decimal.Decimal('10')),
)

deduction_1000_cut_20 = CouponKind(
    id_=1013,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('1000'), deduct_quota=decimal.Decimal('20')),
)

deduction_5000_cut_100 = CouponKind(
    id_=1014,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('5000'), deduct_quota=decimal.Decimal('100')),
)

deduction_20000_cut_80 = CouponKind(
    id_=1015,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('20000'), deduct_quota=decimal.Decimal('80')),
)

deduction_50000_cut_115 = CouponKind(
    id_=1016,
    regulation=QuotaDeductionRegulation(
        fulfill_quota=decimal.Decimal('50000'), deduct_quota=decimal.Decimal('115')),
)


# 加息类
rate_2_permillage = CouponKind(
    id_=2000,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.2')),
)

rate_3_permillage = CouponKind(
    id_=2001,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.3')),
)

rate_5_permillage = CouponKind(
    id_=2002,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.5')),
)

rate_6_permillage = CouponKind(
    id_=2003,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.6')),
)
rate_8_permillage = CouponKind(
    id_=2004,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.8')),
)
rate_7_permillage = CouponKind(
    id_=2005,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.7')),
)
rate_4_permillage = CouponKind(
    id_=2006,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.4')),
)
rate_9_permillage = CouponKind(
    id_=2009,
    regulation=AnnualRateSupplementRegulation(supply_rate=decimal.Decimal('0.38')),
)
