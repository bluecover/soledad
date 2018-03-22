# coding: utf-8

from flask import request, redirect, g, Blueprint, url_for

from libs.logger.rsyslog import rsyslog
from core.models.plan.plan import Plan
from core.models.plan.consts import REPORT_STATUS, FORMULA_VER
from core.models.plan.report import Report, cal_intermediate_data


def regen_log(report, msg):
    rsyslog.send(report.id + '\t' + msg, tag='formula_update_regen')


def _before_request():
    # redirects anonymous users to the login page
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.path))

    plan = Plan.get_by_user_id(g.user.id)
    g.plan = plan if plan else None
    if request.path.startswith('/mine/plan'):
        # TODO move to mine.plan
        if not g.plan:
            return redirect('/mine/info')
        report = Report.get_latest_by_plan_id(g.plan.id)
        if not report:
            return redirect('/mine/info')

        # stop gen pdf
        if not (report.status >= REPORT_STATUS.interdata):
            return redirect('/mine/info')

        if int(report.formula_ver) < int(FORMULA_VER):
            regen_log(report, 'start regenerate inter data')
            cal_intermediate_data(report, force=True, log=regen_log)
            report.update_formula_ver(FORMULA_VER)
            regen_log(
                report,
                'success regenerate inter data FV:%s' % report.formula_ver)

        g.report = report
        g.report_data = report.inter_data


def create_blueprint(name, import_name, before_request=None, **kwargs):
    kwargs.setdefault('url_prefix', '/mine')
    bp = Blueprint('mine.%s' % name, import_name, **kwargs)
    if not before_request:
        before_request = _before_request
    bp.before_request(before_request)
    return bp
