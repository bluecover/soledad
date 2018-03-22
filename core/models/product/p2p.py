# -*- coding: utf-8 -*-

from core.models.product.base import ProductBase

from core.models.mixin.props import PropsItem


class P2P(ProductBase):
    '''
    P2P
    '''

    kind = 'p2p'
    _table = 'product_p2p'

    year_rate = PropsItem('year_rate', 0)  # 预期年化收益率
    pay_return_type = PropsItem('pay_return_type', '')  # 返还方式
    deadline = PropsItem('deadline', '')  # 投资期限
    min_money = PropsItem('min_money', '')  # 购买起点
    protect = PropsItem('protect', '')  # 保障

    def __repr__(self):
        return '<Product P2P id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @property
    def type_name(self):
        return 'P2P'
