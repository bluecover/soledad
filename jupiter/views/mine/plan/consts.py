from core.models.plan.property import RAW_DATA


PLAN_FORM_STEP1 = dict(
    gender=RAW_DATA.gender,
    age=RAW_DATA.age,
    career=RAW_DATA.career,
    province=RAW_DATA.province,
    city=RAW_DATA.city,
    phone=RAW_DATA.phone,
    mine_society_insure=RAW_DATA.mine_society_insure,
    mine_biz_insure=RAW_DATA.mine_biz_insure,
    spouse=RAW_DATA.spouse,
    spouse_age=RAW_DATA.spouse_age,
    spouse_career=RAW_DATA.spouse_career,
    spouse_society_insure=RAW_DATA.spouse_society_insure,
    spouse_biz_insure=RAW_DATA.spouse_biz_insure,
    children=RAW_DATA.children,
)

PLAN_FORM_STEP2 = dict(
    income_month_salary=RAW_DATA.income_month_salary,
    income_month_extra=RAW_DATA.income_month_extra,
    income_year_bonus=RAW_DATA.income_year_bonus,
    income_year_extra=RAW_DATA.income_year_extra,
    spouse_income_month_salary=RAW_DATA.spouse_income_month_salary,
    spouse_income_month_extra=RAW_DATA.spouse_income_month_extra,
    spouse_income_year_bonus=RAW_DATA.spouse_income_year_bonus,
    spouse_income_year_extra=RAW_DATA.spouse_income_year_extra,
    expend_month_ent=RAW_DATA.expend_month_ent,
    expend_month_trans=RAW_DATA.expend_month_trans,
    expend_month_shopping=RAW_DATA.expend_month_shopping,
    expend_month_house=RAW_DATA.expend_month_house,
    expend_month_extra=RAW_DATA.expend_month_extra,
    expend_year_extra=RAW_DATA.expend_year_extra,
)

PLAN_FORM_STEP3 = dict(
    deposit_current=RAW_DATA.deposit_current,
    deposit_fixed=RAW_DATA.deposit_fixed,
    funds_money=RAW_DATA.funds_money,
    funds_index=RAW_DATA.funds_index,
    funds_hybrid=RAW_DATA.funds_hybrid,
    funds_bond=RAW_DATA.funds_bond,
    funds_stock=RAW_DATA.funds_stock,
    funds_other=RAW_DATA.funds_other,
    invest_bank=RAW_DATA.invest_bank,
    invest_stock=RAW_DATA.invest_stock,
    invest_national_debt=RAW_DATA.invest_national_debt,
    invest_p2p=RAW_DATA.invest_p2p,
    invest_insure=RAW_DATA.invest_insure,
    invest_metal=RAW_DATA.invest_metal,
    invest_other=RAW_DATA.invest_other,
    consumer_loans=RAW_DATA.consumer_loans,
    real_estate_value=RAW_DATA.real_estate_value,
    real_estate_loan=RAW_DATA.real_estate_loan,
    real_collection_value=RAW_DATA.real_collection_value,
    real_other_value=RAW_DATA.real_other_value,
)

PLAN_FORM_STEP4 = dict(
    target=RAW_DATA.target,
    invest_exp=RAW_DATA.invest_exp,
    invest_concern=RAW_DATA.invest_concern,
    invest_increase=RAW_DATA.invest_increase,
    invest_handle=RAW_DATA.invest_handle,
)
