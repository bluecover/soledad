# -*- coding: utf-8 -*-

from flask import Blueprint, session, redirect, url_for, g, request
from flask_mako import render_template

from core.models.location import location
from core.models.wxplan.data import PlanData, ProvinceSalary
from core.models.wallet import PublicDashboard
from core.models.utils import round_half_up
from core.models.wxplan.formula import Formula, Report
from core.models.plan.report import get_user_count

bp = Blueprint('plan', __name__, url_prefix='/plan')


@bp.route('/info', methods=['GET'])
def info():
    redo = request.args.get('redo')
    if not redo:
        if g.user:
            report = Report.get_by_user_id(g.user.id)
            plan = PlanData.get_by_user_id(g.user.id)
            if report and not report.is_deprecated:
                return redirect(url_for('.result'))
            if plan:
                session['wxplan'] = plan.to_dict()
                return redirect(url_for('.brief'))
        wxplan = session.get('wxplan')
        if wxplan:
            return redirect(url_for('.brief'))
    if g.user:
        report = Report.get_by_user_id(g.user.id)
        if report:
            report.deprecate()
    show_mask = request.args.get('mask')
    china = location.Location.get('100000')
    user_count = get_user_count()
    wxplan = session.get('wxplan')
    return render_template('plan/info.html', location=china, user_count=user_count, wxplan=wxplan,
                           show_mask=show_mask)


@bp.route('/brief', methods=['GET'])
def brief():
    wxplan = session.get('wxplan')
    if not wxplan:
        return redirect(url_for('.info'))

    plan = PlanData.from_dict(wxplan)
    formula = Formula(plan=plan)
    raise_quota = round_half_up(formula.get_raise_quota() * 100, 2)
    norm_dist = [min(99, int(n * 100)) for n in formula.get_ten_norm_dist()]
    income_msg = formula.get_income_msg()
    province = ProvinceSalary.get_by_province_code(plan.province_code)

    return render_template('plan/brief_result.html',
                           province=province,
                           raise_quota=raise_quota,
                           norm_dist=norm_dist,
                           income_msg=income_msg)


@bp.route('/result', methods=['GET'])
def result():
    if g.user:
        report = Report.get_by_user_id(g.user.id)
        if not report or report.is_deprecated:
            wxplan = session.get('wxplan')
            if not wxplan:
                return redirect(url_for('.info'))
            plan = PlanData.from_dict(wxplan)
            plan = plan.assign_to_user(g.user.id)
            formula = Formula(plan=plan)
            report = formula.gen_report()
        else:
            plan = PlanData.get_by_user_id(g.user.id)
            if not plan:
                return redirect(url_for('.info'))
        weekly_annual_rates = []
        latest_rate = 0
        if report.pocket_money > 0:
            dashboard = PublicDashboard.today()
            weekly_annual_rates = [(unicode(r.date), round_half_up(r.annual_rate, 2)) for r in
                                   dashboard.weekly_annual_rates]
            latest_rate = round_half_up(dashboard.latest_annual_rate.annual_rate, 2)
        return render_template('plan/detail_result.html', report=report, plan=plan,
                               weekly_annual_rates=weekly_annual_rates,
                               latest_rate=latest_rate,
                               monthly_mortgages=report.get_monthly_mortgages(),
                               rent_data=report.get_rent_data())

    return redirect(url_for('.brief'))
