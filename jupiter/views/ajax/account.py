# coding: utf-8

from flask import Blueprint, g, jsonify, request, abort, after_this_request
from flask_wtf import Form
from wtforms import fields, validators
from werkzeug.urls import url_parse

from datetime import datetime
from libs.captcha.captcha import CaptchaError
from libs.logger.rsyslog import rsyslog

from core.models import errors
from core.models.errors import BindError, PasswordValidationError, AccountAliasValidationError
from core.models.user.alias import get_reg_type_from_alias
from core.models.user.bind import verify_bind, confirm_bind as confirm_mobile_bind
from core.models.user.account import Account
from core.models.user.consts import ACCOUNT_REG_TYPE, VERIFY_CODE_TYPE
from core.models.sms import ShortMessage
from core.models.sms.kind import forgot_password_sms
from core.models.user.register import register_with_confirm, confirm_register, initial_new_user
from core.models.user.verify import Verify, VerifyCodeException
from core.models.group import invitation_reminder_group
from core.models.invitation import transform_digit, Invitation
from core.models.invitation.consts import INVITER_KEY
from core.models.utils.limit import Limit, LIMIT
from core.models.utils.validator import (
    validate_email, validate_phone, validate_password, AnnotatedValidationMixin)
from jupiter.ext import sentry
from jupiter.views.accounts.utils.password_utils import (
    reset_password, validate_reset_password_asker, send_reset_password_mail)
from jupiter.views.accounts.utils.bind_utils import pre_bind, log_binding
from jupiter.views.accounts.utils.captcha_utils import validate_captcha_text
from jupiter.views.accounts.utils.login_utils import (
    login as _login, login_err_msg_dict)
from jupiter.views.accounts.utils.register_logger import log_register_source
from jupiter.views.accounts.utils.session import login_user, logout_user
from jupiter.integration.limiter import FlexibleLimiter
from core.models.gift import UserLotteryNum


bp = Blueprint('jaccount', __name__, url_prefix='/j/account')
sms_limiter = FlexibleLimiter('1/minute; 4/hour; 8/day')
ip_limiter = FlexibleLimiter('5/minute; 10/hour')


@bp.route('/settings', methods=['POST'])
def settings():
    if not g.user:
        return jsonify(r=False)
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirmed_password = request.form.get('repwd_txt')

    try:
        reset_password(g.user, new_password, confirmed_password, old_password=old_password)
    except PasswordValidationError as e:
        return jsonify(r=False, error=unicode(e))
    else:
        return jsonify(r=True)


@bp.errorhandler(429)
def handler_too_freq_requests(e):
    return jsonify(errors=[{'message': e.description}]), e.code


@bp.route('/register/captcha', methods=['POST'])
def register_mobile_captcha():
    register = RegisterCaptchaForm()
    if register.validate():
        sms_limiter.raise_for_exceeded(
            key=register.mobile.data,
            message=u'{granularity}内只能发送{amount}次验证码，请稍后再试')
        user = register_with_confirm(alias=register.mobile.data,
                                     password=register.mobile.data,
                                     reg_type=ACCOUNT_REG_TYPE.MOBILE)
        if user:
            sms_limiter.hit(register.mobile.data)
            return '', 204
        else:
            return jsonify(errors=[{'message': u'手机号注册失败，T_T'}]), 403

    return jsonify(errors=register.failure), 400


def invitation_register_completed(request, invitee):
    # 新人注册成功
    invitation_reminder_group.add_member(invitee.id_)

    code = request.cookies.get(INVITER_KEY)
    if code:
        inviter_id = transform_digit(code)
        inviter = Account.get(inviter_id)

        if inviter:
            UserLotteryNum.add_by_invite(inviter_id)

            Invitation.add(inviter, invitee, Invitation.Kind.invite_investment)

            @after_this_request
            def set_cookie(response):
                response.set_cookie(key=INVITER_KEY, expires=0)
                return response


@bp.route('/register', methods=['POST'])
def register_mobile():
    register = RegisterForm()
    if register.validate():
        user = Account.get_by_alias(register.mobile.data)
        error = confirm_register(user.id)
        if error == errors.err_ok:
            user = login_user(user, remember=True)
            initial_new_user(user.id_, register.password.data)
            log_register_source(user.id, request)
            invitation_register_completed(request, Account.get(user.id_))
            if user:
                return '', 204
            else:
                return jsonify(errors=[{'message': u'手机号注册失败，T_T'}]), 403
        else:
            return jsonify(errors=[{'message': login_err_msg_dict[error]}]), 400

    return jsonify(errors=register.failure), 400


@bp.route('/request_reset_mobile_user_password_verify', methods=['POST'])
def request_reset_mobile_user_password_verify():
    mobile = request.form.get('mobile')

    l = Limit.get(LIMIT.MOBILE_REG % mobile, timeout=60 * 60, limit=10)
    if l.is_limited():
        return jsonify(r=False, error=u'发送短信过于频繁,请您稍后再试')
    l.touch()

    user = Account.get_by_alias(mobile)
    if not user:
        return jsonify(r=False, error=u'该手机号尚未注册好规划')

    sms = ShortMessage.create(user.mobile, forgot_password_sms, user_id=user.id_)
    sms.send()
    return jsonify(r=True)


@bp.route('/reset_mobile_user_password', methods=['POST'])
def reset_mobile_user_password():
    '''
    /j/account/reset_mobile_user_password
    '''
    # 校验手机号是否对应已存在的用户
    mobile = request.form.get('mobile')
    user = Account.get_by_alias(mobile)
    if not user:
        return jsonify(r=False, error=u'该手机号尚未注册好规划')

    # 校验验证码是否正确
    code = request.form.get('code')
    try:
        v = Verify.validate(user.id_, code, VERIFY_CODE_TYPE.FORGOT_PASSWORD_MOBILE)
        v.delete()
    except VerifyCodeException as e:
        return jsonify(r=False, error=unicode(e))

    # 校验密码是否合法一致
    new_password = request.form.get('new_password')
    confirmed_password = request.form.get('confirmed_password')

    try:
        reset_password(user, new_password, confirmed_password)
    except PasswordValidationError as e:
        return jsonify(r=False, error=unicode(e))
    else:
        return jsonify(r=True)


@bp.route('/forgot_password', methods=['POST'])
def j_forgot_password():
    if g.user:
        return jsonify(r=False), 403

    error = ''
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
                return jsonify(r=True, type='email', alias=alias)
            elif alias_type == ACCOUNT_REG_TYPE.MOBILE:
                return jsonify(r=True, type='mobile', alias=alias)
    return jsonify(r=False, error=error)


@bp.route('/login', methods=['POST'])
def login():
    '''
        login method
    '''
    login_form = LoginForm()
    rsyslog.send(u'login request(%s,%s,%s)' %
                 (login_form.alias.data, login_form.password.data, datetime.now()),
                 tag='login')
    try:
        if login_form.validate():
            res = _login(login_form.alias.data, login_form.password.data, True)
            sentry.captureMessage('Login Result',
                                  extra={'result': res, 'alias': login_form.alias.data})
            rsyslog.send(u'login result --- (%s,%s,%s)' %
                         (login_form.alias.data, res, datetime.now()),
                         tag='login')
            if errors.err_ok == res:
                return '', 204
            else:
                return jsonify(errors=[{
                    'message': login_err_msg_dict[res]}]), 403
        sentry.captureMessage(login_form.failure, extra={'alias': login_form.alias})
        return jsonify(errors=login_form.failure), 400

    except Exception as ex:
        sentry.captureException(ex, extra={'id': login_form.alias, 'pass': 'filtered'})
        rsyslog.send(u'login error --- (%s,%s,%s)' %
                     (login_form.alias.data, ex.message, datetime.now()),
                     tag='login')
        return jsonify(errors=ex.message), 500


@bp.route('/logout', methods=['POST'])
def logout():
    if g.user:
        logout_user()
    return '', 200


BIND_MOBILE_WHITELIST = [
    u'/accounts/settings',
    u'/savings/auth/withdraw',
    u'/savings/auth/channel',
    u'/savings/auth/channel/c02',
    u'/savings/auth/channel/c03',
    u'/profile/auth',
    u'/wallet/auth',
]


@bp.route('/bind_mobile', methods=['POST'])
def bind_mobile():
    if not g.user:
        return jsonify(r=False, error=u'登录会话已过期，请重新登录')

    if g.user.mobile:
        return jsonify(r=False, error=u'您已经绑定了手机号，无需再次绑定')

    # check referer
    if not request.environ.get('HTTP_REFERER'):
        sentry.captureMessage('No HTTP_REFERER when %s visits' % g.user.id)
        return jsonify(r=False, error=u'未知错误，错误代码BM01，请联系客服处理')
    referer = url_parse(request.environ.get('HTTP_REFERER'))

    if not all([referer.scheme == request.scheme,
                referer.netloc == request.host,
                referer.path in BIND_MOBILE_WHITELIST]):
        sentry.captureMessage('Invalid bind request from %s' % g.user.id)
        return jsonify(r=False, error=u'未知错误，错误代码BM02，请联系客服处理')

    mobile = request.form.get('mobile')
    # limit phone
    l = Limit.get(LIMIT.MOBILE_BIND % mobile, timeout=60 * 60, limit=5)
    if l.is_limited():
        return jsonify(r=False, error=u'发送短信过于频繁, 请您稍后再试')
    l.touch()

    # limit ip
    l = Limit.get(LIMIT.IP_MOBILE_BIND % request.remote_addr,
                  timeout=10 * 60, limit=10)
    if l.is_limited():
        return jsonify(r=False, error=u'发送短信过于频繁, 请您稍后再试')
    l.touch()

    try:
        pre_bind(mobile)
    except BindError as e:
        return jsonify(r=False, error=e.args[0])
    else:
        return jsonify(r=True)


@bp.route('/confirm_bind', methods=['POST'])
def confirm_bind():
    if not g.user:
        return jsonify(r=False, error=u'登录会话已过期，请重新登录')

    if g.user.mobile:
        return jsonify(r=False, error=u'您已经绑定了手机号，无需再次绑定')

    mobile = request.form.get('mobile')
    code = request.form.get('code')
    if validate_phone(mobile) != errors.err_ok:
        return jsonify(r=False, error=u'无效的手机号')

    try:
        verify_bind(g.user.id, code)
        confirm_mobile_bind(g.user.id, mobile)
    except BindError as e:
        return jsonify(r=False, error=e.args[0])
    else:
        log_binding(g.user.id, request, mobile)
        return jsonify(r=True)


class RegisterCaptchaForm(Form, AnnotatedValidationMixin):
    mobile = fields.StringField(
        validators=[
            validators.DataRequired(u'请填写您的手机号码')
        ])

    captcha = fields.StringField(
        validators=[
            validators.DataRequired(u'请填写图型验证码'),
            validators.Regexp('\d{4,8}', message=u'请正确填写图型验证码')
        ])

    def validate_mobile(self, field):
        if errors.err_ok != validate_phone(field.data):
            raise validators.StopValidation(message=u'手机号错误')

        user = Account.get_by_alias(field.data)
        if user and not user.need_verify():
            raise validators.StopValidation(message=u'手机号已被注册 试试直接登录吧')

    def validate_captcha(self, field):
        try:
            validate_captcha_text(field.data)
        except CaptchaError as e:
            raise validators.ValidationError(unicode(e))


class RegisterForm(Form, AnnotatedValidationMixin):
    mobile = fields.StringField('mobile', validators=[validators.DataRequired(u'请填写您的手机号码')])
    password = fields.StringField(
        validators=[
            validators.DataRequired(u'请输入密码'),
            validators.Length(min=6, message=u'密码长度太短')
        ])
    captcha = fields.StringField(
        validators=[
            validators.DataRequired(u'请填写图型验证码'),
            validators.Regexp('\d{4,8}', message=u'请正确填写图型验证码')
        ])
    invite_code = fields.StringField('invite_code')
    verify_code = fields.StringField('verify_code', validators=[
        validators.DataRequired(u'请填写手机验证码'),
        validators.Regexp('\d{4,8}', message=u'请正确填写手机验证码')
    ])

    def validate_mobile(self, field):
        mobile = field.data
        error = validate_phone(mobile)
        if error != errors.err_ok:
            raise validators.ValidationError(u'无效的手机号码')
        ip_limiter.raise_for_exceeded(
            key=request.remote_addr,
            message=u'{granularity}内只能发起{amount}次注册，请稍后再试')

        if not Account.get_by_alias(mobile):
            raise validators.ValidationError(u'修改手机号后请重新获取验证码')

        ip_limiter.hit(request.remote_addr)

    def validate_password(self, field):
        error = validate_password(field.data)
        if error != errors.err_ok:
            raise validators.ValidationError(u'密码不符合规则')

    def validate_verify_code(self, field):
        user = Account.get_by_alias(self.mobile.data)
        if user:
            try:
                v = Verify.validate(user.id_, field.data, VERIFY_CODE_TYPE.REG_MOBILE)
                v.delete()
            except VerifyCodeException as e:
                raise validators.ValidationError(unicode(e))


class LoginForm(Form, AnnotatedValidationMixin):
    alias = fields.StringField(validators=[
        validators.DataRequired(u'请填写正确的手机号或邮箱')
    ])
    password = fields.PasswordField(validators=[
        validators.DataRequired(u'请输入密码'),
        validators.Length(min=6, message=u'密码长度太短')
    ])

    def validate_alias(self, field):
        reg_type = get_reg_type_from_alias(field.data)
        if not reg_type:
            raise validators.StopValidation(message=u'手机号或邮箱错误')

        if reg_type == ACCOUNT_REG_TYPE.EMAIL:
            if not errors.err_ok == validate_email(field.data):
                raise validators.StopValidation(message=u'邮箱错误')

        elif reg_type == ACCOUNT_REG_TYPE.MOBILE:
            if not errors.err_ok == validate_phone(field.data):
                return validators.StopValidation(message=u'手机号错误')
