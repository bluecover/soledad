# -*- coding: utf-8 -*-

from solar.utils.storify import storify

from core.models.utils.validator import not_validate, validate_phone

from .validator import (PlanValidateRangeItem,
                        PlanValidateItem,
                        PlanChildrenValidateItem,
                        PlanInsureValidateItem,
                        PlanTargetValidateItem,
                        PlanLocValidateItem,
                        PlanValidateRangeItemWithZero)

from .consts import (DEFAUT_MONEY_RANGE, REAL_PROPERTY_RANGE,
                     ADULT_AGE_RANGE, MINORS_AGE_RANGE)

from .consts import (CAREER_DEFAULT_VALUES, SOCIETY_INSURANCE_DEFAULT_VALUES,
                     GENDER_DEFAULT_VALUES, BIZ_INSURANCE_DEFAULT_VALUES,
                     SPOUSE_DEFAULT_VALUES,
                     SPOUSE_CAREER_DEFAULT_VALUES,
                     SOCIETY_INSURE_DEFAULT_VALUES,
                     INVEST_EXP_DEFAULT_VALUES,
                     INVEST_CONCERN_DEFAULT_VALUES,
                     INVEST_RISK_RAGE_DEFAULT_VALUES,
                     INVEST_HANDLE_DEFAULT_VALUES)


class PlanProperty():
    def __init__(self, validator, default_type, empty_value=None):
        self.validator = validator
        self.empty_value = empty_value
        self.default_type = default_type

P = PlanProperty

RAW_DATA = storify(dict(
    gender                     = P(PlanValidateItem(default_values=GENDER_DEFAULT_VALUES), str), # 性别
    age                        = P(PlanValidateRangeItem(value_range=ADULT_AGE_RANGE), str), # 年龄
    career                     = P(PlanValidateItem(default_values=CAREER_DEFAULT_VALUES), str), # 职业
    province                   = P(PlanLocValidateItem(), str), # 居住地 省份
    city                       = P(PlanLocValidateItem(), str), # 居住地 城市
    phone                      = P(PlanValidateItem(validate_method=validate_phone, force_input=False), str), # 电话
    mine_society_insure        = P(PlanValidateItem(default_values=SOCIETY_INSURE_DEFAULT_VALUES), str, '0'), # 我的社会保险
    mine_biz_insure            = P(PlanInsureValidateItem(), list, []), # 我的商业保险
    spouse                     = P(PlanValidateItem(default_values=SPOUSE_DEFAULT_VALUES, force_input=False), str), # 有无配偶
    spouse_age                 = P(PlanValidateRangeItem(value_range=ADULT_AGE_RANGE, force_input=False), str), # 配偶年龄
    spouse_career              = P(PlanValidateItem(default_values=SPOUSE_CAREER_DEFAULT_VALUES, force_input=False), str), # 配偶工作
    spouse_society_insure      = P(PlanValidateItem(default_values=SOCIETY_INSURE_DEFAULT_VALUES, force_input=False), str, '0'), # 配偶的社会保险
    spouse_biz_insure          = P(PlanInsureValidateItem(), list, []), # 配偶的商业保险
    children                   = P(PlanChildrenValidateItem(), list, []), # 子女

    income_month_salary        = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 每月工资收入
    income_month_extra         = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 每月其他收入
    income_year_bonus          = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 年终奖
    income_year_extra          = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 其他年收入
    spouse_income_month_salary = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 配偶每月工资收入
    spouse_income_month_extra  = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 配偶每月其他收入
    spouse_income_year_bonus   = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 配偶年终奖
    spouse_income_year_extra   = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 配偶其他年收入
    expend_month_ent           = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 每月餐饮娱乐
    expend_month_trans         = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 每月交通通讯
    expend_month_shopping      = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 每月家居购物
    expend_month_house         = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 每月房租房贷
    expend_month_extra         = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 每月其他支出
    expend_year_extra          = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 其他年度支出

    deposit_current            = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 现金及活期存款
    deposit_fixed              = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 定期存款
    funds_money                = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 货币基金/余额宝
    funds_index                = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 指数型基金
    funds_hybrid               = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 混合型基金
    funds_bond                 = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 债券型基金
    funds_stock                = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 股票型基金
    funds_other                = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 其他基金
    invest_bank                = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 银行理财产品
    invest_stock               = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 股票
    invest_national_debt       = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 国债
    invest_p2p                 = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # p2p网贷
    invest_insure              = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 储蓄型保险
    invest_metal               = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 贵金属
    invest_other               = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 其他金融资产
    consumer_loans             = P(PlanValidateRangeItemWithZero(value_range=DEFAUT_MONEY_RANGE, force_input=False), int, 0), # 信用卡债/消费贷款
    real_estate_value          = P(PlanValidateRangeItemWithZero(value_range=REAL_PROPERTY_RANGE, force_input=False), int, 0), # 房产市值
    real_estate_loan           = P(PlanValidateRangeItemWithZero(value_range=REAL_PROPERTY_RANGE, force_input=False), int, 0), # 未还房贷
    car_value                  = P(PlanValidateRangeItemWithZero(value_range=REAL_PROPERTY_RANGE, force_input=False), int, 0), # 汽车价值
    real_collection_value      = P(PlanValidateRangeItemWithZero(value_range=REAL_PROPERTY_RANGE, force_input=False), int, 0), # 收藏品
    real_other_value           = P(PlanValidateRangeItemWithZero(value_range=REAL_PROPERTY_RANGE, force_input=False), int, 0), # 其他实物资产

    target                     = P(PlanTargetValidateItem(), list, []), # 目标

    invest_exp                 = P(PlanValidateItem(force_input=True, default_values=INVEST_EXP_DEFAULT_VALUES), str), # 经验年数
    invest_concern             = P(PlanValidateItem(force_input=True, default_values=INVEST_CONCERN_DEFAULT_VALUES), str), # 投资时主要考虑
    invest_increase            = P(PlanValidateItem(force_input=True, default_values=INVEST_RISK_RAGE_DEFAULT_VALUES), str), # 波动范围
    invest_handle              = P(PlanValidateItem(force_input=True, default_values=INVEST_HANDLE_DEFAULT_VALUES), str), # 亏损后应对
        ))
