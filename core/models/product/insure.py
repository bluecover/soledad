# -*- coding: utf-8 -*-

from core.models.product.base import ProductBase

from core.models.mixin.props import PropsItem

from core.models.product.consts import INSURE_TYPE, INSURE_NAME


class Insure(ProductBase):
    '''
    保险
    '''

    duration = PropsItem('duration', '')  # 保险期间
    pay_duration = PropsItem('pay_duration', '')  # 缴费期限
    insure_duty = PropsItem('insure_duty', '')  # 保险责任
    throng = PropsItem('throng', '')  # 适合人群
    prospect = PropsItem('prospect', '')  # 保费预估

    kind = 'insure'
    _table = 'product_insure'

    def __repr__(self):
        return '<Product Insure id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @classmethod
    def gets_by_type(cls, type):
        funds = super(Insure, cls).get_all(limit=1000)
        if not funds:
            return []
        if type and str(type) not in INSURE_TYPE.values():
            return []
        return filter(lambda x: x.type == str(type), funds)

    @property
    def type_name(self):
        for name, value in INSURE_TYPE.items():
            if self.type == value:
                return INSURE_NAME.get(name)
        return '未命名'
