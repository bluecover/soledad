# coding: utf-8

from __future__ import absolute_import, unicode_literals

from flask import request, jsonify, abort, g
from marshmallow import Schema, fields, pre_dump
from gb2260 import Division

from core.models.errors import BindError
from core.models.user.account import Account
from core.models.user.bind import request_bind, verify_bind, confirm_bind
from core.models.profile.identity import Identity, IdentityBindingError
from core.models.profile.bankcard import (
    BankCardManager, CardConflictError, BankConflictError)
from core.models.hoard.account import YixinAccount
from core.models.hoard.zhiwang.account import ZhiwangAccount
from core.models.hoard.xinmi import XMAccount
from core.models.hoard.zhiwang.utils import iter_banks as iter_banks_of_zw
from core.models.hoard.xinmi.utils import iter_banks as iter_banks_of_xm
from core.models.hoarder.utils import iter_banks as iter_banks_of_sxb
from core.models.hoarder.bankcard_binding import is_bound_bankcard as is_bound_sxb_bankcard
from core.models.hoarder.vendor import Vendor, Provider
from core.models.bank import Partner
from core.models.wallet.utils import iter_banks as iter_banks_of_zs
from core.models.wallet.providers import zhongshan
from core.models.wallet._bankcard_binding import is_bound_bankcard
from core.models.notification import Notification
from core.models.welfare import CouponManager, FirewoodWorkflow
from core.models.hoarder.account import Account as NewAccount
from ..blueprint import create_blueprint, conditional_for
from ..fields import (
    MobilePhoneField, PersonNameField, PersonRicnField, BankCardNumberField,
    BankIDField, DivisionIDField)
from ..decorators import require_oauth
from .accounts import UserSchema
from .data import BankSchema


bp = create_blueprint('profile', 'v1', __name__, url_prefix='/profile')


@bp.before_request
@require_oauth(['basic'])
def initialize_bankcard_manager():
    if hasattr(request, 'oauth'):
        g.bankcard_manager = BankCardManager(request.oauth.user.id_)
        g.firewood_flow = FirewoodWorkflow(request.oauth.user.id_)
        g.coupon_manager = CouponManager(request.oauth.user.id_)
    else:
        g.bankcard_manager = None


@bp.route('/mine', methods=['GET'])
@require_oauth(['basic'])
def mine():
    """用户状况.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回 :class:`~jupiter.views.api.v1.profile.ProfileSchema`
    """
    profile_schema = ProfileSchema(strict=True)

    identity = Identity.get(request.oauth.user.id_)
    yixin_account = YixinAccount.get_by_local(request.oauth.user.id_)
    zw_account = ZhiwangAccount.get_by_local(request.oauth.user.id_)
    xm_account = XMAccount.get_by_local(request.oauth.user.id_)
    coupon_manager = CouponManager(request.oauth.user.id_)

    sxb_account = None
    sxb_vendor = Vendor.get_by_name(Provider.sxb)
    if sxb_vendor:
        sxb_account = NewAccount.get(sxb_vendor.id_, request.oauth.user.id_)

    data = {
        'user': request.oauth.user,
        'has_mobile_phone': bool(request.oauth.user.mobile),
        'has_identity': bool(identity),
        'has_yixin_account': bool(yixin_account),
        'has_zw_account': bool(zw_account),
        'has_xm_account': bool(xm_account),
        'has_sxb_account': bool(sxb_account),
        'coupon_count': len(coupon_manager.available_coupons),
        'is_old_user_of_yrd': False,
        'masked_person_name': identity.masked_name if identity else '',
        'red_packets': g.firewood_flow.balance
    }

    return jsonify(success=True, data=profile_schema.dump(data).data)


@bp.route('/has-new-notifications', methods=['GET'])
@require_oauth(['user_info'])
def has_new_notifications():
    """用户通知.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回 :class:`NewNotificationCheckSchema`
    """
    schema = NewNotificationCheckSchema(strict=True)
    data = {
        'has_new_notification': bool(
            Notification.get_multi_unreads_by_user(request.oauth.user.id_))}
    return jsonify(success=True, data=schema.dump(data).data)


@bp.route('/mobile', methods=['POST'])
@require_oauth(['user_info'])
def bind_mobile():
    """绑定手机号 - 发送短信验证码.

    :request: :class:`.MobilePhoneSchema`
    :response: :class:`.UserSchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 短信验证码发送成功
    """
    mobile_phone_schema = MobilePhoneSchema(strict=True)
    user_schema = UserSchema(strict=True)
    result = mobile_phone_schema.load(request.get_json(force=True))
    mobile_phone = result.data['mobile_phone']

    check_before_binding(request.oauth.user, mobile_phone)
    request_bind(request.oauth.user.id_, mobile_phone)

    return jsonify(
        success=True, data=user_schema.dump(request.oauth.user).data)


@bp.route('/mobile/verify', methods=['POST'])
@require_oauth(['user_info'])
def bind_mobile_verify():
    """绑定手机号 - 确认短信验证码.

    :request: :class:`.MobileVerifySchema`
    :response: :class:`.UserSchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 绑定成功
    :status 403: 绑定失败
    """
    mobile_verify_schema = MobileVerifySchema(strict=True)
    user_schema = UserSchema(strict=True)
    result = mobile_verify_schema.load(request.get_json(force=True))
    mobile_phone = result.data['mobile_phone']
    sms_code = result.data['sms_code']

    check_before_binding(request.oauth.user, mobile_phone)

    try:
        verify_bind(request.oauth.user.id_, sms_code)
        confirm_bind(request.oauth.user.id_, mobile_phone)
    except BindError as e:
        return jsonify(
            success=False, messages={'mobile_phone': [e.args[0]]}), 403
    else:
        return jsonify(
            success=True, data=user_schema.dump(request.oauth.user).data)


@bp.route('/identity', methods=['POST'])
@require_oauth(['user_info'])
def bind_identity():
    """绑定实名信息.

    :request: :class:`.IdentitySchema`
    :response: :class:`.IdentitySchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 绑定成功
    :status 400: 姓名或身份证号不合法
    :status 403: 绑定被拒
    """

    identity_schema = IdentitySchema(strict=True)
    result = identity_schema.load(request.get_json(force=True))

    if Identity.get(request.oauth.user.id_):
        abort(403, '该账号已绑定身份信息，无法重复绑定')

    try:
        identity = Identity.save(
            user_id=request.oauth.user.id_,
            person_name=result.data['person_name'],
            person_ricn=result.data['person_ricn'])
    except IdentityBindingError as e:
        abort(403, unicode(e))

    return jsonify(success=True, data=identity_schema.dump(identity).data)


@bp.route('/bankcards', methods=['GET'])
@require_oauth(['user_info'])
def bankcards():
    """用户已绑的银行卡列表.

    :query partner: 可选参数, 按合作方支持情况限制返回结果. 目前可为:

                    - ``"zw"`` 指旺 (攒钱助手)
                    - ``"xm"`` 新米 (攒钱助手)
                    - ``"sxb"`` 随心宝 (攒钱助手)
                    - ``"zs"`` 中山证券 (零钱包)

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :reqheader If-None-Match: 客户端缓存的 ETag
    :resheader ETag: 客户端可缓存的 ETag
    :status 304: 客户端缓存未过期, 无需返回数据
    :status 200: 返回 :class:`.BankCardSchema` 列表
    """
    bankcard_schema = BankCardSchema(strict=True, many=True)
    partner = request.args.get('partner', type=Partner)
    bankcard_list = g.bankcard_manager.get_all()
    if partner is not None:
        bankcard_list = [
            bankcard for bankcard in bankcard_list
            if partner in bankcard.bank.available_in]
        if partner is Partner.zs:
            bankcard_list = [
                bankcard for bankcard in bankcard_list
                if is_bound_bankcard(bankcard, zhongshan)]

    inject_bankcard_amount_limit(partner, bankcard_list)

    if partner:
        if partner is Partner.sxb:
            vendor = Vendor.get_by_name(Provider.sxb)
            for bankcard in bankcard_list:
                if is_bound_sxb_bankcard(bankcard, vendor):
                    bankcard.is_default = True
                else:
                    bankcard.is_default = False

    bankcard_data = bankcard_schema.dump(bankcard_list).data
    conditional_for('{0}#{1}#{2}#{3}'.format(
        item['uid'], item['amount_limit'], item['is_bound_in_wallet'],
        item['is_default']) for item in bankcard_data)

    return jsonify(success=True, data=bankcard_data)


@bp.route('/bankcards', methods=['POST'])
@require_oauth(['user_info'])
def bind_bankcard():
    """绑定新的银行卡或更新已有银行卡.
    :query partner: 可选参数, 按合作方支持情况限制返回结果. 目前可为:

                    - ``"zw"`` 指旺 (攒钱助手)
                    - ``"xm"`` 指旺 (攒钱助手)
                    - ``"zs"`` 中山证券 (零钱包)


    :request: :class:`.BankCardRequestSchema`
    :response: :class:`.BankCardSchema`
    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 绑定或更新成功
    :status 403: 绑定被拒
    """
    bankcard_schema = BankCardSchema(strict=True)
    bankcard_request_schema = BankCardRequestSchema(strict=True)
    partner = request.args.get('partner', type=Partner)
    data = bankcard_request_schema.load(request.get_json(force=True)).data
    result = {
        'mobile_phone': data['mobile_phone'],
        'card_number': data['bankcard_number'],
        'bank_id': data['bank_id'],
        'city_id': data['division_id'],
        'province_id': Division.search(data['division_id']).province.code,
        'local_bank_name': data.get('local_bank_name'),
    }
    #: 针对零钱包，若用户已经绑定银行卡，只返回已绑定卡
    if partner is Partner.zs:
        bankcard_list = [
            bankcard for bankcard in g.bankcard_manager.get_all()
            if is_bound_bankcard(bankcard, zhongshan)]
        if bankcard_list:
            abort(403, u'零钱包暂时只支持绑定一张银行卡, 详情见通知中心')
    try:
        bankcard = g.bankcard_manager.create_or_update(**result)
        inject_bankcard_amount_limit(partner, [bankcard])
    except (BankConflictError, CardConflictError) as e:
        return abort(403, unicode(e))

    return jsonify(success=True, data=bankcard_schema.dump(bankcard).data)


def check_before_binding(current_user, mobile_phone):
    if current_user.mobile:
        abort(403, '该账号已绑定手机号，无法重复绑定')
    user = Account.get_by_alias(mobile_phone)
    if user and user.is_normal_account():
        abort(403, '该手机号已被其他账号绑定，请更换号码重试')


def inject_bankcard_amount_limit(partner, bankcard_list):
    for item in bankcard_list:
        if partner is Partner.zw:
            bank_dict = dict(iter_banks_of_zw(request.oauth.user.id_))
        elif partner is Partner.xm:
            bank_dict = dict(iter_banks_of_xm(request.oauth.user.id_))
        elif partner is Partner.zs:
            bank_dict = dict(iter_banks_of_zs(request.oauth.user.id_))
        elif partner is Partner.sxb:
            bank_dict = dict(iter_banks_of_sxb(request.oauth.user.id_))
        else:
            bank_dict = {}
        item._amount_limit = bank_dict.get(item.bank)


class NewNotificationCheckSchema(Schema):
    """用户通知"""

    #: :class:`bool` 是否有新通知
    has_new_notification = fields.Boolean()


class MobilePhoneSchema(Schema):
    """手机号绑定 - 发送短信验证码请求实体."""

    #: :class:`str` 手机号
    mobile_phone = MobilePhoneField(required=True)


class MobileVerifySchema(Schema):
    """手机号绑定 - 确认短信验证码请求实体."""

    #: :class:`str` 手机号
    mobile_phone = MobilePhoneField(required=True)
    #: :class:`str` 收到的短信验证码
    sms_code = fields.String(required=True)


class IdentitySchema(Schema):
    """身份证绑定请求实体."""

    #: :class:`str` 账户拥有者真实姓名
    person_name = PersonNameField(required=True)
    #: :class:`str` 账户拥有者身份证号
    person_ricn = PersonRicnField(required=True)


class BankCardSchema(Schema):
    """银行卡实体."""

    #: :class:`str` 银行卡唯一 ID
    uid = fields.String(attribute='id_')
    #: :class:`str` 卡号
    card_number = fields.String(attribute='display_card_number')
    #: :class:`str` 银行预留手机号
    mobile_phone = fields.String(attribute='display_mobile_phone')
    #: :class:`BankSchema` 银行卡开户银行
    bank = fields.Nested(BankSchema)
    #: :class:`str` 开户支行名称
    local_bank_name = fields.String()
    #: :class:`str` 开户所在省的行政区划 ID
    province_id = fields.String()
    #: :class:`bool` 是否是默认使用的银行卡
    is_default = fields.Boolean()
    #: :class:`int` 银行卡限额
    amount_limit = fields.Decimal(attribute='_amount_limit')
    #: :class:`bool` 是否绑定了零钱包
    is_bound_in_wallet = fields.Boolean()

    @pre_dump
    def check_for_wallet(self, data):
        data.is_bound_in_wallet = bool(is_bound_bankcard(data, zhongshan))
        return data


class BankCardRequestSchema(Schema):
    """银行卡绑定请求实体."""

    #: :class:`str` 卡号
    bankcard_number = BankCardNumberField(required=True)
    #: :class:`str` 银行预留手机号
    mobile_phone = MobilePhoneField(required=True)
    #: :class:`int` 银行卡开户银行的唯一 ID
    bank_id = BankIDField(required=True)
    #: :class:`int` 银行卡开户地行政区划 (地级市) ID
    division_id = DivisionIDField(required=True)


class ProfileSchema(Schema):
    """用户信息实体."""

    #: :class:`.UserSchema` 用户实体
    user = fields.Nested(UserSchema)
    #: :class:`bool` 是否已经绑定了手机号 (实名验证必备条件)
    has_mobile_phone = fields.Boolean(required=True)
    #: :class:`bool` 是否已经绑定了身份证号 (实名验证必备条件)
    has_identity = fields.Boolean(required=True)
    #: :class:`bool` 是否已经绑定了宜人贷帐号
    has_yixin_account = fields.Boolean(required=True)
    #: :class:`bool` 是否已经绑定了指旺帐号
    has_zw_account = fields.Boolean(required=True)
    #: :class:`bool` 是否已经绑定了新米帐号
    has_xm_account = fields.Boolean(required=True)
    #: :class:`bool` 是否已经绑定了随心宝账户
    has_sxb_account = fields.Boolean(required=True)
    #: :class:`int` 已拥有的礼券数目
    coupon_count = fields.Integer(required=True)
    #: :class:`bool` 用户是否为老用户
    is_old_user_of_yrd = fields.Boolean()
    #: :class:`str` 用户真实姓名
    masked_person_name = fields.String()
    #: :class:`~decimal.Decimal` 用户红包金额
    red_packets = fields.Decimal(places=2)
