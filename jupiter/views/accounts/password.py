# coding: utf-8

from flask import request, g, redirect, url_for, abort
from flask_mako import render_template

from core.models.errors import AccountAliasValidationError, PasswordValidationError
from core.models.user.account import Account
from core.models.user.consts import ACCOUNT_REG_TYPE, VERIFY_CODE_TYPE
from core.models.user.verify import Verify, VerifyCodeException
from core.models.utils.limit import Limit, LIMIT
from jupiter.views.accounts.utils.password_utils import (
    reset_password, validate_reset_password_asker, send_reset_password_mail)

from ._blueprint import create_blueprint


bp = create_blueprint('password', __name__, url_prefix='/password')


@bp.before_request
def lead_to_house():
    if g.user:
        return redirect(url_for('mine.mine.mine'))


@bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    error = ''
    alias = ''
    if request.method == 'POST':
        # TODO 设置依据IP可能会有校园网访问的问题
        l = Limit.get(LIMIT.FORGOT_PASSWORD % request.remote_addr)
        if l.is_limited():
            abort(429)
        l.touch()

        alias = request.form.get('alias')
        try:
            alias_type = validate_reset_password_asker(alias)
            user = Account.get_by_alias(alias)
        except AccountAliasValidationError as e:
            error = unicode(e)
        else:
            if alias_type == ACCOUNT_REG_TYPE.EMAIL:
                send_reset_password_mail(user)
                return render_template('accounts/forgot_password_mail_sent.html', alias=alias)
            elif alias_type == ACCOUNT_REG_TYPE.MOBILE:
                return render_template(
                    'accounts/reset_mobile_user_password.html', mobile=alias)
    return render_template('accounts/forgot_password.html', alias=alias, error=error)


@bp.route('/reset/from_mail/<user_id>/<code>', methods=['GET', 'POST'])
def reset_for_mail_user(user_id, code):
    error = ''
    user = Account.get(user_id)
    if not user:
        return redirect(url_for('.reset_failed'))

    try:
        # 当post时才删除验证码
        v = Verify.validate(user.id_, code, VERIFY_CODE_TYPE.FORGOT_PASSWORD_EMAIL)
        if request.method == 'POST':
            v.delete()
    except VerifyCodeException as e:
        return redirect(url_for('.reset_failed'))

    if request.method == 'POST':
        # 校验密码是否合法一致
        new_password = request.form.get('new-password')
        confirmed_password = request.form.get('confirmed-password')

        try:
            reset_password(user, new_password, confirmed_password)
        except PasswordValidationError as e:
            error = unicode(e)
        else:
            return redirect(url_for('.reset_success'))
    return render_template('accounts/reset_mail_user_password.html', error=error)


@bp.route('/reset/success')
def reset_success():
    return render_template('accounts/reset_password_success.html')


@bp.route('/reset/fail')
def reset_failed():
    return render_template('accounts/reset_password_fail.html')
