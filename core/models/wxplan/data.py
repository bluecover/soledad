# -*- coding: utf-8 -*-
from decimal import Decimal

from enum import Enum

from core.models.base import EntityModel
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.wxplan.consts import FeeRate
from core.models.utils import round_half_up
from libs.db.store import db
from libs.cache import cache, mc
from datetime import datetime


class PlanData(EntityModel):
    """
        小规划用户数据
    """
    table_name = 'wxplan_plan'
    cache_key_plan = 'wxplan:plan:{id_}'
    cache_key_plan_user = 'wxplan:plan:user:{id_}'

    class Meta:
        repr_attr_names = ['user_id', 'gender', 'age', 'province_code']

    def __init__(self, id_, gender, user_id, age, province_code, stock, rent, mpayment, insurance,
                 tour, has_children, savings, mincome, create_time, update_time):
        """
        :param gender: 性别(0:男，1:女)
        :type gender: int(1),
        :param age:年龄(1-200) - [18,50]
        :type age: int(3)
        :param province_code:省份
        :type province_code:string
        :param stock:股票基金
        :type stock:int
        :param rent:房租（默认：－1表示无房租，房租：>0为承担房租额，）
        :type rent:int
        :param mpayment:月供
        :type mpayment:float
        :param insurance:保险（－1 无保险，1有保险）
        :type insurance:float
        :param tour:旅游（－1 无旅游，>－1 旅游费用）
        :type tour:float
        :param has_children:是否有儿女(-1 无儿女，>－1 子女个数）
        :type has_children:int
        :param savings:积蓄(-1 无积蓄，>-1 积蓄额）
        :type savings:float
        :param mincome:税后月收入(-1 无收入, >-1 月收入)
        :type mincome:float
        """
        self.id_ = str(id_)
        self.gender = 1 if gender > 0 else 0
        self.user_id = str(user_id)
        self.age = age
        self.province_code = province_code
        self.stock = stock
        self.rent = rent
        self.mpayment = mpayment
        self.insurance = insurance
        self.tour = tour
        self.has_children = has_children
        self.savings = savings
        self.mincome = mincome
        self.create_time = create_time
        self.update_time = update_time

    @classmethod
    def get(cls, plan_id):
        return cls.get_by_id(plan_id)

    @classmethod
    @cache(cache_key_plan)
    def get_by_id(cls, id_):
        sql = ('select id, gender, user_id, age, province_code, stock, rent, mpayment, insurance, '
               'tour, has_children, savings, mincome, create_time, update_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)

        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_plan_user)
    def get_id_by_user_id(cls, id_):
        sql = ('select id from {0} where user_id=%s').format(cls.table_name)
        rs = db.execute(sql, (id_,))
        return rs[0][0] if rs else None

    @classmethod
    def get_by_user_id(cls, user_id):
        id_ = cls.get_id_by_user_id(user_id)
        return cls.get(id_) if id_ else None

    @classmethod
    def add(cls, gender, user_id, age, province_code, stock, rent, mpayment, insurance, tour,
            has_children, savings, mincome):
        sql = ('insert into {0} (gender, user_id, age, province_code, stock, '
               'rent, mpayment, insurance, tour, has_children, savings, mincome,'
               'create_time) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)').format(
            cls.table_name)

        params = (gender, user_id, age, province_code, stock, rent, mpayment, insurance, tour,
                  has_children, savings, mincome, datetime.now())

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_user_id(user_id)
        return cls.get(id_)

    @classmethod
    def update(cls, id_, gender, user_id, age, province_code, stock, rent, mpayment, insurance,
               tour, has_children, savings, mincome):
        sql = ('update {0} set gender=%s, user_id=%s, age=%s, province_code=%s, stock=%s, rent=%s, '
               'mpayment=%s, insurance=%s, tour=%s, has_children=%s, savings=%s, mincome=%s, '
               'update_time=%s  where id=%s').format(cls.table_name)
        params = (gender, user_id, age, province_code, stock, rent, mpayment, insurance,
                  tour, has_children, savings, mincome, datetime.now(), id_)
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_user_id(user_id)
        return cls.get(id_)

    @classmethod
    def add_or_update(cls, gender, user_id, age, province_code, stock, rent, mpayment,
                      insurance, tour, has_children, savings, mincome):
        instance = cls.get_by_user_id(user_id)
        if instance:
            return cls.update(instance.id_, gender, user_id, age, province_code, stock, rent,
                              mpayment, insurance, tour, has_children, savings, mincome)
        return cls.add(gender, user_id, age, province_code, stock, rent, mpayment, insurance, tour,
                       has_children, savings, mincome)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key_plan.format(id_=id_))

    @classmethod
    def clear_cache_by_user_id(cls, user_id):
        mc.delete(cls.cache_key_plan_user.format(id_=user_id))

    def to_dict(self):
        return {'gender': self.gender, 'age': self.age, 'province_code': self.province_code,
                'stock': self.stock, 'rent': self.rent, 'mpayment': self.mpayment,
                'insurance': self.insurance, 'tour': self.tour, 'has_children': self.has_children,
                'savings': self.savings, 'mincome': self.mincome}

    @classmethod
    def from_dict(cls, d):
        if not d:
            return None
        if not isinstance(d, dict):
            return None
        white_list = ['id_', 'user_id', 'gender', 'age', 'province_code', 'stock', 'rent',
                      'mpayment', 'insurance', 'tour', 'has_children', 'savings', 'mincome',
                      'create_time', 'update_time']
        new_dict = {}
        for k in white_list:
            new_dict[k] = d.get(k)
        return cls(**new_dict)

    def assign_to_user(self, user_id):
        return self.add_or_update(self.gender, user_id, self.age, self.province_code,
                                  self.stock, self.rent, self.mpayment, self.insurance, self.tour,
                                  self.has_children, self.savings, self.mincome)


class ProvinceSalary(EntityModel):
    """
        小规划全国各省市平均收支信息
    """
    table_name = 'wxplan_salary'
    cache_key_salary = 'wxplan:salary:{id_}'
    cache_key_salary_province = 'wxplan:salary:province:{id_}'

    class Meta:
        repr_attr_names = ['id_', 'code', 'province', 'income', 'expenditure']

    def __init__(self, id_, code, province, income, expenditure):
        self.id_ = str(id_)
        self.code = code
        self.province = province
        self.income = income
        self.expenditure = expenditure

    @classmethod
    def get(cls, salary_id):
        return cls.get_by_id(salary_id)

    @classmethod
    @cache(cache_key_salary)
    def get_by_id(cls, id_):
        sql = ('select id, code, province, income, expenditure '
               'from {0} where id=%s').format(cls.table_name)
        rs = db.execute(sql, (id_,))
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_salary_province)
    def get_id_by_province_code(cls, id_):
        rs = db.execute('select id '
                        'from {0} where code=%s'.format(cls.table_name), (id_,))

        return rs[0][0] if rs else None

    @classmethod
    def get_by_province_code(cls, province_code):
        id_ = cls.get_id_by_province_code(province_code)
        return cls.get(id_) if id_ else None

    @classmethod
    def add(cls, code, province, income, expenditure):
        sql = ('INSERT INTO {0} '
               '(code, province, income, expenditure) '
               'values(%s, %s, %s, %s)').format(cls.table_name)
        params = (code, province, income, expenditure)

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_province_code(code)
        return cls.get(id_)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key_salary.format(id_=id_))

    @classmethod
    def clear_cache_by_province_code(cls, code):
        mc.delete(cls.cache_key_salary_province.format(id_=code))

    @classmethod
    def has_code(cls, code):
        return cls.get_by_province_code(province_code=code) is not None


class Report(EntityModel, PropsMixin):
    """
        小规划用户报告
    """
    table_name = 'wxplan_report'
    cache_key_report = 'wxplan:report:v2:{id_}'
    cache_key_report_user = 'wxplan:report:user:{id_}'
    #: 攒钱(1-5年后)每年的[(本金,本息和),]金额
    recommended_savings_amount = PropsItem('recommended_savings_amount', [])
    income_msg = PropsItem('income_msg', '')

    class Meta:
        repr_attr_names = ['id_', 'user_id', 'raise_quota', 'income_msg']

    class Status(Enum):
        deprecated = 'D'
        valid = 'V'

    def __init__(self, id_, user_id, raise_quota, tour_children, savings, erfund, erfund_factor,
                 disposable_income, month_factor, mincome, pocket_money, mpayment, rent, status,
                 create_time, update_time):
        """
        :param user_id:用户ID
        :type user_id:int
        :param raise_quota:加薪额度
        :type raise_quota:int
        :param tour_children:旅游／子女
        :type tour_children:int
        :param savings:攒钱
        :type savings:int
        :param erfund:紧急备用金
        :type erfund:int
        :param erfund_factor:紧急备用金因子
        :type erfund_factor:int
        :param disposable_income:可支配收入
        :type disposable_income:int
        :param month_factor:月份数
        :type month_factor:int
        :param mincome:每月需存
        :type mincome:int
        :param pocket_money:零用钱
        :type pocket_money:int
        :param mpayment:月供
        :type mpayment:int
        :param rent:房租
        :type rent:int
        :param status:状态
        :type status:char
        """
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.raise_quota = raise_quota
        self.tour_children = tour_children
        self.savings = savings
        self.erfund = erfund
        self.erfund_factor = erfund_factor
        self.disposable_income = disposable_income
        self.month_factor = month_factor
        self.mincome = mincome
        self.pocket_money = pocket_money
        self.mpayment = mpayment
        self.rent = rent
        self._status = status
        self.create_time = create_time
        self.update_time = update_time

    def get_db(self):
        return 'wxplan'

    def get_uuid(self):
        return 'report:{.id_}'.format(self)

    @property
    def status(self):
        return self.Status(self._status)

    @classmethod
    def get(cls, report_id):
        return cls.get_by_id(report_id)

    @classmethod
    @cache(cache_key_report)
    def get_by_id(cls, id_):
        sql = ('select id, user_id, raise_quota, tour_children, savings, erfund, erfund_factor, '
               'disposable_income, month_factor, mincome, pocket_money, mpayment, rent, status, '
               'create_time, update_time from {0} where id=%s').format(cls.table_name)
        rs = db.execute(sql, (id_,))
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_report_user)
    def get_id_by_user_id(cls, id_):
        sql = ('select id from {0} where user_id=%s').format(cls.table_name)

        rs = db.execute(sql, (id_,))
        return rs[0][0] if rs else None

    @classmethod
    def get_by_user_id(cls, user_id):
        id_ = cls.get_id_by_user_id(user_id)
        return cls.get(id_) if id_ else None

    @classmethod
    def add(cls, user_id, raise_quota, tour_children, savings, erfund, erfund_factor,
            disposable_income, month_factor, mincome, pocket_money, mpayment, rent,
            recommended_savings_amount, income_msg):
        sql = (
            'insert into {0} (user_id, raise_quota, tour_children, savings, erfund, erfund_factor, '
            'disposable_income, month_factor, mincome, pocket_money, mpayment, rent, status, '
            'create_time) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)').format(
            cls.table_name)
        params = (user_id, raise_quota, tour_children, savings, erfund, erfund_factor,
                  disposable_income, month_factor, mincome, pocket_money, mpayment, rent,
                  cls.Status.valid.value, datetime.now())

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_user_id(user_id)
        instance = cls.get(id_)
        if instance:
            instance.recommended_savings_amount = recommended_savings_amount
            instance.income_msg = income_msg
        return instance

    @classmethod
    def add_or_update(cls, user_id, raise_quota, tour_children, savings, erfund, erfund_factor,
                      disposable_income, month_factor, mincome, pocket_money, mpayment, rent,
                      recommended_savings_amount, income_msg):
        report = cls.get_by_user_id(user_id)
        raise_quota = round_half_up(raise_quota, 10)

        if report:
            return cls.update(report.id_, user_id, raise_quota, tour_children,
                              savings, erfund, erfund_factor,
                              disposable_income, month_factor,
                              mincome, pocket_money, mpayment, rent,
                              recommended_savings_amount, income_msg)
        return cls.add(user_id, raise_quota, tour_children, savings, erfund, erfund_factor,
                       disposable_income, month_factor, mincome, pocket_money, mpayment, rent,
                       recommended_savings_amount, income_msg)

    @classmethod
    def update(cls, id_, user_id, raise_quota, tour_children, savings, erfund, erfund_factor,
               disposable_income, month_factor, mincome, pocket_money, mpayment, rent,
               recommended_savings_amount, income_msg):
        sql = ('update {0} set user_id=%s, raise_quota=%s, tour_children=%s, savings=%s, erfund=%s,'
               'erfund_factor=%s, disposable_income=%s, month_factor=%s,'
               ' mincome=%s, pocket_money=%s, mpayment=%s, rent=%s, status=%s, update_time=%s '
               'where id=%s').format(cls.table_name)
        params = (user_id, raise_quota, tour_children, savings, erfund, erfund_factor,
                  disposable_income, month_factor, mincome, pocket_money,
                  mpayment, rent, cls.Status.valid.value, datetime.now(), id_)
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_user_id(user_id)
        instance = cls.get(id_)
        if instance:
            instance.recommended_savings_amount = recommended_savings_amount
            instance.income_msg = income_msg
        return instance

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key_report.format(id_=id_))

    @classmethod
    def clear_cache_by_user_id(cls, user_id):
        mc.delete(cls.cache_key_report_user.format(id_=user_id))

    @property
    def user(self):
        from core.models.user.account import Account

        return Account.get(self.user_id)

    def get_rent_data(self):
        if self.rent > 0:
            h27 = Decimal(self.rent) * FeeRate.current_interest.value * Decimal('180') / Decimal(
                '365')
            g27 = Decimal(self.rent) * FeeRate.thirty_days.value * Decimal('180') / Decimal('365')
            return round(h27, 1), round(g27, 1)

    def get_monthly_mortgages(self):
        if self.mpayment > 0:
            h26 = Decimal(self.mpayment) * FeeRate.current_interest.value * Decimal('30') / Decimal(
                '365')
            g26 = Decimal(self.mpayment) * FeeRate.thirty_days.value * Decimal('30') / Decimal(
                '365')
            return round(h26, 1), round(g26, 1)

    def get_pocket_wallet_profit(self):
        if self.pocket_money > 0:
            return round(self.pocket_money * FeeRate.wallet.value / 12, 1)
        return 0

    def get_pocket_bank_profit(self):
        if self.pocket_money > 0:
            return round(self.pocket_money * FeeRate.current_interest.value / 12, 1)
        return 0

    def deprecate(self):
        if self.id_:
            sql = 'update {0} set status=%s where id=%s'.format(self.table_name)
            self._status = self.Status.deprecated.value
            db.execute(sql, (self._status, self.id_,))
            db.commit()
            self.clear_cache(self.id_)
            return True
        return False

    @property
    def is_deprecated(self):
        return self.status is self.Status.deprecated


class WageLevel(EntityModel):
    """
    未来10年，收入水平占本省人均收入比例
    """
    table_name = 'wxplan_wage_level'
    cache_key = 'wxplan:wage_levels:report:{id_}'

    def __init__(self, id_, report_id, year_interval, wage_level):
        """
        :param report_id: report id
        :type report_id: int
        :param year_interval: 年份
        :type year_interval: int
        :param wage_level: 收入水平占本省人均收入比例
        :type wage_level: float
        """
        self.id_ = id_
        self.report_id = report_id
        self.year_interval = year_interval
        self.wage_level = wage_level

    @classmethod
    @cache(cache_key)
    def get_by_report_id(cls, id_):
        sql = ('select id, report_id, year_interval, wage_level '
               'from {0} where report_id=%s').format(cls.table_name)
        rs = db.execute(sql, (id_,))
        return [cls(*item) for item in rs if rs]

    @classmethod
    def add(cls, report_id, wages):
        sql = ('insert into {0} (report_id, year_interval, wage_level) '
               'values(%s, %s, %s)').format(cls.table_name)

        for year_interval, wage_level in enumerate(wages):
            params = (report_id, year_interval, wage_level)
            db.execute(sql, params)
        db.commit()
        cls.clear_cache(report_id)
        return cls.get_by_report_id(report_id)

    @classmethod
    def update(cls, report_id, wages):
        sql = ('update {0} set wage_level=%s where report_id=%s and year_interval=%s').format(
            cls.table_name)

        for year_interval, wage_level in enumerate(wages):
            params = (wage_level, report_id, year_interval)
            db.execute(sql, params)
        db.commit()
        cls.clear_cache(report_id)
        return cls.get_by_report_id(report_id)

    @classmethod
    def add_or_update(cls, report_id, wages):
        wage = cls.get_by_report_id(report_id)
        return cls.update(report_id, wages) if wage else cls.add(report_id, wages)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))
