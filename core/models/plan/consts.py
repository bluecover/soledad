# -*- coding: utf-8 -*-

import os

from solar.utils.storify import storify
from jupiter.utils import get_repository_root


ROOT_DIR = get_repository_root()
FORMULA_DIR = os.path.join(ROOT_DIR, 'core/models/plan/formula/formula.py')
CHILD_FORMULA_DIR = os.path.join(ROOT_DIR, 'core/models/plan/formula/child.py')
REPORT_DIR = os.path.join(ROOT_DIR, 'report/')

ONE_HUNDRED_MILLION = 100000000
DEFAUT_MONEY_RANGE = (1, ONE_HUNDRED_MILLION)  # 一亿
REAL_PROPERTY_RANGE = (1, 10000)  # 万元

ADULT_AGE_RANGE = (18, 100)  # 岁
MINORS_AGE_RANGE = (0, 18)  # 岁

YEARS_RANGE = (1, 51)

GENDER_DEFAULT_VALUES = ['male', 'female']
CAREER_DEFAULT_VALUES = [str(i) for i in range(0, 8)]
SPOUSE_DEFAULT_VALUES = ['1', ]
SPOUSE_CAREER_DEFAULT_VALUES = [str(i) for i in range(0, 7)]
SOCIETY_INSURANCE_DEFAULT_VALUES = [str(i) for i in range(1, 8)]
BIZ_INSURANCE_DEFAULT_VALUES = [str(i) for i in range(1, 9)]
SOCIETY_INSURE_DEFAULT_VALUES = [str(i) for i in range(0, 9)]

TARGET_DEFAULT_VALUES = [str(i) for i in range(1, 12)]

# 1、到目前为止，您有多少年投资于风险类资产的经验？( 如基金、股票、贵金属、外汇等 )
INVEST_EXP_DEFAULT_VALUES = ['1', '2', '3', '4', '5']

# 2、进行一笔投资时，您更关心的是？
INVEST_CONCERN_DEFAULT_VALUES = ['1', '2', '3']

# 3、如果由于市场火爆，您的投资组合突然大涨10%，您会如何应对？
INVEST_RISK_RAGE_DEFAULT_VALUES = ['1', '2', '3', '4']

# 4、您的投资组合在一个月内亏损了10%，您会如何应对？
INVEST_HANDLE_DEFAULT_VALUES = ['1', '2', '3', '4']


REPORT_STATUS = storify(dict(
    fail='-1',
    new='0',
    interdata='1',
    html='2',
    pdf='3',
))

# 记录算法的版本

FORMULA_VER = '13'


# 儿童险

CHILDREN_KEYS = [
    'name', 'gender', 'birthdate',
    'health', 'society', 'other',
    'family_income', 'insurance',
    'complematory', 'disease',
    'education']
