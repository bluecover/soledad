# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from flask import g, abort, jsonify, request, url_for
from flask_wtf import Form
from wtforms import fields, validators
from zslib.errors import BusinessError

from core.models.profile.bankcard import BankCardManager
from core.models.wallet.account import WalletAccount
from core.models.wallet.providers import zhongshan
from core.models.wallet._bankcard_binding import is_bound_bankcard
from core.models.wallet.facade import (
    CreateAccountFlow, TransactionFlow, UnboundBankcardError,
    BankSuspendError, WalletSuspendError)
from core.models.wallet.transaction import WalletTransaction
from core.models.wallet.consts import (
    SMS_BINDING_BANKCARD, SMS_PURCHASE, SMS_REDEEMING,
    SMS_CODE_INCORECT_FOR_TRANSACTION, SMS_CODE_INCORECT_FOR_BINDING)
from core.models.wallet.utils import describe_business_error, describe_wallet_suspend
from core.models.utils import round_half_up
from jupiter.ext import sentry
from .blueprint import create_blueprint, ValidationMixin
from .bankcard import make_bankcard_response


bp = create_blueprint('wallet', __name__, url_prefix='/j/wallet')


@bp.before_request
def initialize_managers():
    if not g.user:
        abort(401)
    g.bankcards = BankCardManager(g.user.id_)
    g.wallet_provider = zhongshan
    g.wallet_account = WalletAccount.get_or_add(g.user, g.wallet_provider)


@bp.errorhandler(BusinessError)
def handle_business_errors(error):
    description = describe_business_error(error, sentry)
    return jsonify(r=False, error=description)


@bp.errorhandler(BankSuspendError)
@bp.errorhandler(WalletSuspendError)
def handle_suspend_error(error):
    return jsonify(r=False, error=error.args[0])


@bp.errorhandler(UnboundBankcardError)
def handle_unbound_bankcard_errors(error):
    return jsonify(r=False, error='该银行卡尚未绑定, 请刷新页面重试')


@bp.route('/bankcard/<int:bankcard_id>/verify', methods=['POST'])
def verify_bankcard(bankcard_id):
    """零钱包绑卡."""
    form = VerifyForm()
    form.raise_for_validation()
    bankcard = obtain_bankcard(bankcard_id)

    flow = CreateAccountFlow(g.user.id_, bankcard.id_)
    if form.sms_code.data:
        try:
            if flow.need_to_create():
                flow.create_account(form.sms_code.data)
            else:
                flow.bind_bankcard(form.sms_code.data)
        except BusinessError as e:
            if form.is_new.data:
                g.bankcards.remove(bankcard.card_number, silent=True)
            if e.kind is BusinessError.kinds.sms_code_incorrect:
                return jsonify(r=False, error=SMS_CODE_INCORECT_FOR_BINDING)
            raise
    else:
        flow.send_sms(SMS_BINDING_BANKCARD, bankcard=bankcard)

    bind_cards = [card for card in g.bankcards.get_all()
                  if is_bound_bankcard(card, zhongshan)]
    return make_bankcard_response(g.bankcards, g.wallet_provider.bank_partner,
                                  g.user.id_, bind_cards)


@bp.route('/deposit', methods=['POST'])
def deposit():
    """零钱包申购"""
    form = TransactionForm()
    form.raise_for_validation()
    bankcard = obtain_bankcard(form.bankcard_id.data)

    flow = TransactionFlow(g.user.id_, bankcard.id_)
    flow.raise_for_bank_suspend('purchase')
    if form.sms_code.data:
        try:
            flow.purchase(form.sms_code.data, form.amount.data)
        except BusinessError as e:
            if e.kind is BusinessError.kinds.sms_code_incorrect:
                return jsonify(r=False, error=SMS_CODE_INCORECT_FOR_TRANSACTION)
            raise
    else:
        flow.send_sms(SMS_PURCHASE, amount=form.amount.data)

    return jsonify(r=True)


@bp.route('/withdraw', methods=['POST'])
def withdraw():
    """零钱包赎回"""
    form = TransactionForm()
    form.raise_for_validation()
    bankcard = obtain_bankcard(form.bankcard_id.data)

    flow = TransactionFlow(g.user.id_, bankcard.id_)
    flow.raise_for_bank_suspend('redeem')
    if form.sms_code.data:
        try:
            flow.redeem(form.sms_code.data, form.amount.data)
        except BusinessError as e:
            if e.kind is BusinessError.kinds.sms_code_incorrect:
                return jsonify(r=False, error=SMS_CODE_INCORECT_FOR_TRANSACTION)
            raise
    else:
        flow.send_sms(SMS_REDEEMING, amount=form.amount.data)

    return jsonify(r=True)


@bp.route('/transactions')
def transactions():
    start = request.args.get('start', type=int, default=0)
    limit = request.args.get('limit', type=int, default=5)

    ids = WalletTransaction.get_ids_by_account(g.wallet_account.id_)
    transactions = WalletTransaction.get_multi(ids[start:start + limit])

    data = {
        'collection': [{
            'type': (
                'deposit' if t.type_ is WalletTransaction.Type.purchase
                else 'withdraw'),
            'bankcard': {
                'bank': {'name': t.bankcard.bank.name},
                'display_card_number': t.bankcard.display_card_number},
            'amount': unicode(round_half_up(t.amount, 2)),
            'creation_date': unicode(t.creation_time.date()),
            'value_date': unicode(t.value_date) if t.value_date else None}
            for t in transactions
            if t.status is WalletTransaction.Status.success],
        'start': start,
        'total': len(ids),
    }
    return jsonify(r=True, data=data)


def obtain_bankcard(bankcard_id):
    bankcard = g.bankcards.get(bankcard_id)
    if not bankcard:
        abort(400, '信息已过期, 请刷新页面重试')
    if g.wallet_provider.bank_partner not in bankcard.bank.available_in:
        abort(400, '不支持所选的银行卡')
    return bankcard


class VerifyForm(Form, ValidationMixin):
    """绑定银行卡表单."""

    sms_code = fields.StringField(validators=[
        validators.Optional(),
        validators.Regexp(r'\d{4,8}', message='请正确填写短信验证码'),
    ])
    is_new = fields.BooleanField()


class TransactionForm(Form, ValidationMixin):
    """申购、赎回表单."""

    sms_code = fields.StringField(validators=[
        validators.Optional(),
        validators.Regexp('\d{4,8}', message='请正确填写短信验证码'),
    ])
    amount = fields.DecimalField(places=2, validators=[
        validators.DataRequired('请填写金额'),
        validators.NumberRange(1, 50000, '金额必须在 %(min)s 到 %(max)s 之间')
    ])
    bankcard_id = fields.IntegerField(validators=[
        validators.DataRequired('请选择银行卡')
    ])


@bp.route('/available')
def check_for_available():
    suspend = describe_wallet_suspend(request.args['order_type'])
    if suspend:
        return jsonify(r=False, error=suspend)
    else:
        wallet_route = {'deposit': url_for('wallet.transaction.deposit'),
                        'withdraw': url_for('wallet.transaction.withdraw')}
        return jsonify(r=True, data={'redirect_url': wallet_route[request.args['order_type']]})
