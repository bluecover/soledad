# coding: utf-8

from flask import request, redirect, Blueprint
from flask_mako import render_template
from markupsafe import escape

from core.models import errors
from core.models.feedback.feedback import (
    Feedback, MAX_FEEDBACK_CONTACT_LEN, MAX_FEEDBACK_CONTENT_LEN)
from core.models.utils.validator import (
    validate_value_len, validate_email, validate_phone)


bp = Blueprint('about', __name__)


@bp.route('/about')
def about():
    return render_template('about/about.html')


@bp.route('/join')
def join():
    return render_template('about/join.html')


@bp.route('/contact')
def contact():
    return render_template('about/contact.html')


@bp.route('/legal/useragreement')
def useragreement():
    return render_template('about/agreement.html')


@bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    error = ''
    contact = None
    content = None
    if request.method == 'POST':
        contact = request.form.get('contact')
        content = request.form.get('content')
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
            Feedback.add(contact, escape(content))
            return redirect('/feedback')
    context = dict(
        error=error,
        contact=contact,
        content=content)
    return render_template('about/feedback.html', **context)
