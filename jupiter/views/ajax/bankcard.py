# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from functools import partial

from flask import abort, g, jsonify, request
from flask_wtf import Form

from core.models.bank import Partner
from core.models.profile.bankcard import (
    BankCardManager, CardConflictError, BankConflictError)
from core.models.wallet import is_bound_bankcard
from core.models.wallet.providers import zhongshan
from .blueprint import create_blueprint, ValidationMixin
from ._bankcard import bankcard_mixin, bankcard_editing_mixin, bankcard_to_dict


bp = create_blueprint('bankcard', __name__, url_prefix='/j/bankcard')


@bp.before_request
def initialize():
    if not g.user:
        abort(401)
    g.bankcards = BankCardManager(g.user.id_)
    g.partner = request.args.get('partner', type=Partner)
    if not g.partner:
        abort(400)


@bp.route('/', methods=['POST'])
def create_bankcard():
    form = CreateBankcardForm()
    form.raise_for_validation()
    try:
        bankcard = g.bankcards.create_or_update(
            mobile_phone=form.mobile_phone.data,
            card_number=form.card_number.data,
            bank_id=form.bank_id.data.id_,
            city_id=form.city_id.data.code,
            province_id=form.province_id.data.code,
            local_bank_name=form.bank_branch_name.data or '')
    except (BankConflictError, CardConflictError) as e:
        abort(403, unicode(e))
    return make_bankcard_response(
        g.bankcards, g.partner, g.user.id_, bankcard_id=bankcard.id_)


@bp.route('/<int:bankcard_id>', methods=['PUT'])
def edit_bankcard(bankcard_id):
    bankcard = g.bankcards.get(bankcard_id) or abort(404)
    form = EditBankcardForm()
    form.raise_for_validation()
    bankcard.update(
        mobile_phone=form.mobile_phone.data,
        bank_id=bankcard.bank_id,
        city_id=bankcard.city_id,
        province_id=bankcard.province_id,
        local_bank_name=form.bank_branch_name.data or '',
        is_default=False)
    return make_bankcard_response(
        g.bankcards, g.partner, g.user.id_, bankcard_id=bankcard.id_)


@bankcard_mixin(bank_partner=None)
class CreateBankcardForm(Form, ValidationMixin):
    pass


@bankcard_editing_mixin
class EditBankcardForm(Form, ValidationMixin):
    pass


ORDER_KEYS = {
    'valid': 0,
    'unbound': 1,
    'invalid': 2,
}


def _bankcard_to_dict(bankcard, partner, user_id):
    """Returns serialzied bankcard."""
    if partner is Partner.zs:
        bound_checker = partial(is_bound_bankcard, provider=zhongshan)
    else:
        bound_checker = None
    return bankcard_to_dict(bankcard, partner, user_id, bound_checker)


def make_bankcard_response(bankcards, partner, user_id, bind_cards=None, **kwargs):
    """Returns success response of bankcard operations."""
    cards = bind_cards if bind_cards else bankcards.get_all()
    bankcards = [
        _bankcard_to_dict(b, partner, user_id) for b in cards]
    bankcards.sort(key=lambda bankcard: ORDER_KEYS[bankcard['status']])
    return jsonify(r=True, bankcards=bankcards, **kwargs)
