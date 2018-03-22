# -*- coding: utf-8 -*-

from core.models.product.base import ProductBase
from core.models.mixin.props import PropsItem

from core.models.product.consts import FUND_TYPE, FUND_NAME


class Fund(ProductBase):
    '''
    基金
    '''

    kind = 'fund'
    _table = 'product_fund'

    code = PropsItem('code', '')  # 基金代码
    found_date = PropsItem('found_date', '')  # 成立日期
    index = PropsItem('index', '')  # 跟踪指数
    risk = PropsItem('risk', '')  # 风险

    manager = PropsItem('manager', '')  # 基金经理
    year_rate = PropsItem('year_rate', '')  # 近一年涨幅

    nickname = PropsItem('nickname', '')  # 别名

    def __repr__(self):
        return '<Product fund id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @classmethod
    def gets_by_type(cls, type):
        funds = super(Fund, cls).get_all(limit=1000)
        if not funds:
            return []
        if type and str(type) not in FUND_TYPE.values():
            return []
        return filter(lambda x: x.type == str(type), funds)

    @property
    def type_name(self):
        for name, value in FUND_TYPE.items():
            if self.type == value:
                return FUND_NAME.get(name)
        return '未命名'

    @classmethod
    def gets_by_risk(cls, risk):
        if risk not in ('高', '中', '低'):
            return []
        funds = super(Fund, cls).get_all(limit=1000)
        if not funds:
            return []
        return filter(lambda x: x.risk == risk, funds)
