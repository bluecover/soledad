from __future__ import print_function, absolute_import, unicode_literals

import uuid

from zslib.errors import BusinessError

from jupiter.ext import zslib
from libs.logger.rsyslog import rsyslog
from core.models.user.account import Account
from core.models.profile.bankcard import BankCard
from core.models.profile.identity import (
    Identity, has_real_identity, RealIdentityRequiredError)
from .account import WalletAccount
from .providers import zhongshan
from .transaction import WalletTransaction
from .utils import describe_bank_suspend, describe_wallet_suspend
from ._bankcard_binding import WalletBankcardBinding, is_bound_bankcard


__all__ = ['CreateAccountFlow', 'TransactionFlow']


class Workflow(object):
    """The base workflow class."""

    provider = zhongshan

    def initialize_with_user(self, user_id):
        """Initializes with user and identity.

        :param user_id: The local account id of user.
        :raises RealIdentityRequiredError: if the user has not real identity.
        """
        self.user = Account.get(user_id)
        self.identity = Identity.get(user_id)

        if not self.user:
            raise ProgrammingError('user %r not found' % user_id)
        if not has_real_identity(self.user):
            raise RealIdentityRequiredError(self.user)

    def initialize_with_bankcard(self, bankcard_id):
        """Initializes with bankcard.

        :param bankcard_id: The default bankcard used in third-party account.
        :raises UnsupportedBankError: if the bank of choosen bankcard is not
                                      supported.
        """
        self.bankcard = BankCard.get(bankcard_id)
        if not self.bankcard:
            raise ProgrammingError('bankcard %r not found' % bankcard_id)
        self.bankcard.bank.raise_for_unavailable(self.provider.bank_partner)

    @property
    def statuses(self):
        return WalletAccount.Status

    @property
    def wallet_account(self):
        return WalletAccount.get_or_add(self.user, self.provider)

    def make_transaction_id(self):
        return uuid.uuid4().hex

    def raise_for_bank_suspend(self, transfer_type):
        message = describe_wallet_suspend(transfer_type)
        if message is not None:
            raise WalletSuspendError(message)
        message = describe_bank_suspend(self.bankcard.bank, transfer_type)
        if message is not None:
            raise BankSuspendError(message)

    def send_sms(self, template, **kwargs):
        """Sends SMS for verifying bankcard operation."""
        response = zslib.send_sms(
            transaction_id=self.make_transaction_id(),
            user_id=self.wallet_account.secret_id,
            mobile_phone=self.bankcard.mobile_phone,
            template=template.format(**kwargs))
        return response

    def unbind_all_bankcards(self):
        bindings = WalletBankcardBinding.get_multi_by_user(
            self.user.id_, self.provider)
        for binding in bindings:
            binding.freeze()

    def bind_bankcard(self, sms_code):
        """Binds this bankcard while first time used in remote side."""
        # WTF... We must unbind all bankcards because of our partner.
        self.unbind_all_bankcards()

        with WalletBankcardBinding.record_for_binding(
                self.bankcard, self.provider):
            zslib.bind_bankcard(
                transaction_id=self.make_transaction_id(),
                user_id=self.wallet_account.secret_id,
                bank_id=self.bankcard.bank.zslib_id,
                card_number=self.bankcard.card_number,
                person_name=self.identity.person_name,
                person_ricn=self.identity.person_ricn,
                mobile_phone=self.bankcard.mobile_phone,
                password=self.wallet_account.secret_token,
                sms_code=sms_code)


class CreateAccountFlow(Workflow):
    """The workflow for creating account in third-party service provider."""

    def __init__(self, user_id, bankcard_id):
        self.initialize_with_user(user_id)
        self.initialize_with_bankcard(bankcard_id)

    def need_to_create(self):
        return self.wallet_account.status is not self.statuses.success

    def create_account(self, sms_code):
        if self.need_to_create():
            try:
                with WalletBankcardBinding.record_for_binding(
                        self.bankcard, self.provider):
                    zslib.create_account(
                        transaction_id=self.make_transaction_id(),
                        user_id=self.wallet_account.secret_id,
                        bank_id=self.bankcard.bank.zslib_id,
                        card_number=self.bankcard.card_number,
                        person_name=self.identity.person_name,
                        person_ricn=self.identity.person_ricn,
                        mobile_phone=self.bankcard.mobile_phone,
                        password=self.wallet_account.secret_token,
                        sms_code=sms_code)
            except BusinessError as e:
                if e.kind is BusinessError.kinds.account_activated:
                    self.wallet_account.transfer_status(self.statuses.success)
                    rsyslog.send(
                        'account_activated %r' % self.wallet_account.id_,
                        'wallet_programming')
                else:
                    self.wallet_account.transfer_status(self.statuses.failure)
                    raise
            except:
                self.wallet_account.transfer_status(self.statuses.failure)
                raise
            else:
                self.wallet_account.transfer_status(self.statuses.success)
        return self.wallet_account


class TransactionFlow(Workflow):
    """The workflow for transacting in third-party service provider."""

    def __init__(self, user_id, bankcard_id):
        self.initialize_with_user(user_id)
        self.initialize_with_bankcard(bankcard_id)

    def purchase(self, sms_code, amount):
        """Purchases money fund.

        :type sms_code: :class:`str` or :class:`unicode`
        :type amount: :class:`~decimal.Decimal`
        :raises UnboundBankcardError: if the bankcard is not bound
        :raises BankSuspendError: if the bank is suspended
        """
        return self._make_transaction(
            sms_code, amount, WalletTransaction.Type.purchase)

    def redeem(self, sms_code, amount):
        """Redeems money fund.

        :type sms_code: :class:`str` or :class:`unicode`
        :type amount: :class:`~decimal.Decimal`
        :raises UnboundBankcardError: if the bankcard is not bound
        :raises BankSuspendError: if the bank is suspended
        """
        return self._make_transaction(
            sms_code, amount, WalletTransaction.Type.redeeming)

    def _make_transaction(self, sms_code, amount, type_):
        if not is_bound_bankcard(self.bankcard, self.provider):
            raise UnboundBankcardError(self.bankcard)

        transaction = WalletTransaction.add(
            account=self.wallet_account,
            bankcard=self.bankcard,
            transaction_id=self.make_transaction_id(),
            amount=amount,
            type_=type_)
        transaction_args = {
            'transaction_id': transaction.transaction_id,
            'user_id': self.wallet_account.secret_id,
            'amount': amount,
            'sms_code': sms_code,
            'card_number': self.bankcard.card_number}

        try:
            if type_ is WalletTransaction.Type.purchase:
                zslib.purchase(**transaction_args)
            elif type_ is WalletTransaction.Type.redeeming:
                zslib.redeem(**transaction_args)
            else:
                raise ValueError('unknown type: %r' % type_)
        except:
            transaction.transfer_status(WalletTransaction.Status.failure)
            raise
        else:
            transaction.transfer_status(WalletTransaction.Status.success)

        return transaction


class ProgrammingError(Exception):
    pass


class UnboundBankcardError(Exception):
    pass


class BankSuspendError(Exception):
    pass


class WalletSuspendError(Exception):
    pass
