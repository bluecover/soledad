# coding: utf-8

from flask import jsonify, g, Blueprint, request
from markupsafe import escape

from core.models.plan.plan import Plan
from core.models.plan.report import Report
from core.models.plan.consts import REPORT_STATUS
from core.models import errors
from core.models.utils.validator import (
    validate_value_len, validate_email, validate_phone)
from core.models.feedback.feedback import (
    Feedback, MAX_FEEDBACK_CONTACT_LEN, MAX_FEEDBACK_CONTENT_LEN)
from core.models.mail.kind import insurance_guide_mail
from core.models.mail.mail import Mail

bp = Blueprint('ajax', __name__, url_prefix='/j')


@bp.route('/')
def index():
    return jsonify(r=False)


@bp.route('/get_plan_status')
def get_plan_status():
    if not g.user:
        return jsonify(r=False)
    plan = Plan.get_by_user_id(g.user.id)
    if not plan:
        return jsonify(r=False)
    report = Report.get_latest_by_plan_id(plan.id)
    if not report:
        return jsonify(r=False)
    # stop gen pdf
    if report.status >= REPORT_STATUS.interdata:
        return jsonify(r=True)
    return jsonify(r=False)


@bp.route('/feedback', methods=['POST'])
def feedback():
    error = ''
    contact = None
    content = None
    if request.method == 'POST':
        contact = request.form.get('contact')
        content = request.form.get('content')
        referer = request.environ.get('HTTP_REFERER')
        if not contact:
            return jsonify(r=False)
        if not content:
            return jsonify(r=False)
        if (
            validate_value_len(contact, MAX_FEEDBACK_CONTACT_LEN) != errors.err_ok or
            validate_value_len(content, MAX_FEEDBACK_CONTENT_LEN) != errors.err_ok
        ):
            error = errors.err_value_too_long
        if (
            validate_email(contact) != errors.err_ok and
            validate_phone(contact) != errors.err_ok
        ):
            error = errors.err_invalid_default_values
        if not error:
            content = escape(content)
            # FIXME hidden danger of XSS here
            # The user's content should be store into database directly,
            # and displaying under the protection of Mako autoescape.
            content += u'    [来源：%s]' % referer
            Feedback.add(contact, content)
            return jsonify(r=True)
    return jsonify(r=False, error=error)


@bp.route('/mail', methods=['POST'])
def mail():
    email = request.form.get('user_email', type=str)
    ins_title = request.form.get('ins_title')
    product_url = request.referrer
    if errors.err_ok != validate_email(email):
        return jsonify(r=False, error=errors.err_invalid_default_values), 403

    mail = Mail.create(
        email, insurance_guide_mail, ins_title=ins_title, product_url=product_url)
    mail.send()
    return jsonify(r=True)
