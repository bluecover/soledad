# coding: utf-8

from __future__ import absolute_import, unicode_literals
import random
import string

from flask import request, jsonify, abort
from marshmallow import Schema, fields

from core.models import errors
from core.models.user.account import Account
from core.models.user.verify import Verify, VerifyCodeException
from core.models.user.register import (
    confirm_register, register_with_confirm, initial_new_user)
from core.models.user.change_password import change_password
from core.models.user.consts import ACCOUNT_REG_TYPE, VERIFY_CODE_TYPE
from core.models.profile.identity import Identity
from core.models.sms import ShortMessage
from core.models.sms.kind import forgot_password_sms
from core.models.utils.voucher import VerifyVoucher
from jupiter.integration.limiter import FlexibleLimiter
from ..blueprint import create_blueprint
from ..decorators import require_credentials, require_oauth
from ..fields import MobilePhoneField, PasswordField, PersonRicnField
from ..track import events


bp = create_blueprint('accounts', 'v1', __name__, url_prefix='/accounts')
sms_limiter = FlexibleLimiter('1/minute; 4/hour; 8/day')


@bp.route('/register', methods=['POST'])
@require_credentials
def register():
    """注册新用户（发送短信验证码）

    要使用本接口, 客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.RegisterSchema`
    :response: :class:`.UserSchema`

    :reqheader X-Client-ID: OAuth 2.0 Client ID
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret
    :status 403: 注册被拒
    :status 202: 接受注册，已发出验证码
    """
    register_schema = RegisterSchema(strict=True)
    user_schema = UserSchema(strict=True)

    result = register_schema.load(request.get_json(force=True))
    mobile_phone = result.data['mobile_phone']

    sms_limiter.raise_for_exceeded(
        key=mobile_phone,
        message='{granularity}内只能发送{amount}次验证码，请稍后再试')

    user = register_with_confirm(
        alias=mobile_phone,
        password=mobile_phone,
        reg_type=ACCOUNT_REG_TYPE.MOBILE)

    if user:
        sms_limiter.hit(key=mobile_phone)
        return jsonify(success=True, data=user_schema.dump(user).data), 202
    else:
        return jsonify(success=False, messages={
            'mobile_phone': ['该手机号已被注册，请直接登录或使用其他号码注册']
        }), 403


@bp.route('/register/verify', methods=['POST'])
@require_credentials
def register_verify():
    """注册新用户（验证短信验证码）

    要使用本接口, 客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.RegisterVerifySchema`
    :response: :class:`.UserSchema`

    :reqheader X-Client-ID: OAuth 2.0 Client ID
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret
    :status 403: 注册被拒
    :status 200: 注册成功
    """
    register_verify_schema = RegisterVerifySchema(strict=True)
    user_schema = UserSchema(strict=True)

    result = register_verify_schema.load(request.get_json(force=True))
    user = Account.get_by_alias(result.data['mobile_phone'])
    if not user:
        return jsonify(success=False, messages={
            'mobile_phone': ['该手机号与验证码不符，请确认后重试']
        }), 403

    try:
        v = Verify.validate(
            user.id_, result.data['sms_code'], VERIFY_CODE_TYPE.REG_MOBILE)
        v.delete()
    except VerifyCodeException as e:
        return jsonify(success=False, messages={'sms_code': [unicode(e)]}), 403

    error_tuple = confirm_register(user.id_)
    if error_tuple != errors.err_ok:
        return jsonify(success=False, messages={
            'mobile_phone': ['用户状态异常，请联系客服']
        }), 403
    initial_new_user(user.id_, result.data['password'])
    events['register_success'].send(request, user_id=user.id_)

    return jsonify(success=True, data=user_schema.dump(user).data)


@bp.route('/reset_password', methods=['POST'])
@require_credentials
def reset_password():
    """重置密码（发送短信验证码）

    要使用本接口, 客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.ResetPasswordSchema`
    :response: :class:`.UserSchema`

    :reqheader X-Client-ID: OAuth 2.0 Client ID
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret
    :status 403: 账号不存在
    :status 200: 已发出验证码
    """
    reset_password_schema = ResetPasswordSchema(strict=True)
    user_schema = UserSchema(strict=True)

    result = reset_password_schema.load(request.get_json(force=True))
    mobile_phone = result.data['mobile_phone']

    sms_limiter.raise_for_exceeded(
        key=mobile_phone,
        message='{granularity}内只能发送{amount}次验证码，请稍后再试')

    user = Account.get_by_alias(mobile_phone)
    if user:
        sms = ShortMessage.create(mobile_phone, forgot_password_sms, user_id=user.id_)
        sms.send()
        sms_limiter.hit(key=mobile_phone)
        return jsonify(success=True, data=user_schema.dump(user).data)
    else:
        abort(403, u'账号不存在')


@bp.route('/reset_password_sms_verify', methods=['POST'])
@require_credentials
def reset_password_sms_verify():
    """重置密码（验证短信验证码）

    要使用本接口, 客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.ResetPasswordSmsVerifySchema`
    :response: :class:`.IdentityVoucherSchema`

    :reqheader X-Client-ID: OAuth 2.0 Client ID
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret
    :status 403: 验证码错误或账号不存在
    :status 200: 验证通过
    """
    reset_password_sms_verify_schema = ResetPasswordSmsVerifySchema(strict=True)
    identity_voucher_schema = IdentityVoucherSchema(strict=True)

    result = reset_password_sms_verify_schema.load(request.get_json(force=True))
    user = Account.get_by_alias(result.data['mobile_phone'])
    if not user:
        abort(403, u'账号不存在')
    try:
        v = Verify.validate(
            user.id_, result.data['sms_code'], VERIFY_CODE_TYPE.FORGOT_PASSWORD_MOBILE)
        v.delete()
        identity = Identity.get(user.id_)
        confirmed_code = VerifyVoucher(user.id_)
        confirmed_code.voucher = ''.join(random.sample(string.digits, 6))
        data = {'confirmed_code': confirmed_code.voucher,
                'uid': user.id_,
                'masked_name': identity}
        return jsonify(success=True, data=identity_voucher_schema.dump(data).data)
    except VerifyCodeException as e:
        abort(403, unicode(e))


@bp.route('/reset_password_identity_verify', methods=['POST'])
@require_credentials
def reset_password_identity_verify():
    """重置密码（验证身份信息）

    要使用本接口, 客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.IdentityVerifySchema`
    :response: :class:`.IdentityVoucherSchema`

    :reqheader X-Client-ID: OAuth 2.0 Client ID
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret
    :status 403: 身份验证失败
    :status 200: 身份验证成功
    """
    check_identity_schema = IdentityVerifySchema(strict=True)
    identity_voucher_schema = IdentityVoucherSchema(strict=True)

    result = check_identity_schema.load(request.get_json(force=True))
    confirmed_code = VerifyVoucher(result.data['uid'])
    if result.data['confirmed_code'] != confirmed_code.voucher:
        abort(403, u'未验证手机号，请先验证手机号')
    identity = Identity.get(result.data['uid'])
    if not identity:
        abort(403, u'未绑定身份信息')
    if identity.person_ricn == result.data['person_ricn']:
        confirmed_code.voucher = ''.join(random.sample(string.digits, 6))
        identity_data = {'confirmed_code': confirmed_code.voucher,
                         'uid': identity.id_,
                         'identity': identity}
        return jsonify(success=True, data=identity_voucher_schema.dump(identity_data).data)
    else:
        abort(403, u'您输入的身份证号与账户不匹配')


@bp.route('/reset_password_verify', methods=['POST'])
@require_credentials
def reset_password_verify():
    """重置密码（验证新密码）

    要使用本接口, 客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.SetNewPasswordSchema`
    :response: :class:`.UserSchema`

    :reqheader X-Client-ID: OAuth 2.0 Client ID
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret
    :status 403: 重置密码失败
    :status 200: 重置密码成功
    """
    set_new_password_schema = SetNewPasswordSchema(strict=True)
    user_schema = UserSchema(strict=True)

    result = set_new_password_schema.load(request.get_json(force=True))
    user = Account.get(result.data['uid'])
    if not user:
        abort(403, u'账号不存在')
    confirmed_code = VerifyVoucher(result.data['uid'])
    if result.data['confirmed_code'] != confirmed_code.voucher:
        abort(403, u'未验证身份或手机')
    if change_password(result.data['uid'], result.data['new_password']):
        confirmed_code.disable()
        return jsonify(success=True, data=user_schema.dump(user).data)
    abort(403, u'修改密码失败')


@bp.route('/change_password', methods=['POST'])
@require_oauth(['user_info'])
def change_user_password():
    """ 修改密码（验证新密码）

    要使用本接口, 客户端必须有权以 ``user_info`` 作为 scope.

    :request: :class:`.ChangePasswordSchema`
    :response: :class:`.UserSchema`

    :reqheader X-Client-ID: OAuth 2.0 Client ID
    :reqheader X-Client-Secret: OAuth 2.0 Client Secret
    :status 403: 修改密码失败
    :status 200: 修改密码成功
    """
    change_password_schema = ChangePasswordSchema(strict=True)
    user_schema = UserSchema(strict=True)

    result = change_password_schema.load(request.get_json(force=True))
    user = Account.get(request.oauth.user.id_)
    if not user:
        abort(403, u'账号不存在')
    if not user.verify_password(result.data['old_password']):
        abort(403, '原密码输入有误')
    if user.verify_password(result.data['new_password']):
        abort(403, '新密码与原密码一致，请重新输入')
    if change_password(user.id_, result.data['new_password']):
        return jsonify(success=True, data=user_schema.dump(user).data)
    else:
        abort(403, u'修改密码失败')


class RegisterSchema(Schema):
    """注册用户 - 发送短信验证码的请求实体."""

    #: :class:`str` 用户手机号
    mobile_phone = MobilePhoneField(required=True)


class RegisterVerifySchema(Schema):
    """注册用户 - 确认短信验证码的请求实体."""

    #: :class:`str` 用户手机号
    mobile_phone = MobilePhoneField(required=True)
    #: :class:`str` 用户密码
    password = PasswordField(required=True)
    #: :class:`str` 用户收到的短信验证码
    sms_code = fields.String(required=True)


class UserSchema(Schema):
    """用户 (好规划帐号) 实体."""

    #: :class:`str` 用户唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 昵称
    screen_name = fields.String(attribute='screen_ident')
    #: :class:`~datetime.date` 注册日期
    created_at = fields.Date(attribute='creation_date', required=True)


class IdentityVerifySchema(Schema):
    """重置密码 - 身份验证请求实体"""

    #: :class:`str` 用户唯一 ID
    uid = fields.String(required=True)
    #: :class:`str` 账户拥有者身份证号
    person_ricn = PersonRicnField(attribute='person_ricn')
    #: :class:`str` 校验步骤凭证
    confirmed_code = fields.String(required=True)


class MaskedNameSchema(Schema):
    """重置密码 - 姓名实体"""

    #: :class:`str` 姓名
    #:
    #: .. note:: 返回时已处理为如：**忌
    masked_name = fields.String(attribute='masked_name')


class IdentityVoucherSchema(Schema):
    """重置密码 - 带验证凭证的身份实体"""

    #: :class:`str` 用户ID
    uid = fields.String(required=True)
    #: :class:`.MaskedNameSchema` 姓名
    masked_name = fields.Nested(MaskedNameSchema)
    #: :class:`str` 步骤校验凭证
    confirmed_code = fields.String(required=True)


class ResetPasswordSchema(Schema):
    """重置密码 - 发送短信验证码的请求实体."""

    #: :class:`str` 用户手机号
    mobile_phone = MobilePhoneField(required=True)


class ResetPasswordSmsVerifySchema(Schema):
    """重置密码 - 确认短信密码请求实体."""

    #: :class:`str` 用户手机号
    mobile_phone = MobilePhoneField(required=True)
    #: :class:`str` 用户收到的短信验证码
    sms_code = fields.String(required=True)


class SetNewPasswordSchema(Schema):
    """重置密码请求实体"""

    #: :class:`str` 用户唯一 ID
    uid = fields.String(required=True)
    #: :class:`str` 用户新密码
    new_password = PasswordField(required=True)
    #: :class:`str` 步骤校验凭证
    confirmed_code = fields.String()


class ChangePasswordSchema(Schema):
    """修改密码请求实体"""

    #: :class:`str` 用户旧密码
    old_password = fields.String(required=True)
    #: :class:`str` 用户新密码
    new_password = PasswordField(required=True)
