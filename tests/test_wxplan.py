# -*- coding: utf-8 -*-

from core.models.wxplan.data import ProvinceSalary
from .framework import BaseTestCase
from core.models.wxplan.formula import Formula
from core.models.wxplan.data import PlanData
from decimal import Decimal
from core.models import errors


class PlanTest(BaseTestCase):
    def setUp(self):
        super(PlanTest, self).setUp()
        ProvinceSalary.add('110000', '北京', 48531.85, 33717.45)

    def test_add_wxplan(self):
        account = self.add_account()

        user_id = account.id

        plan = PlanData.add(gender=1, user_id=user_id, age=30, province_code=u'110000', stock=1,
                            rent=123,
                            mpayment=123,
                            insurance=1, tour=1, has_children=1, savings=10000, mincome=2000)
        assert plan is not None
        assert plan.user_id == user_id

    def test_gen_report(self):
        account = self.add_account()

        user_id = account.id

        plan = PlanData.add(gender=1, user_id=user_id, age=25, province_code=u'110000', stock=1,
                            rent=1000,
                            mpayment=1000,
                            insurance=1, tour=1, has_children=1, savings=10000, mincome=10000)
        formula = Formula(plan=plan)
        report = formula.gen_report()

        assert formula.get_theory_children_tour_factor() == 1600
        assert formula.get_practice_children_tour_factor() == 1600
        assert abs(formula.get_this_year_norm_dist() - 0.564386647) < 0.00001
        assert abs(formula.get_raise_quota() - Decimal(0.07233586)) < Decimal(0.00001)
        assert report is not None
        assert report.erfund == 16859

    def test_gen_simple_report(self):
        plan = PlanData(id_=None, gender=1, user_id=None, age=30, province_code=u'110000', stock=-1,
                        rent=1, mpayment=-1, insurance=-1, tour=-1, has_children=-1,
                        savings=20, mincome=20, update_time=None, create_time=None)
        formula = Formula(plan=plan)
        assert formula.get_practice_need_msavings_factor() == 0
        assert formula.get_practice_pocket_money_factor() == 19
        assert formula.get_theory_children_tour_factor() == 0
        assert formula.get_practice_children_tour_factor() == 0
        assert abs(formula.get_this_year_norm_dist() - 0.401612399) < 0.00001
        assert abs(formula.get_raise_quota() - Decimal(0.0365)) < Decimal(0.00001)

    def test_savings_money(self):
        account = self.add_account()

        user_id = account.id

        plan = PlanData.add(gender=1, user_id=user_id, age=30, province_code=u'110000', stock=1,
                            rent=123,
                            mpayment=123,
                            insurance=1, tour=1, has_children=1, savings=10000, mincome=10000)
        formula = Formula(plan=plan)

        assert 75100 in formula.get_five_savings_money()[0]

    def test_validation(self):
        account = self.add_account()

        user_id = account.id
        plan = PlanData(id_=None, gender=1, user_id=user_id, age=30, province_code=u'110000',
                        stock=1, rent=123, mpayment=123, insurance=1, tour=1, has_children=1,
                        savings=10000, mincome=2000, create_time=None, update_time=None)

        formula = Formula(plan=plan)
        validator = formula.validate()
        assert validator == {'name': 'result', 'code': errors.err_ok}

    def tearDown(self):
        super(PlanTest, self).tearDown()
