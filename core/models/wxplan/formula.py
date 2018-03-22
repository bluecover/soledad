# -*- coding: utf-8 -*-

from decimal import Decimal
from math import ceil

from numpy import fv
from scipy.stats import norm

from .consts import FeeRate, IncomeDiagnosis
from .data import ProvinceSalary, Report, WageLevel
from core.models.utils import validator
from core.models import errors as err


class Formula(object):
    """
        小规划处理类
    """

    def __init__(self, plan):
        self.plan = plan

    @property
    def user(self):
        from core.models.user.account import Account

        return Account.get(self.plan.user_id)

    @property
    def province_salary(self):
        salary = ProvinceSalary.get_by_province_code(self.plan.province_code)
        return salary

    def format_error(self, name, error):
        return {'name': name, 'code': error}

    def validate_age(self, name):
        if isinstance(self.plan.age, int):
            result = validator.validate_values_in(self.plan.age, range(18, 56))
            if err.err_ok != result:
                return self.format_error(name, result)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_gender(self, name):
        if isinstance(self.plan.gender, int):
            result = validator.validate_values_in(
                self.plan.gender, range(0, 2))
            if err.err_ok != result:
                return self.format_error(name, result)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_stock(self, name):
        if isinstance(self.plan.stock, int):
            result = validator.validate_values_in(self.plan.stock, [-1, 1])
            if err.err_ok != result:
                return self.format_error(name, result)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_rent(self, name):
        if isinstance(self.plan.rent, int):
            if not self.plan.rent > -2:
                return self.format_error(name, err.err_invalid_validate)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_mpayment(self, name):
        if isinstance(self.plan.mpayment, int):
            if not self.plan.mpayment > -2:
                return self.format_error(name, err.err_invalid_validate)
        else:
            return self.format_error(name, err.err_invalid_data_format)

        if not self.is_month_income_validate():
            return self.format_error(name, err.err_invalid_validate)

    def validate_insurance(self, name):
        if isinstance(self.plan.insurance, int):
            if not self.plan.insurance > -2:
                return self.format_error(name, err.err_invalid_validate)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_tour(self, name):
        if isinstance(self.plan.tour, int):
            if not self.plan.tour > -2:
                return self.format_error(name, err.err_invalid_validate)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_children(self, name):
        if isinstance(self.plan.has_children, int):
            if not self.plan.has_children > -2:
                return self.format_error(name, err.err_invalid_validate)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_savings(self, name):
        if isinstance(self.plan.savings, int):
            if not self.plan.savings > -2:
                return self.format_error(name, err.err_invalid_validate)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_income(self, name):
        if isinstance(self.plan.mincome, int):
            if not self.plan.mincome > -2:
                return self.format_error(name, err.err_invalid_validate)
        else:
            return self.format_error(name, err.err_invalid_data_format)

    def validate_province_code(self, name):
        if not ProvinceSalary.has_code(self.plan.province_code):
            return self.format_error(name, err.err_invalid_validate)

    def validate(self):
        """
        gender, age, province_code, stock, rent, mpayment, insurance,
        tour, has_children, savings, mincome, create_time, update_time
        """
        validator_filters = ['age', 'gender', 'stock', 'rent', 'mpayment', 'insurance', 'tour',
                             'children', 'savings', 'income', 'province_code']
        for name in validator_filters:
            inline_func = getattr(self, 'validate_%s' % name)
            result = inline_func(name)
            if result is not None:
                return result
        return self.format_error('result', err.err_ok)

    def get_age_factor(self):
        return int(self.plan.age < 35)

    def get_children_factor(self):
        return int(self.plan.has_children == -1)

    def get_payment_factor(self):
        return int(self.plan.mpayment == -1)

    def get_rent_factor(self):
        return int(self.plan.rent == -1)

    def get_insurance_factor(self):
        return int(self.plan.insurance == -1)

    def get_sum_factor(self):
        """合计"""
        sum_factors = [self.get_age_factor(),
                       self.get_children_factor(),
                       self.get_payment_factor(),
                       self.get_rent_factor(),
                       self.get_insurance_factor()]
        return sum(sum_factors)

    def get_erfund_factor(self):
        """
        紧急备用金基数
        """
        return 6 if self.get_sum_factor() < 3 else 3

    def get_erfund_salary_factor(self):
        """
        紧急备用金额度
        """
        return self.get_erfund_factor() * self.get_theory_pocket_money_factor()

    def get_p15_factor(self):
        theory = self.get_theory_need_msavings_factor()
        month_payment = self.get_month_payment()
        return theory if self.plan.mincome > (theory +
                                              month_payment) else self.plan.mincome - month_payment

    def get_erfund(self):
        """
        紧急备用金
        """
        p15 = self.get_p15_factor()
        erfund_salary = self.get_erfund_salary_factor()
        min_salary = min(self.plan.savings, erfund_salary)
        return min_salary if (p15 * 10 + self.plan.savings) < erfund_salary else erfund_salary

    def get_theory_need_msavings_factor(self):
        """
        理论每月需存
        """
        erfund_salary = self.get_erfund_salary_factor()
        return 0 if self.plan.savings > erfund_salary else (erfund_salary -
                                                            self.plan.savings) / 10.0

    def get_month_payment(self):
        """
        月供＋房租
        """
        s = 0
        if self.plan.rent > -1:
            s += self.plan.rent
        if self.plan.mpayment > -1:
            s += self.plan.mpayment
        return s

    def is_month_income_validate(self):
        """
        判断月收入大于月供＋房租
        """

        return self.plan.mincome > self.get_month_payment()

    def get_monthly_disposable_income(self):
        """
        获取月可支配收入
        """
        return self.plan.mincome - self.get_month_payment()

    def get_practice_need_msavings_factor(self):
        """
        实际每月需存
        """
        theory = self.get_theory_need_msavings_factor()
        p15 = self.get_p15_factor()

        if (p15 * 10 + self.plan.savings) < self.get_erfund_salary_factor():
            return 0
        return theory

    def get_theory_pocket_money_factor(self):
        """
        理论零用钱
        """
        return self.province_salary.expenditure / 12.0

    def get_practice_pocket_money_factor(self):
        """
        实际零用钱
        """
        theory_pocket_money = self.get_theory_pocket_money_factor()
        practice_pocket_money = self.plan.mincome - self.get_month_payment()
        practice_pocket_money -= self.get_practice_need_msavings_factor()
        return min(theory_pocket_money, max(practice_pocket_money, 0))

    def get_pocket_money(self):
        return min(self.get_theory_pocket_money_factor(), self.get_practice_pocket_money_factor())

    def get_theory_children_tour_factor(self):
        """
        理论旅游/子女
        """
        tour_factor = 1 if self.plan.tour > -1 else 0
        children = 1 if self.plan.has_children > -1 else 0
        return (self.plan.mincome - self.get_month_payment()) * 0.1 * (tour_factor + children)

    def get_practice_children_tour_factor(self):
        """
        实际旅游/子女
        """
        theory_children_tour = self.get_theory_children_tour_factor()

        practice_children_tour = self.plan.mincome - self.get_month_payment()
        practice_children_tour -= self.get_need_msavings() + self.get_pocket_money()
        return min(theory_children_tour, practice_children_tour)

    def get_need_msavings(self):
        """
        每月需存
        """
        return self.get_practice_need_msavings_factor()

    def get_children_tour(self):
        """
        旅游 ／ 子女
        """
        return min(self.get_theory_children_tour_factor(),
                   self.get_practice_children_tour_factor())

    def get_theory_msavings_factor(self):
        """
        理论攒钱
        """
        result = self.plan.mincome - self.get_need_msavings() - self.get_pocket_money()
        return result - self.get_month_payment() - self.get_children_tour()

    def get_practice_msavings_factor(self):
        """
        实际攒钱
        """
        return self.get_theory_msavings_factor()

    def get_msavings(self):
        """
        攒钱
        """
        return min(self.get_theory_msavings_factor(), self.get_practice_msavings_factor())

    def get_this_year_norm_dist(self):
        """
        获取当年正态分布值
        """
        month_salary = self.province_salary.income / 12.0
        return norm.cdf(self.plan.mincome, 1.5 * month_salary, 6 * month_salary)

    def get_raise_quota(self):
        """
        加薪额度
        """
        return (Decimal(self.get_children_tour()) * FeeRate.one_year.value +
                Decimal(self.get_msavings()) * FeeRate.one_year.value +
                Decimal(self.get_need_msavings()) * FeeRate.thirty_days.value +
                Decimal(self.get_pocket_money()) * FeeRate.wallet.value +
                Decimal(self.get_month_payment()) * FeeRate.thirty_days.value
                ) / Decimal(self.plan.mincome)

    def get_ten_norm_dist(self):
        """
        获取未来10年的工资正态分布比例
        """
        now_norm_dist = self.get_this_year_norm_dist()
        yield now_norm_dist
        for year in range(1, 11):
            yield now_norm_dist * (1 + float(self.get_raise_quota()) / 2) ** year

    def get_five_savings_money(self):
        """
        获取未来5年本金，本息和
        """
        children_tour = self.get_children_tour()
        savings = self.get_msavings()
        _total = children_tour + savings
        origins = []
        results = []
        for year in range(1, 6):
            b = int(round(_total * year * 12))
            d = int(
                round(abs(fv(float(FeeRate.one_year.value / Decimal(12.0)), 12 * year, _total, 0))))
            origins.append(b)
            results.append(max(d - b, 0))
        return [origins, results]

    def get_income_msg(self):
        """
        获取收入诊断
        self.plan.mincome > self.province_salary.income / 12.0 * 2.5
        """
        for income in list(IncomeDiagnosis):
            if self.plan.mincome > self.province_salary.income / 12.0 * income.factor:
                return income.description

    def get_month_factor(self):
        """
        获取月份数
        """
        m = int(
            ceil((self.get_erfund() - self.plan.savings) / self.get_monthly_disposable_income()))
        return m if m > 0 else 0

    def gen_report(self):
        """
        生成报告
        """

        report = Report.add_or_update(user_id=self.plan.user_id,
                                      raise_quota=self.get_raise_quota(),
                                      tour_children=self.get_children_tour(),
                                      savings=self.get_msavings(),
                                      erfund=self.get_erfund(),
                                      erfund_factor=self.get_erfund_factor(),
                                      disposable_income=self.get_monthly_disposable_income(),
                                      month_factor=self.get_month_factor(),
                                      mincome=self.get_need_msavings(),
                                      pocket_money=self.get_pocket_money(),
                                      mpayment=self.plan.mpayment,
                                      rent=self.plan.rent,
                                      recommended_savings_amount=list(
                                          self.get_five_savings_money()),
                                      income_msg=self.get_income_msg())
        if report:
            WageLevel.add_or_update(report.id_, self.get_ten_norm_dist())
        return report
