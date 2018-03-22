# -*- coding: utf-8 -*-

from jupiter.utils import get_repository_root

from core.models.plan.calculator import Calculator, InvalidFormulaKeyError
from core.models.plan.property import RAW_DATA
from .framework import BaseTestCase


_data = dict(
    income_month_salary=10000,
    income_month_extra=10000,
    income_year_bonus=100000,
    income_year_extra=100000,
    expend_month_ent=10000,
    expend_month_trans=10000,
    expend_month_shopping=10000,
    expend_month_house=10000,
    expend_month_extra=10000,
    expend_year_extra=10000,
)

_str_data = dict(
    income_month_salary='10000',
    income_month_extra=None,
)

_assets_data = dict(
    deposit_current=100,
    deposit_fixed=100,
    funds_money=100,
    funds_hybrid=100,
    funds_bond=100,
    funds_stock=100,
    funds_other=100,
    invest_bank=100,
    invest_stock=100,
    invest_national_debt=100,
)


class PlanTest(BaseTestCase):

    def test_calculate_plan(self):
        cal = Calculator.get_by_plan_data(_data)
        self.assertEqual(cal.data, _data)
        output = cal.execute(
            data_property=RAW_DATA,
            formula=get_repository_root() + '/tests/test_data/formula_1.py')
        assert output['income_month'] == \
            _data['income_month_salary'] + _data['income_month_extra']
        assert 'balance_year' in output
        assert 'income_year' in output
        assert output['balance_year_ratio'] == \
            round(float(output['balance_year']) / output['income_year'], 2)

    def test_wrong_formula(self):
        cal = Calculator.get_by_plan_data(_data)
        self.assertEqual(cal.data, _data)
        with self.assertRaises(InvalidFormulaKeyError) as err:
            cal.execute(
                data_property=RAW_DATA,
                formula=get_repository_root() + '/tests/test_data/formula_2.py')
        error = InvalidFormulaKeyError(
            'invalid key: %s in formula [%s]' %
            ('income_a',
             (get_repository_root() + '/tests/test_data/formula_2.py')))
        assert str(err.exception) == str(error)

    def test_calculate_string_plan_data(self):
        cal = Calculator.get_by_plan_data(_str_data)
        assert isinstance(_str_data['income_month_salary'], str)
        output = cal.execute(
            data_property=RAW_DATA,
            formula=get_repository_root() + '/tests/test_data/formula_3.py')
        assert output['income_month'] == \
            int(_str_data['income_month_salary']) + 0
        assert isinstance(output['income_month_salary'], int)
        assert output['expend_month'] == 0

    def test_calculate_asset_plan(self):
        cal = Calculator.get_by_plan_data(_assets_data)
        output = cal.execute(
            data_property=RAW_DATA,
            formula=get_repository_root() + '/tests/test_data/formula_4.py')
        assert output['fin_assets'] == 100 * 10
        assert output['complex_fin_assets'] == output['fin_assets']
        assert output['invest_eval'] == 8
