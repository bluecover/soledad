# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.utils.validator import (
    not_validate,
    validate_phone,
)

from core.models.plan.validator import (
    PlanValidator,
    PlanValidateRangeItem,
    PlanValidateItem,
    PlanChildrenValidateItem,
    PlanInsureValidateItem,
    PlanTargetValidateItem,
)

from jupiter.views.mine.plan.consts import (
    PLAN_FORM_STEP1,
)

from core.models import errors


_form = dict(
    gender='male',
    age=39,
    career='4',
    province='110105',
    city='110000',
    phone='18618193877',
    spouse='',
    income_salary=10000,
    income_month_extra=10000,
    income_year_bonus=100000,
    income_year_extra=100000,
    expend_ent=10000,
    expend_trans=10000,
    expend_shopping=10000,
    expend_house=10000,
    expend_month_extra=10000,
    expend_year_extra=10000,
    mine_society_insure='4',
)

_err_form = dict(
    gender='male',
    age=1000,
    career='4',
    province='110105',
    city='110000',
    phone='18618193877',
    income_salary=10000,
    income_month_extra=10000,
    income_year_bonus=100000,
    income_year_extra=100000,
    expend_ent=10000,
    expend_trans=10000,
    expend_shopping=10000,
    expend_house=10000,
    expend_month_extra=10000,
    expend_year_extra=10000,
    society_insurance='4',
)

NAME = 'name'


class PlanValidatorTest(BaseTestCase):
    def test_not_validor(self):
        value = '123'
        r = not_validate(value=value)
        self.assertEqual(r, errors.err_ok)

    def test_validate_phone(self):
        phone = '18618193877'
        r = validate_phone(phone)
        self.assertEqual(r, errors.err_ok)

        phone = '186181938771'
        r = validate_phone(phone)
        self.assertEqual(r, errors.err_invalid_phone_number)

        phone = '1861819381'
        r = validate_phone(phone)
        self.assertEqual(r, errors.err_invalid_phone_number)

    def test_plan_validator(self):
        validator = PlanValidator(PLAN_FORM_STEP1)
        r = validator.validate(_form)
        self.assertEqual(r, errors.err_ok)

    def test_err_plan_validator(self):
        validator = PlanValidator(PLAN_FORM_STEP1)
        r = validator.validate(_err_form)
        self.assertEqual(r, errors.err_invalid_range_values)

    def test_validate_item(self):
        gender = PlanValidateItem(force_input=True,
                                  default_values=['male', 'female'])
        self.assertEqual(gender.validate('male'), errors.err_ok)
        self.assertEqual(gender.validate('animal'),
                         errors.err_invalid_default_values)
        self.assertEqual(gender.validate('<script>'),
                         errors.err_input_is_xss)

    def test_validate_item_should_input_but_no_input(self):
        gender = PlanValidateItem(force_input=True,
                                  default_values=['male', 'female'])
        self.assertEqual(gender.validate(''), errors.err_input_value_empty)

    def test_validate_range_item(self):
        age = PlanValidateRangeItem(force_input=True,
                                    value_range=(20, 100))
        self.assertEqual(age.validate(21), errors.err_ok)
        self.assertEqual(age.validate(101), errors.err_invalid_range_values)

    def test_validate_range_item_should_input_but_no_input(self):
        age = PlanValidateRangeItem(force_input=True,
                                    value_range=(20, 100))
        self.assertEqual(age.validate(0), errors.err_input_value_empty)

    def test_validate_function_should_be_called(self):
        def some_func(value, **kwargs):
            if value % 2 == 0:
                return errors.err_ok
            else:
                return errors.err_invalid_default_values
        some = PlanValidateItem(force_input=True,
                                validate_method=some_func)
        self.assertEqual(some.validate(4), errors.err_ok)
        self.assertEqual(some.validate(5), errors.err_invalid_default_values)

    def test_children_validate_item(self):
        v = PlanChildrenValidateItem()
        children_str = ('[{"child_society_insure":"7",'
                        '"biz_insure":"",'
                        '"age":"3"'
                        # '"career":"2"'
                        '}]')
        r = v.validate(children_str)
        self.assertEqual(r, errors.err_ok)

        v = PlanChildrenValidateItem()
        children_str = ('[{"child_society_insure":"7",'
                        '"biz_insure":"",'
                        '"age":"1000"'
                        # '"career":"2"'
                        '}]')
        r = v.validate(children_str)
        self.assertEqual(r, errors.err_invalid_range_values)

        v = PlanChildrenValidateItem()
        children_str = ('[{"child_society_insure":"7",'
                        '"biz_insure":"",'
                        '"age":"3"'
                        # '"career":"100"'
                        '}]')
        r = v.validate(children_str)
        self.assertEqual(r, errors.err_ok)

        r = v.validate('test')
        self.assertEqual(r, errors.err_invalid_json_format)

        v = PlanChildrenValidateItem()
        children_str = ('[{"child_society_insure":"100",'
                        '"biz_insure":"[]",'
                        '"age":"3"'
                        # '"career":"2"'
                        '}]')
        r = v.validate(children_str)
        self.assertEqual(r, errors.err_invalid_default_values)

        v = PlanChildrenValidateItem()
        children_str = (
            '[{"age": "9", '
            '"child_society_insure": "7", '
            '"biz_insure": [{"insure_year_fee": "78", '
            '"insure_quota": "600", "insure_type": "3"}]}]')
        r = v.validate(children_str)
        self.assertEqual(r, errors.err_ok)

        v = PlanChildrenValidateItem()
        children_str = (
            '[{"age": "9", '
            '"child_society_insure": "7", '
            '"biz_insure": [{"insure_year_fee": "-1", '
            '"insure_quota": "600", "insure_type": "3"}]}]')
        r = v.validate(children_str)
        self.assertEqual(r, errors.err_invalid_range_values)

    def test_insure_validate_item(self):
        v = PlanInsureValidateItem()
        insure_str = ('[{"insure_type":"4",'
                      '"insure_year_fee":"66","insure_quota":"2333"},'
                      '{"insure_type":"7",'
                      '"insure_year_fee":"22","insure_quota":"444"}]')
        r = v.validate(insure_str)
        self.assertEqual(r, errors.err_ok)

        insure_str = ('[{"insure_type":"1000",'
                      '"insure_year_fee":"66","insure_quota":"2333"},'
                      '{"insure_type":"7",'
                      '"insure_year_fee":"22","insure_quota":"444"}]')
        r = v.validate(insure_str)
        self.assertEqual(r, errors.err_invalid_default_values)

        insure_str = ('[{"insure_type":"4",'
                      '"insure_year_fee":"-1","insure_quota":"2333"},'
                      '{"insure_type":"7",'
                      '"insure_year_fee":"22","insure_quota":"444"}]')
        r = v.validate(insure_str)
        self.assertEqual(r, errors.err_invalid_range_values)

    def test_target_validate_item(self):
        v = PlanTargetValidateItem()
        target_str = ('[{"target":"4", "money":"1000", "year":"10"}]')
        r = v.validate(target_str)
        self.assertEqual(r, errors.err_ok)

        v = PlanTargetValidateItem()
        target_str = ('[{"target":"1000", "money":"1000", "year":"10"}]')
        r = v.validate(target_str)
        self.assertEqual(r, errors.err_invalid_default_values)

        v = PlanTargetValidateItem()
        target_str = ('[{"target":"4", "money":"1000", "year":"1000"}]')
        r = v.validate(target_str)
        self.assertEqual(r, errors.err_invalid_range_values)

        v = PlanTargetValidateItem()
        target_str = ('[]')
        r = v.validate(target_str)
        self.assertEqual(r, errors.err_input_value_empty)
