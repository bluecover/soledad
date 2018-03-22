# -*- coding: utf-8 -*-

from enum import Enum
from decimal import Decimal


class FeeRate(Enum):
    thirty_days = Decimal('0.065')
    three_month = Decimal('0.07')
    one_year = Decimal('0.1')
    wallet = Decimal('0.035')
    current_interest = Decimal('0.0035')


class IncomeDiagnosis(Enum):
    def __new__(cls, name, factor, description=''):
        instance = object.__new__(cls)
        instance._value_ = name
        instance.factor = factor
        instance.description = description
        return instance

    __ordered__ = 'step1 step2 step3 step4'
    step1 = ('step1', 2.5, '远高于当地平均收入水平。加上理财，你离富人只有半步之遥')
    step2 = ('step2', 1.5, '已经高于当地平均收入水平，只要稍加理财生活就会更轻松哦。')
    step3 = ('step3', 1, '略高于当地平均收入水平，吓死宝宝了，赶紧理财给自己加薪。')
    step4 = ('step4', 0, '低于当地平均收入水平，现阶段增加收入、开源节流是你的重点。')
