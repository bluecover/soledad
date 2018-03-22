# -*- coding: utf-8 -*-

import re
import copy
import types

from .consts import FORMULA_DIR

# from core.models import errors
# from .property import RAW_DATA


class InvalidFormulaKeyError(Exception):
    pass


class Calculator():

    def __init__(self, data):
        self.data = data

    # @classmethod
    # def _load_data(cls, plan):
    #     if plan.step < 6:
    #         return errors.err_invalid_plan_step, ''
    #     data = plan.data.data

    #     if not data:
    #         return errors.err_none_plan_data, ''

    #     if isinstance(data, dict):
    #         return errors.err_invalid_data_format, ''

    #     return errors.err_ok, data

    # @classmethod
    # def get_by_plan(cls, plan):
    #     error, r = cls._load_data(plan)
    #     if error == errors.err_ok:
    #         return cls(r)

    @classmethod
    def get_by_plan_data(cls, data):
        if data and isinstance(data, dict):
            return cls(data)

    def _verify_data(self, data_property):
        assert self.data
        data = copy.deepcopy(self.data)

        if not data_property:
            return data

        for key, prop in data_property.iteritems():
            # DATA校验
            if key in data:
                '''
                已经完成赋值, 检查赋值正确性
                '''
                if prop.default_type == int:
                    value = data[key]
                    if isinstance(value, int):
                        pass
                    else:
                        try:
                            value = int(value)
                        except (ValueError, TypeError):
                            '''
                            无法转换的，使用默认值
                            '''
                            value = prop.empty_value
                    data[key] = value
                elif prop.default_type == list:
                    value = data[key]
                    if isinstance(value, list):
                        pass
                    else:
                        value = prop.empty_value
                    data[key] = value
                elif prop.default_type == str:
                    pass
            else:
                '''
                没有的key，需要初始化
                '''
                if prop.empty_value is not None:
                    if prop.default_type == int:
                        data[key] = prop.empty_value
                    elif prop.default_type == list:
                        data[key] = prop.empty_value
                    elif prop.default_type == str:
                        data[key] = prop.empty_value
        return data

    def _detect_error(self, error, formula, data):
        key = re.findall("name '(\w+)' is not defined", str(error))[0]
        if key in data:
            # unlikely happen
            pass
        else:
            raise InvalidFormulaKeyError(
                'invalid key: %s in formula [%s]' % (key, formula))

    def execute(self, data_property=None, formula=FORMULA_DIR):
        if not self.data:
            return False

        inter_data = self._verify_data(data_property=data_property)

        # execute the formula
        # execfile(formula, inter_data)
        try:
            execfile(formula, inter_data)
        except NameError, e:
            self._detect_error(e, formula, locals())

        output_data = {}
        for k, v in inter_data.iteritems():
            if k == '__builtins__':
                continue
            if isinstance(v, types.FunctionType):
                continue
            if isinstance(v, types.ModuleType):
                continue
            output_data[k] = v

        return output_data
