# coding: utf-8

from pytest import raises
from mock import patch

from core.models.wallet.account import WalletAccount
from core.models.wallet.facade import CreateAccountFlow, ProgrammingError
from core.models.profile.identity import RealIdentityRequiredError
from core.models.bank.errors import UnsupportedBankError
from .framework import BaseTestCase


class CreateAccountFlowTest(BaseTestCase):

    def setUp(self):
        super(CreateAccountFlowTest, self).setUp()
        self.user = self.add_account(mobile='13800138000')
        self.user_with_email = self.add_account(email='foo@guihua.dev')
        self.bankcard = self.add_bankcard(self.user.id_)

    def _add_identity_for_users(self):
        self.identity = self.add_identity(
            self.user.id_, u'左冷禅', '44011320141005001x')
        self.identity_with_email = self.add_identity(
            self.user_with_email.id_, u'莫大', '360426199101010071')

    def test_invalid_id(self):
        self._add_identity_for_users()

        with raises(ProgrammingError):
            CreateAccountFlow('-1', self.bankcard.id_)
        with raises(ProgrammingError):
            CreateAccountFlow(self.user.id_, '-1')

    def test_real_identity_checking(self):
        with raises(RealIdentityRequiredError):
            CreateAccountFlow(self.user.id_, self.bankcard.id_)
        with raises(RealIdentityRequiredError):
            CreateAccountFlow(self.user_with_email.id_, self.bankcard.id_)

        self._add_identity_for_users()

        assert CreateAccountFlow(self.user.id_, self.bankcard.id_)
        with raises(RealIdentityRequiredError):
            CreateAccountFlow(self.user_with_email.id_, self.bankcard.id_)

    def test_bankcard_checking(self):
        self._add_identity_for_users()

        # 深发银行还没有任何产品线支持, 正好用来测试
        invalid_bankcard = self.add_bankcard(
            self.user.id_, '10010', card_number='6222980000010001')

        with raises(UnsupportedBankError):
            CreateAccountFlow(self.user.id_, invalid_bankcard.id_)
        assert CreateAccountFlow(self.user.id_, self.bankcard.id_)

    @patch('core.models.wallet.facade.uuid')
    @patch('core.models.wallet.facade.zslib')
    def test_send_sms(self, zslib, uuid):
        self._add_identity_for_users()

        flow = CreateAccountFlow(self.user.id_, self.bankcard.id_)

        assert flow.send_sms('dummy %s') is zslib.send_sms.return_value
        zslib.send_sms.assert_called_once_with(
            transaction_id=uuid.uuid4.return_value.hex,
            user_id=flow.wallet_account.secret_id,
            mobile_phone=self.bankcard.mobile_phone,
            template='dummy %s')

    @patch('core.models.wallet.facade.uuid')
    @patch('core.models.wallet.facade.zslib')
    def test_create_account(self, zslib, uuid):
        self._add_identity_for_users()

        flow = CreateAccountFlow(self.user.id_, self.bankcard.id_)
        assert flow.need_to_create()
        wallet_account = flow.create_account('10010')
        zslib.create_account.assert_called_once_with(
            transaction_id=uuid.uuid4.return_value.hex,
            user_id=wallet_account.secret_id,
            bank_id=self.bankcard.bank.zslib_id,
            card_number=self.bankcard.card_number,
            person_name=self.identity.person_name,
            person_ricn=self.identity.person_ricn,
            mobile_phone=self.bankcard.mobile_phone,
            password=wallet_account.secret_token,
            sms_code='10010')
        assert wallet_account.status is WalletAccount.Status.success
        assert not flow.need_to_create()

        zslib.create_account.reset_mock()

        wallet_account = flow.create_account('10010')
        assert not zslib.create_account.called

    @patch('core.models.wallet.facade.uuid')
    @patch('core.models.wallet.facade.zslib')
    def test_create_failure(self, zslib, uuid):
        self._add_identity_for_users()

        class TestingException(Exception):
            pass

        # calls with exception
        zslib.create_account.side_effect = TestingException()
        flow = CreateAccountFlow(self.user.id_, self.bankcard.id_)
        with raises(TestingException):
            flow.create_account('10010')
        assert zslib.create_account.called

        # check failure
        wallet_account = WalletAccount.get_by_local_account(
            self.user, flow.provider)
        assert wallet_account.status is WalletAccount.Status.failure
        assert flow.need_to_create()

        # retry
        zslib.create_account.side_effect = None
        wallet_account = flow.create_account('10010')
        assert wallet_account.status is WalletAccount.Status.success
        assert not flow.need_to_create()
