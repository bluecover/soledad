# coding: utf-8

from collections import namedtuple


class ProfitPeriod(namedtuple('ProfitPeriod', 'value unit')):
    """攒钱封闭期.

    :param value: 封闭期数值
    :param unit: 封闭期单位, 可能为 ``"month"`` 或 ``"day"``
    """

    def __init__(self, value, unit):
        assert unit in ('month', 'day')

    def __eq__(self, other):
        if self.unit != other.unit:
            return NotImplemented
        return self.value == other.value

    def __gt__(self, other):
        if self.unit != other.unit:
            return NotImplemented
        return self.value > other.value

    @property
    def display_unit(self):
        return {'day': u'天', 'month': u'个月'}[self.unit]

    @property
    def display_text(self):
        return u'%d %s' % (self.value, self.display_unit)
