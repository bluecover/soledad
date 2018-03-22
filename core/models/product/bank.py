# -*- coding: utf-8 -*-

'''
银行理财产品
'''


from datetime import datetime
from warnings import warn
from MySQLdb import IntegrityError
from libs.db.store import db
from libs.cache import mc, cache

from core.models.product.base import ProductBase
from core.models.product.consts import PRODUCT_STATUS

_PRODUCT_BANK_CACHE_PRFIX = 'product:bank:'

PRODUCT_BANK_CACHE_KEY = _PRODUCT_BANK_CACHE_PRFIX + '%s'


class Bank(ProductBase):
    '''
    银行理财产品
    '''

    kind = 'bank'
    _table = 'product_bank_financial'

    def __init__(self, id, name, type, risk_rank, earning, min_money,
                 start_time, end_time, status, create_time, update_time):
        self.id = str(id)
        self.name = name
        self.type = str(type)
        self.risk_rank = str(risk_rank)
        self.earning = earning
        self.min_money = min_money
        self.start_time = start_time
        self.end_time = end_time
        self.status = str(status)
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Product bank id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @classmethod
    @cache(PRODUCT_BANK_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, name, `type`, risk_rank,'
                        'earning, min_money, start_time,'
                        'end_time, status, create_time, update_time '
                        ' from product_bank_financial where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, name, type, risk_rank, earning, min_money,
            start_time, end_time, status, rec_reason,
            rec_rank, link, phone):
        try:
            id = db.execute('insert into product_bank_financial '
                            '(name, `type`, risk_rank, earning, '
                            'min_money, start_time,'
                            'end_time, status, create_time) '
                            'values(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                            (name, type, risk_rank, earning, min_money,
                             start_time, end_time, status, datetime.now()))
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
            warn('insert product bank failed')

    def update(self, name, type, risk_rank, earning, min_money,
               start_time, end_time, rec_reason, rec_rank, link, phone):
        db.execute('update product_bank_financial set '
                   'name=%s, `type`=%s, risk_rank=%s, '
                   'earning=%s, min_money=%s, start_time=%s,'
                   'end_time=%s where id=%s', (name, type, risk_rank,
                                               earning, min_money,
                                               start_time, end_time,
                                               self.id))
        db.commit()
        self.rec_reason = rec_reason
        self.rec_rank = rec_rank
        self.link = link
        self.phone = phone
        self.clear_cache()
        return Bank.get(self.id)

    def delete(self):
        db.execute('update product_bank_financial set status=%s where id=%s',
                   (PRODUCT_STATUS.OFF, self.id))
        db.commit()
        self.clear_cache()
        self.status = PRODUCT_STATUS.OFF

    def clear_cache(self):
        mc.delete(PRODUCT_BANK_CACHE_KEY % self.id)
        self._clear_all_cache()

    @property
    def type_name(self):
        return '银行理财'
