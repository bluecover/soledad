# coding: utf-8

'''
insure class
'''

from core.models.insurance.insurance import Insurance
from core.models.insurance.age import Age


class Order(object):
    table_name = 'insurance_order'

    def __init__(self, user_id, order_id, package_id, insurance_id):
        self.user_id = user_id
        self.order_id = order_id
        self.package_id = package_id
        self.insurance_id = insurance_id
        self._age = None
        self._coverage = 10
        self._fee = 0
        self._will = 0

    @property
    def will(self):
        return self._will

    @will.setter
    def will(self, value):
        self._will = value

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, birthday):
        self._age = Age(birthday)

    @property
    def insurance(self):
        return Insurance.get(self.insurance_id)

    def rate(self, **kwargs):
        self.insurance.age = self.age
        return self.insurance.get_fee(self.package_id, **kwargs)

    def ins_sub_title(self):
        return self.insurance.get_ins_sub_title(self.package_id)

    @property
    def coverage(self):
        return self._coverage

    @coverage.setter
    def coverage(self, value):
        self._coverage = value

#
#    @classmethod
#    def add(cls, user_id, order_id, package_id, insurance_id, kind):
#        sql = ('insert into {.table_name}'
#               ' ( user_id, order_id, package_id, insurance_id, '
#               ' rate', 'fee', 'coverage,'
#               ' create_time, update_time)'
#               ' values ( %s, %s, %s, %s, %s, %s)').format(cls)
#        params = (user_id, order_id, package_id, insurance_id, kind,
#                  datetime.now(), datetime.now())
#        db.execute(sql, params)
#        db.commit()
#
# 根据保险代码获取保险实例
#    @classmethod
#    def get(cls, insurance_id):
#        sql = ('select user_id, order_id, package_id, insurance_id, kind '
#               ' from {.table_name}  where insurance_id = %s').format(cls)
#        param = insurance_id
#        rs = db.execute(sql, param)
#        return cls(*rs[0])
