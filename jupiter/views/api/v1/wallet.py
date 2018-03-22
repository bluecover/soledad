# coding: utf-8

from __future__ import absolute_import, unicode_literals

import decimal
import datetime

from marshmallow import Schema, fields, pre_dump
from flask import g, abort, jsonify, request, url_for
from zslib.errors import BusinessError

from jupiter.ext import sentry
from core.models.utils import round_half_up
from core.models.profile.bankcard import BankCardManager
from core.models.wallet import PublicDashboard, UserDashboard
from core.models.wallet.providers import zhongshan
from core.models.wallet.profit import WalletProfit
from core.models.wallet.annual_rate import WalletAnnualRate, WalletAnnualRateList
from core.models.wallet.account import WalletAccount
from core.models.wallet.utils import get_value_date, describe_business_error
from core.models.wallet.facade import (
    CreateAccountFlow, TransactionFlow, UnboundBankcardError, BankSuspendError, WalletSuspendError)
from core.models.wallet.consts import (
    SMS_BINDING_BANKCARD, SMS_PURCHASE, SMS_REDEEMING, SMS_CODE_INCORECT_FOR_TRANSACTION,
    SMS_CODE_INCORECT_FOR_BINDING)
from core.models.wallet.transaction import WalletTransaction
from ..blueprint import create_blueprint
from .profile import BankCardSchema
from ..decorators import require_oauth


bp = create_blueprint('wallet', 'v1', __name__, url_prefix='/wallet')


@bp.before_request
@require_oauth(['wallet_r'])
def initialize_managers():
    if hasattr(request, 'oauth'):
        g.bankcards = BankCardManager(request.oauth.user.id_)
        g.wallet_provider = zhongshan
        g.wallet_account = WalletAccount.get_or_add(
            request.oauth.user, g.wallet_provider)


@bp.errorhandler(BusinessError)
def handle_business_errors(error):
    description = describe_business_error(error, sentry)
    messages = {'_': [description]}
    return jsonify(success=False, messages=messages), 403


@bp.errorhandler(BankSuspendError)
@bp.errorhandler(WalletSuspendError)
def handle_suspend_error(error):
    return jsonify(success=False, messages={'_': [error.args[0]]}), 403


@bp.errorhandler(UnboundBankcardError)
def handle_unbound_bankcard_errors(error):
    messages = {'_': ['零钱包服务已绑定其他银行卡，请重新选择']}
    return jsonify(success=False, messages=messages), 403


@bp.route('/mine', methods=['GET'])
@require_oauth(['wallet_r'])
def mine():
    """用户信息, 包含历史收益数据等.

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :status 200: 返回 :class:`.ProfileSchema`
    """
    profile_schema = ProfileSchema(strict=True)
    profile = UserDashboard.today(g.wallet_account)
    return jsonify(success=True, data=profile_schema.dump(profile).data)


@bp.route('/dashboard', methods=['GET'])
def dashboard():
    """零钱包年化收益率、万份收益等信息.

    :status 200: 返回 :class:`.DashboardSchema`
    """
    dashboard_schema = DashboardSchema(strict=True)
    dashboard = PublicDashboard.today()
    return jsonify(success=True, data=dashboard_schema.dump(dashboard).data)


@bp.route('/bankcard/<int:bankcard_id>/verify', methods=['POST'])
@require_oauth(['wallet_w'])
def verify_bankcard(bankcard_id):
    """零钱包绑卡

    :request: :class:`.BankcardRequestSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 绑定或更新成功,  返回 :class:`.BankCardSchema`
    :status 403: 绑定被拒
    """
    bankcard = obtain_bankcard(bankcard_id)
    bankcard_schema = BankCardSchema(strict=True)
    flow = CreateAccountFlow(request.oauth.user.id_, bankcard.id_)
    bankcard_request_schema = BankcardRequestSchema(strict=True)
    result = bankcard_request_schema.load(request.get_json())
    sms_code = result.data.get('sms_code')

    if sms_code:
        try:
            if flow.need_to_create():
                flow.create_account(sms_code)
            else:
                flow.bind_bankcard(sms_code)
        except BusinessError as e:
            if e.kind is BusinessError.kinds.sms_code_incorrect:
                abort(403, SMS_CODE_INCORECT_FOR_BINDING)
            raise
    else:
        flow.send_sms(SMS_BINDING_BANKCARD, bankcard=bankcard)

    return jsonify(success=True, data=bankcard_schema.dump(bankcard).data)


@bp.route('/deposit', methods=['POST'])
@require_oauth(['wallet_w'])
def deposit():
    """申购份额 (存钱).

    :request: :class:`.TransactionsRequestSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 支付成功, 返回 :class:`.TransactionResultSchema`
    :status 403: 申购失败
    """
    transaction_request_schema = TransactionsRequestSchema(strict=True)
    transaction_result_schema = TransactionResultSchema(strict=True)
    result = transaction_request_schema.load(request.get_json(force=True))
    bankcard = obtain_bankcard(result.data['bankcard_id'])
    sms_code = result.data.get('sms_code')
    amount = result.data['amount']

    flow = TransactionFlow(request.oauth.user.id_, bankcard.id_)
    flow.raise_for_bank_suspend('purchase')
    if sms_code:
        try:
            transaction = flow.purchase(sms_code, amount)
            transaction_result = transaction_result_schema.dump(transaction).data
        except BusinessError as e:
            if e.kind is BusinessError.kinds.sms_code_incorrect:
                abort(403, SMS_CODE_INCORECT_FOR_TRANSACTION)
            raise
    else:
        flow.send_sms(SMS_PURCHASE, amount=amount)
        transaction_result = None

    return jsonify(success=True, data=transaction_result)


@bp.route('/withdraw', methods=['POST'])
@require_oauth(['wallet_w'])
def withdraw():
    """赎回份额 (取钱).

    :request: :class:`.TransactionsRequestSchema`

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 支付成功, 返回 :class:`.TransactionResultSchema`
    :status 403: 赎回失败
    """
    transaction_request_schema = TransactionsRequestSchema(strict=True)
    transaction_result_schema = TransactionResultSchema(strict=True)
    result = transaction_request_schema.load(request.get_json(force=True))
    bankcard = obtain_bankcard(result.data['bankcard_id'])
    sms_code = result.data.get('sms_code')
    amount = result.data['amount']
    # TODO 赎回限额临时限制
    if amount > 50000:
        abort(403, '最高单笔取回上限为5万元，如有大额赎回请分多笔进行')

    flow = TransactionFlow(request.oauth.user.id_, bankcard.id_)
    flow.raise_for_bank_suspend('redeem')
    if sms_code:
        try:
            transaction = flow.redeem(sms_code, amount)
            transaction_result = transaction_result_schema.dump(transaction).data
        except BusinessError as e:
            if e.kind is BusinessError.kinds.sms_code_incorrect:
                abort(403, SMS_CODE_INCORECT_FOR_TRANSACTION)
            raise
    else:
        flow.send_sms(SMS_REDEEMING, amount=amount)
        transaction_result = None

    return jsonify(success=True, data=transaction_result)


@bp.route('/transactions', methods=['GET'])
@require_oauth(['wallet_r'])
def transactions():
    """用户历史交易记录.

    :reqheader Authorization: OAuth 2.0 Bearer Token

    :status 200: 返回 :class:`.TransactionSchema`
    :query offset: 可选参数, 开始条数，按交易列表请求数限制返回结果.
    :query count: 可选参数, 每页数量，按交易列表请求数限制返回结果.
    """
    transaction_schema = TransactionSchema(strict=True, many=True)
    offset = request.args.get('offset', type=int, default=0)
    count = request.args.get('count', type=int, default=20)
    ids = WalletTransaction.get_ids_by_account(g.wallet_account.id_)
    transactions = WalletTransaction.get_multi(ids[offset:offset + count])
    transaction_data = transaction_schema.dump(transactions).data
    return jsonify(success=True, data=transaction_data)


@bp.route('/spec', methods=['GET'])
@require_oauth(['wallet_r'])
def spec():
    """购买金额限制.

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回  :class:`.SpecSchema`
    """
    spec_schema = SpecSchema(strict=True)
    value_date = get_value_date(datetime.datetime.now())
    spec_data = {'amount_min': decimal.Decimal(1),
                 'amount_max': decimal.Decimal(50000),
                 'amount_accurate': decimal.Decimal(0.01),
                 'expected_value_date': value_date,
                 'expected_credited_date': datetime.date.today(),
                 'profit_credited_date': value_date + datetime.timedelta(days=1),
                 'agreement_url': url_for('wallet.landing.agreement', _external=True)}
    return jsonify(success=True, data=spec_schema.dump(spec_data).data)


@bp.route('/mine/profit', methods=['GET'])
@require_oauth(['wallet_r'])
def profit():
    """累积收益

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回  :class:`.ProfitItemSchema`
    :query offset: 可选参数, 开始条数，按请求数限制返回结果.
    :query count: 可选参数, 每页数量，按请求数限制返回结果.
    """
    profit_schema = ProfitItemSchema(strict=True, many=True)
    offset = request.args.get('offset', type=int, default=0)
    count = request.args.get('count', type=int, default=20)
    ids = WalletProfit.get_ids_by_account(g.wallet_account.id_)[::-1]
    items = WalletProfit.get_multi(ids[offset:offset + count])
    return jsonify(success=True, data=profit_schema.dump(items).data)


@bp.route('/dashboard/annual-rates', methods=['GET'])
@require_oauth(['wallet_r'])
def annual_rate():
    """万份收益

    :reqheader Authorization: OAuth 2.0 Bearer Token
    :status 200: 返回  :class:`.AnnualRateListSchema`
    :query offset: 可选参数, 开始条数，按交易列表请求数限制返回结果.
    :query count: 可选参数, 每页数量，按交易列表请求数限制返回结果.
    """
    annual_rate_schema = AnnualRateListSchema(strict=True)
    offset = request.args.get('offset', type=int, default=0)
    count = request.args.get('count', type=int, default=20)
    ids = (WalletAnnualRate.get_ids_by_date_range(
        date_from=datetime.date.today() - datetime.timedelta(days=30),
        date_to=datetime.date.today(), fund_code=g.wallet_provider.fund_code))
    annual_rate_list = WalletAnnualRateList(ids)
    items = annual_rate_list.get_multi(offset, offset + count)
    average = annual_rate_list.average()
    data = {'items': items,
            'average_annual_rate': round_half_up(average.annual_rate, 2),
            'average_ttp': round_half_up(average.ttp, 2)}
    return jsonify(success=True, data=annual_rate_schema.dump(data).data)


def obtain_bankcard(bankcard_id):
    # TODO 重复代码之后统一整理下

    bankcard = g.bankcards.get(bankcard_id)
    if not bankcard:
        abort(400, '信息已过期, 请刷新页面重试')
    if g.wallet_provider.bank_partner not in bankcard.bank.available_in:
        abort(400, '不支持所选的银行卡')
    return bankcard


class AnnualRateItem(Schema):
    """指定日期的年化收益率"""

    #: :class:`~datetime.date` 收益日期
    date = fields.Date()
    #: :class:`~decimal.Decimal` 每日年化收益率
    annual_rate = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 万份收益(元)
    ttp = fields.Decimal(places=2, attribute='ten_thousand_pieces_income')


class ProfitItemSchema(Schema):
    """指定日期累积收益"""

    #: :class:`~datetime.date` 收益日期
    date = fields.Date()
    #: :class:`~decimal.Decimal` 累积收益(元)
    profit = fields.Decimal(attribute='amount', places=2)


class AnnualRateListSchema(Schema):
    """年化收益"""

    #: :class:`list` of :class:`.AnnualRateItem` 年化收益信息列表
    items = fields.Nested(AnnualRateItem, many=True)
    #: :class:`~decimal.Decimal` 平均年化收益
    average_annual_rate = fields.Decimal(places=2)
    #: :class:`.~decimal.Decimal` 平均万份收益
    average_ttp = fields.Decimal(places=2)


class TransactionsRequestSchema(Schema):
    """零钱包交易请求 (可用于申购和赎回)"""

    #: :class:`str` 支付时所用银行卡ID
    bankcard_id = fields.String(required=True)
    #: :class:`str` 银行卡预留手机号所收到的短信验证码
    sms_code = fields.String()
    #: :class:`~decimal.Decimal` 购买金额
    amount = fields.Decimal(places=2, required=True)


class TransactionSchema(Schema):
    """零钱包交易记录.

    对于申购交易, 开始计息日期为 :attr:`.TransactionSchema.value_date` 字段.
    而赎回交易没有起息日期, 所以 ``value_date`` 为空. 此时停止计息日期和交易日
    期相同, 为 :attr:`.TransactionSchema.creation_date`.
    """

    #: :class:`str` 交易类型 (已存入: ``"P"`` /已取出: ``"R"``)
    transation_type = fields.Function(lambda o: o.type_.value)
    #: :class:`~decimal.Decimal` 交易金额
    amount = fields.Decimal(places=2)
    #: :class:`~datetime.date` 交易日期
    creation_date = fields.Date()
    #: :class:`~datetime.date` 开始计息日期
    value_date = fields.Date()
    #: :class:`~datetime.date` 到期计息日期
    end_date = fields.Date()
    #: :class:`.BankCardSchema` 支付所用银行卡
    bankcard = fields.Nested(BankCardSchema)


class ProfileSchema(Schema):
    """用户零钱包概况, 包括年化收益等信息. 收益单位为元, 小数精确到分."""

    #: :class:`~decimal.Decimal` 近一周收益(元)
    weekly_profit_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 近一月收益(元)
    monthly_profit_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 累积收益(元)
    total_profit_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 昨日收益(元)
    latest_profit_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 零钱总数(元)
    balance = fields.Decimal(places=2)
    #: :class:`int` 零钱包总笔数
    total_transations = fields.Integer()


class TransactionResultSchema(Schema):
    """零钱包交易结果"""

    #: :class:`.TransactionSchema` 交易实体
    transaction = fields.Nested(TransactionSchema)
    #: :class:`.ProfileSchema` 用户信息实体
    profile = fields.Nested(ProfileSchema)
    #: :class:`~datetime.date` 转出预计到账时间
    expected_credited_date = fields.Date()
    #: :class:`~datetime.date` 首笔收益到账日期
    profit_credited_date = fields.Date()

    @pre_dump
    def constractor(self, transaction):
        profile = UserDashboard.today(transaction.wallet_account)
        data = {'profile': profile, 'transaction': transaction}
        if transaction.type_ is WalletTransaction.Type.redeeming:
            data['expected_credited_date'] = transaction.end_date
        if transaction.type_ is WalletTransaction.Type.purchase:
            data['profit_credited_date'] = (
                transaction.value_date + datetime.timedelta(days=1))
        return data


class DashboardSchema(Schema):
    """零钱包年化收益率、万份收益等信息."""

    #: :class:`.AnnualRateItem` 最近一周每日年化收益(7天收益率)
    weekly_annual_rates = fields.Nested(AnnualRateItem, many=True)
    #: :class:`.AnnualRateItem` 最后一天年化收益
    latest_annual_rate = fields.Nested(AnnualRateItem)


class SpecSchema(Schema):
    """购买金额限制"""

    #: :class:`~decimal.Decimal` 起始金额
    amount_min = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最大购买金额
    amount_max = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 购买金额精确到
    amount_accurate = fields.Decimal(places=2)
    #: :class:`~datetime.date` 现在购买预计起息日期
    expected_value_date = fields.Date()
    #: :class:`~datetime.date` 预计到账日期
    expected_credited_date = fields.Date()
    #: :class:`~datetime.date` 首笔收益到账日期
    profit_credited_date = fields.Date()
    #: :class:`url` 用户协议地址
    agreement_url = fields.Url()


class BankcardRequestSchema(Schema):
    """银行卡绑定请求实体"""

    #: :class:`str` 银行卡预留手机号所收到的短信验证码
    sms_code = fields.String()
