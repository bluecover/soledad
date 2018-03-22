# coding: utf-8

"""
    plan ui
"""

from flask import g
from flask_mako import render_template

from .._blueprint import create_blueprint


bp = create_blueprint('plan', __name__)


def make_context(**data):
    context = {'cur_path': 'plan'}
    context.update(g.report_data)
    context.update(data)
    return context


@bp.route('/plan')
@bp.route('/plan/status')
def plan_1():
    context = make_context()
    return render_template('/mine/plan/1_status.html', **context)


@bp.route('/plan/balance')
def plan_2():
    context = make_context()
    return render_template('/mine/plan/2_balance.html', **context)


@bp.route('/plan/urgent')
def plan_3():
    context = make_context()
    return render_template('/mine/plan/3_urgent.html', **context)


@bp.route('/plan/insurance')
def plan_4():
    context = make_context()
    return render_template('/mine/plan/4_insurance.html', **context)


@bp.route('/plan/risk')
def plan_5():
    context = make_context()
    return render_template('/mine/plan/5_risk.html', **context)


@bp.route('/plan/invest')
def plan_6():
    context = make_context()
    return render_template('/mine/plan/6_invest.html', **context)


@bp.route('/plan/target')
def plan_7():
    context = make_context()
    return render_template('/mine/plan/7_target.html', **context)
