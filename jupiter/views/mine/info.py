# -*- coding: utf-8 -*-

"""
    mine_info ui
"""

from flask import request, redirect, g
from flask_mako import render_template

from core.models import errors
from core.models.plan.plan import Plan
from core.models.plan.validator import PlanValidator
from jupiter.views.mine.plan.consts import (
    PLAN_FORM_STEP1,
    PLAN_FORM_STEP2,
    PLAN_FORM_STEP3,
    PLAN_FORM_STEP4)

from ._blueprint import create_blueprint


bp = create_blueprint('info', __name__)


def check_form_at_least_one_input(keys):
    '''
    检查form中至少有一个key
    例如：每月收入，每月其他收入只有一个即可
    '''
    for k in keys:
        if request.form.get(k):
            return errors.err_ok
    return errors.err_input_value_empty


def check_main_key_and_other_keys_input(main_key, other_keys,
                                        force_main_key_input=False):
    '''
    检查在main_key存在的情况下，other_keys都必须存在
    force_main_key_input设置main_key是否为必填
    例如：如果有伴侣，则必须会有伴侣的其他信息
    '''
    if force_main_key_input:
        if not request.form.get(main_key):
            return errors.err_input_value_empty
    else:
        if not request.form.get(main_key):
            return errors.err_ok
    for k in other_keys:
        if not request.form.get(k):
            return errors.err_input_value_empty
    return errors.err_ok


def check_need_jump_to_steps(current_step):
    '''
    检查步骤是否合法
    1. 如果没有plan则跳到第一步
    2. 如果没有data但是有了plan，数据错误，则跳会第一步，并更新
    3. 如果步骤小于可以进入的步骤，则跳到可以进入的步骤
    '''
    step = 1
    if not g.plan:
        return step
    if not g.plan.data:
        g.plan.update_step(1, force=True)
        return step
    if g.plan.step < current_step:
        return g.plan.step or step
    return 0


@bp.route('/info', methods=['GET', 'POST'])
@bp.route('/info/1', methods=['GET', 'POST'])
def mine_info_1():
    err_id, err_message = None, None
    cur_path = 'info'
    current_step = 1
    if request.method == 'POST':
        r = check_main_key_and_other_keys_input(
            'spouse', ['spouse_age', 'spouse_career']
        )
        if r == errors.err_ok:
            v = PlanValidator(form_values=PLAN_FORM_STEP1)
            r = v.validate(request.form)
        if r == errors.err_ok:
            plan = Plan.add(g.user.id) if not g.plan else g.plan
            has_spouse = request.form.get('spouse')
            plan.data.update(
                gender=request.form.get('gender'),
                age=int(request.form.get('age')),
                career=request.form.get('career'),
                province=request.form.get('province'),
                city=request.form.get('city'),
                phone=request.form.get('phone'),
                mine_society_insure=request.form.get('mine_society_insure'),
                mine_biz_insure=request.form.get('mine_biz_insure'),
                spouse=request.form.get('spouse'),
                spouse_age=(
                    None if not has_spouse
                    else request.form.get('spouse_age')),
                spouse_career=(
                    None if not has_spouse
                    else request.form.get('spouse_career')),
                spouse_society_insure=(
                    None if not has_spouse
                    else request.form.get('spouse_society_insure')),
                spouse_biz_insure=(
                    None if not has_spouse
                    else request.form.get('spouse_biz_insure')),
                children=request.form.get('children')
            )
            plan.update_step(2)
            return redirect('/mine/info/2')
        err_id, err_message = r
    return render_template('/mine/info/1.html', **locals())


_keys_income = ['income_month_salary',
                'income_month_extra',
                'income_year_bonus',
                'income_year_extra',
                'spouse_income_month_salary',
                'spouse_income_month_extra',
                'spouse_income_year_bonus',
                'spouse_income_year_extra'
                ]

_keys_expend = ['expend_month_ent',
                'expend_month_trans',
                'expend_month_shopping',
                'expend_month_house',
                'expend_month_extra',
                'expend_year_extra'
                ]


@bp.route('/info/2', methods=['GET', 'POST'])
def mine_info_2():
    r = check_need_jump_to_steps(2)
    if r:
        return redirect('/mine/info/%s' % r)
    current_step = 2
    err_id, err_message = None, None
    cur_path = 'info'
    plan = g.plan
    if request.method == 'POST':
        r = check_form_at_least_one_input(_keys_income)
        if r == errors.err_ok:
            r = check_form_at_least_one_input(_keys_expend)
        if r == errors.err_ok:
            v = PlanValidator(form_values=PLAN_FORM_STEP2)
            r = v.validate(request.form)
        if r == errors.err_ok:
            plan.data.update(
                income_month_salary=request.form.get('income_month_salary'),
                income_month_extra=request.form.get('income_month_extra'),
                income_year_bonus=request.form.get('income_year_bonus'),
                income_year_extra=request.form.get('income_year_extra'),
                spouse_income_month_salary=(
                    request.form.get('spouse_income_month_salary')),
                spouse_income_month_extra=(
                    request.form.get('spouse_income_month_extra')),
                spouse_income_year_bonus=(
                    request.form.get('spouse_income_year_bonus')),
                spouse_income_year_extra=(
                    request.form.get('spouse_income_year_extra')),
                expend_month_ent=request.form.get('expend_month_ent'),
                expend_month_trans=request.form.get('expend_month_trans'),
                expend_month_shopping=request.form.get(
                    'expend_month_shopping'),
                expend_month_house=request.form.get('expend_month_house'),
                expend_month_extra=request.form.get('expend_month_extra'),
                expend_year_extra=request.form.get('expend_year_extra')
            )
            plan.update_step(3)
            return redirect('/mine/info/3')
        err_id, err_message = r
    return render_template('/mine/info/2.html', **locals())


@bp.route('/info/3', methods=['GET', 'POST'])
def mine_info_3():
    r = check_need_jump_to_steps(3)
    if r:
        return redirect('/mine/info/%s' % r)
    current_step = 3
    err_id, err_message = None, None
    plan = g.plan
    cur_path = 'info'
    if request.method == 'POST':
        v = PlanValidator(form_values=PLAN_FORM_STEP3)
        r = v.validate(request.form)

        if r == errors.err_ok:
            plan.data.update(
                deposit_current=request.form.get('deposit_current'),
                deposit_fixed=request.form.get('deposit_fixed'),
                funds_money=request.form.get('funds_money') or 0,
                funds_index=request.form.get('funds_index') or 0,
                funds_hybrid=request.form.get('funds_hybrid') or 0,
                funds_bond=request.form.get('funds_bond') or 0,
                funds_stock=request.form.get('funds_stock') or 0,
                funds_other=request.form.get('funds_other') or 0,
                invest_bank=request.form.get('invest_bank') or 0,
                invest_stock=request.form.get('invest_stock') or 0,
                invest_national_debt=(
                    request.form.get('invest_national_debt') or 0),
                invest_p2p=request.form.get('invest_p2p') or 0,
                invest_insure=request.form.get('invest_insure') or 0,
                invest_metal=request.form.get('invest_metal') or 0,
                invest_other=request.form.get('invest_other') or 0,
                consumer_loans=request.form.get('consumer_loans') or 0,
                real_estate_value=request.form.get('real_estate_value') or 0,
                real_estate_loan=request.form.get('real_estate_loan') or 0,
                car_value=request.form.get('car_value') or 0,
                real_collection_value=(
                    request.form.get('real_collection_value') or 0),
                real_other_value=request.form.get('real_other_value') or 0,
            )
            plan.update_step(4)
            return redirect('/mine/info/4')
        err_id, err_message = r
    return render_template('/mine/info/3.html', **locals())


@bp.route('/info/4', methods=['GET', 'POST'])
def mine_info_4():
    r = check_need_jump_to_steps(4)
    if r:
        return redirect('/mine/info/%s' % r)
    current_step = 4
    err_id, err_message = None, None
    plan = g.plan
    cur_path = 'info'
    if request.method == 'POST':
        v = PlanValidator(form_values=PLAN_FORM_STEP4)
        r = v.validate(request.form)
        if r == errors.err_ok:
            plan.data.update(
                target=request.form.get('target'),
                invest_exp=request.form.get('invest_exp'),
                invest_concern=request.form.get('invest_concern'),
                invest_increase=request.form.get('invest_increase'),
                invest_handle=request.form.get('invest_handle')
            )
            plan.update_step(5)
            plan.send_for_report()
            return redirect('/mine')
        err_id, err_message = r
    return render_template('/mine/info/4.html', **locals())
