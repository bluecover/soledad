# -*- coding: utf-8 -*-

from datetime import datetime

from warnings import warn
from MySQLdb import IntegrityError
from libs.db.store import db
from libs.cache import mc, cache

from core.models.product.base import ProductBase
from core.models.product.consts import PRODUCT_STATUS

_PRODUCT_DEBT_CACHE_PRFIX = 'product:debt:'

PRODUCT_DEBT_CACHE_KEY = _PRODUCT_DEBT_CACHE_PRFIX + '%s'


class Debt(ProductBase):
    '''
    国债
    '''

    kind = 'debt'
    _table = 'product_debt'

    def __init__(self, id, name, type, risk_rank, rate, min_money,
                 duration, pay_type, status, create_time, update_time):
        self.id = str(id)
        self.name = name
        self.type = str(type)
        self.risk_rank = str(risk_rank)
        self.rate = rate
        self.min_money = min_money
        self.duration = duration  # 以天为基础单位
        self.pay_type = str(pay_type)
        self.status = str(status)
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Product debt id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @classmethod
    @cache(PRODUCT_DEBT_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, name, `type`, risk_rank, rate, '
                        'min_money, duration, pay_type, status, '
                        'create_time, update_time from product_debt '
                        'where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, name, type, risk_rank, rate, min_money,
            duration, pay_type, status, rec_reason, rec_rank, link, phone):
        try:
            id = db.execute('insert into product_debt '
                            '(name, `type`, risk_rank, rate, min_money, '
                            'duration, pay_type, status, create_time) '
                            'values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                            (name, type, risk_rank, rate, min_money,
                             duration, pay_type, status, datetime.now()))
            if id:
                db.commit()
                p = cls.get(id)
                p.rec_reason = rec_reason
                p.rec_rank = rec_rank
                p.link = link
                p.phone = phone
                return p
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert product debt failed')

    def update(self, name, type, risk_rank, rate, min_money,
               duration, pay_type, rec_reason, rec_rank, link, phone):
        db.execute('update product_debt set '
                   'name=%s, `type`=%s, duration=%s, '
                   'risk_rank=%s, rate=%s, min_money=%s, '
                   'pay_type=%s where id=%s',
                   (name, type, duration, risk_rank,
                    rate, min_money, pay_type, self.id))
        db.commit()
        self.rec_reason = rec_reason
        self.rec_rank = rec_rank
        self.link = link
        self.phone = phone
        self.clear_cache()
        return Debt.get(self.id)

    def delete(self):
        db.execute('update product_debt set status=%s where id=%s',
                   (PRODUCT_STATUS.OFF, self.id))
        db.commit()
        self.clear_cache()
        self.status = PRODUCT_STATUS.OFF

    def clear_cache(self):
        mc.delete(PRODUCT_DEBT_CACHE_KEY % self.id)
        self._clear_all_cache()

    @property
    def type_name(self):
        return '国债'
