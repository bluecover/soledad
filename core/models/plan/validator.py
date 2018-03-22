# -*- coding: utf-8 -*-

'''
validate request.form
'''
import simplejson as json

from datetime import datetime

from core.models.utils.validator import (
    validate_values_in, validate_values_range, validate_xss_input,
    validate_values_range_allow_zero
)

from core.models import errors
from core.models.location.location import Location

from .consts import (MINORS_AGE_RANGE, YEARS_RANGE,
                     SOCIETY_INSURE_DEFAULT_VALUES,
                     DEFAUT_MONEY_RANGE,
                     TARGET_DEFAULT_VALUES,
                     CHILDREN_KEYS)


class PlanValidate(object):

    def validate(self, value):
        if self.force_input:
            if not value:
                return errors.err_input_value_empty
        else:
            if not value:
                return errors.err_ok

        r = validate_xss_input(value)
        if r != errors.err_ok:
            return r
        return self.validate_method(value=value, check_values=self._value)


class PlanValidateRangeItem(PlanValidate):
    def __init__(self,
                 value_range=(0, 10000),
                 force_input=True,
                 validate_method=None):
        if not isinstance(value_range, tuple):
            raise Exception('value range should be tuple')
        self.validate_method = validate_method
        self.force_input = force_input
        self.value_range = value_range
        self.validate_method = validate_method or validate_values_range
        self._value = value_range


class PlanValidateRangeItemWithZero(PlanValidate):
    def __init__(self,
                 value_range=(0, 10000),
                 force_input=True,
                 validate_method=None):
        if not isinstance(value_range, tuple):
            raise Exception('value range should be tuple')
        self.validate_method = validate_method
        self.force_input = force_input
        self.value_range = value_range
        self.validate_method = (validate_method
                                or validate_values_range_allow_zero)
        self._value = value_range


class PlanValidateItem(PlanValidate):
    def __init__(self,
                 default_values=[],
                 force_input=True,
                 validate_method=None):
        if not isinstance(default_values, list):
            raise Exception('default value should be list')
        self.validate_method = validate_method or validate_values_in
        self.force_input = force_input
        self.default_values = default_values
        self._value = default_values


class PlanChildrenValidateItem(PlanValidate):
    def __init__(self):
        pass

    def validate(self, value):
        if not value:
            return errors.err_ok
        try:
            if not isinstance(value, list):
                value = json.loads(value)
        except:
            return errors.err_invalid_json_format
        if not isinstance(value, list):
            return errors.err_invalid_data_format
        for v in value:
            assert len(v.keys()) == 3
            assert 'age' in v.keys()
            assert 'child_society_insure' in v.keys()
            assert 'biz_insure' in v.keys()
            for k in v.keys():
                if not k == 'biz_insure':
                    assert validate_xss_input(v.get(k)) == errors.err_ok
            age = v.get('age')
            child_society_insure = v.get('child_society_insure')
            biz_insure = v.get('biz_insure')
            try:
                age = int(age)
            except:
                return errors.err_invalid_data_format
            _min, _max = MINORS_AGE_RANGE
            if child_society_insure:
                if child_society_insure not in SOCIETY_INSURE_DEFAULT_VALUES:
                    return errors.err_invalid_default_values
            if age < _min or age > _max:
                return errors.err_invalid_range_values
            if biz_insure:
                _cls = PlanInsureValidateItem()
                r = _cls.validate(biz_insure)
                if not r == errors.err_ok:
                    return r
        return errors.err_ok


class PlanInsureValidateItem(PlanValidate):
    def __init__(self):
        pass

    def validate(self, value):
        if not value:
            return errors.err_ok
        try:
            if not isinstance(value, list):
                value = json.loads(value)
        except:
            return errors.err_invalid_json_format
        if not isinstance(value, list):
            return errors.err_invalid_data_format
        for v in value:
            assert len(v.keys()) == 3
            assert 'insure_type' in v.keys()
            assert 'insure_year_fee' in v.keys()
            assert 'insure_quota' in v.keys()
            insure_type = v.get('insure_type')
            insure_year_fee = v.get('insure_year_fee')
            insure_quota = v.get('insure_quota')
            if insure_type not in SOCIETY_INSURE_DEFAULT_VALUES:
                return errors.err_invalid_default_values
            try:
                insure_year_fee = int(insure_year_fee)
                insure_quota = int(insure_quota)
            except:
                return errors.err_invalid_data_format
            _min, _max = DEFAUT_MONEY_RANGE
            if insure_quota < _min or insure_quota > _max:
                return errors.err_invalid_range_values
            if not insure_year_fee > 0:
                return errors.err_invalid_range_values
        return errors.err_ok


class PlanTargetValidateItem(PlanValidate):
    def __init__(self):
        pass

    def validate(self, value):
        if not value:
            return errors.err_input_value_empty
        try:
            if not isinstance(value, list):
                value = json.loads(value)
        except:
            return errors.err_invalid_json_format
        if not isinstance(value, list):
            return errors.err_invalid_data_format
        if not value:
            return errors.err_input_value_empty
        if len(value) > 5:
            return errors.err_invalid_data_format
        for v in value:
            assert len(v.keys()) == 3
            assert 'target' in v.keys()
            assert 'money' in v.keys()
            assert 'year' in v.keys()
            target = v.get('target')
            money = v.get('money')
            year = v.get('year')
            try:
                money = int(money)
                year = int(year)
            except:
                return errors.err_invalid_data_format
            if target not in TARGET_DEFAULT_VALUES:
                return errors.err_invalid_default_values
            _min, _max = DEFAUT_MONEY_RANGE
            if money < _min or money > _max:
                return errors.err_invalid_range_values
            _min, _max = YEARS_RANGE
            if year < _min or year > _max:
                return errors.err_invalid_range_values
        return errors.err_ok


class PlanLocValidateItem(PlanValidate):
    def __init__(self):
        pass

    def validate(self, value):
        if not value:
            return errors.err_input_value_empty
        # value should not be china
        if value == '100000':
            return errors.err_invalid_default_values
        assert validate_xss_input(value) == errors.err_ok
        if not Location.get(value):
            return errors.err_invalid_default_values
        return errors.err_ok


# 儿童保险
class ChildPlanVlidator(PlanValidate):
    def validate(self, value):
        if not value:
            return errors.err_input_value_empty
        try:
            children = json.loads(value)
        except:
            return errors.err_invalid_data_format
        for child in children:
            if 'other' in child:
                assert len(child.keys()) == 7
                assert child.get('other')
            else:
                assert len(child.keys()) == 6
            for k, v in child.items():
                assert k in CHILDREN_KEYS
                filter_chinese = True
                if k == 'name':
                    filter_chinese = False
                elif k == 'birthdate':
                    try:
                        datetime.strptime(v, '%Y-%m-%d')
                    except:
                        return errors.err_invalid_data_format
                else:
                    try:
                        v = int(v)
                    except:
                        return errors.err_invalid_data_format
                if k != 'birthdate':
                    assert (validate_xss_input(v,
                                               filter_chinese=filter_chinese)
                            == errors.err_ok)
        return errors.err_ok


class PlanValidator(object):
    def __init__(self, form_values=None):
        assert form_values
        self.form_values = form_values

    def validate(self, form):
        '''
        form    -> request.form
        RETURN
        True, None or Error, reason
        '''
        assert self.form_values
        if not isinstance(form, dict):
            raise Exception('form should be dict')
        # check default values
        for name, value in self.form_values.items():
            # class
            _cls = value.validator
            if not _cls:
                return errors.err_invalid_data_format
            try:
                r = _cls.validate(form.get(name))
                if r != errors.err_ok:
                    return r
            except AssertionError:
                return errors.err_input_is_xss

        # do some update here
        return errors.err_ok
