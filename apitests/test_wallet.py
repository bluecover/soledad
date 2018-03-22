# coding: utf-8

from __future__ import absolute_import, unicode_literals

from decimal import Decimal
from datetime import date, datetime, time

from mock import patch
from pytest import raises, fixture
from freezegun import freeze_time

from core.models.wallet.profit import WalletProfit
from core.models.wallet.account import WalletAccount
from core.models.wallet.providers import zhongshan
from core.models.wallet.annual_rate import WalletAnnualRate
from core.models.wallet.switch import wallet_bank_suspend, wallet_suspend
from core.models.bank.banks import bank_collection
from core.models.profile.identity import RealIdentityRequiredError


testing_urls = {
    'mine': '/api/v1/wallet/mine',
    'mine_profit': '/api/v1/wallet/mine/profit',
    'dashboard': '/api/v1/wallet/dashboard',
    'annual_rates': '/api/v1/wallet/dashboard/annual-rates',
    'spec': '/api/v1/wallet/spec',
    'bankcard': '/api/v1/wallet/bankcard/{0}/verify',
    'deposit': '/api/v1/wallet/deposit',
    'withdraw': '/api/v1/wallet/withdraw',
    'transaction': '/api/v1/wallet/transactions'
}


@fixture
def annual_rate(sqlstore, redis):
    ttp_income = Decimal('1.0')
    annual_rate = Decimal('3.1')
    return WalletAnnualRate.record(
        date(2015, 10, 19), annual_rate, ttp_income, zhongshan.fund_code)


@fixture
def profit(sqlstore, redis, user):
    wallet_account = WalletAccount.get_or_add(user, zhongshan)
    return WalletProfit.record(wallet_account, Decimal('1.2'), date(2015, 10, 19))


def test_mine(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['mine'])
    assert r.status_code == 200
    assert r.data['success'] is True
    # TODO fill up fake data
    assert r.data['data'] == {
        'balance': 0.0,
        'latest_profit_amount': 0.0,
        'weekly_profit_amount': 0.0,
        'monthly_profit_amount': 0.0,
        'total_profit_amount': 0.0,
        'total_transations': 0}


@freeze_time('2015-10-20')
def test_mine_profit(client, oauth_token, profit):
    client.load_token(oauth_token)

    r = client.get(testing_urls['mine_profit'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'] == [{
        'date': '2015-10-19',
        'profit': 1.2}]


@freeze_time('2015-10-20')
def test_dashboard(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['dashboard'])
    assert r.status_code == 200
    assert r.data['success'] is True
    # TODO fill up fake data
    assert r.data['data'] == {
        'latest_annual_rate': {
            'annual_rate': 0.0,
            'date': '2015-10-20',
            'ttp': 0.0},
        'weekly_annual_rates': []}


@freeze_time('2015-10-20')
def test_annual_rates(client, oauth_token, annual_rate):
    client.load_token(oauth_token)

    r = client.get(testing_urls['annual_rates'])
    assert r.status_code == 200
    assert r.data['data'] == {
        'average_annual_rate': 3.1,
        'average_ttp': 1.0,
        'items': [{
            'date': '2015-10-19',
            'annual_rate': 3.1,
            'ttp': 1.0}]}


@freeze_time('2015-10-20')
def test_spec(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['spec'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'] == {
        'amount_min': 1.0,
        'amount_max': 50000.0,
        'amount_accurate': 0.01,
        'expected_value_date': '2015-10-21',
        'expected_credited_date': '2015-10-20',
        'profit_credited_date': '2015-10-22',
        'agreement_url': 'http://localhost:5000/wallet/agreement'}


@patch('core.models.wallet.facade.zslib')
def test_bankcard_without_identity(zslib, client, oauth_token, bankcard):
    client.load_token(oauth_token)

    # FIXME prompt user instead of throwing an internal server error
    with raises(RealIdentityRequiredError):
        client.post(testing_urls['bankcard'].format(bankcard.id_), data={})


@patch('core.models.wallet.facade.zslib')
def test_bankcard_step_1(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    r = client.post(testing_urls['bankcard'].format(bankcard.id_), data={})

    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['is_bound_in_wallet'] is False

    assert zslib.send_sms.call_count == 1
    args, kwargs = zslib.send_sms.call_args
    assert args == ()
    assert kwargs['mobile_phone'] == '13800138000'
    assert kwargs['user_id']
    assert kwargs['transaction_id']
    # card_number suffix should appeare in SMS content
    assert bankcard.card_number[-4:] in kwargs['template']


@patch('core.models.wallet.facade.zslib')
def test_bankcard_step_2(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    # first time
    r = client.post(testing_urls['bankcard'].format(bankcard.id_), data={
        'sms_code': '314159',
    })
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['is_bound_in_wallet'] is True

    assert zslib.create_account.call_count == 1
    args, kwargs = zslib.create_account.call_args
    assert args == ()
    assert kwargs['bank_id'] == bankcard.bank.zslib_id
    assert kwargs['card_number'] == bankcard.card_number
    assert kwargs['person_name'] == identity.person_name
    assert kwargs['person_ricn'] == identity.person_ricn
    assert kwargs['sms_code'] == '314159'

    zslib.reset_mock()

    # second time
    r = client.post(testing_urls['bankcard'].format(bankcard.id_), data={
        'sms_code': '610591',
    })
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['is_bound_in_wallet'] is True

    assert zslib.bind_bankcard.call_count == 1
    args, kwargs = zslib.bind_bankcard.call_args
    assert args == ()
    assert kwargs['bank_id'] == bankcard.bank.zslib_id
    assert kwargs['card_number'] == bankcard.card_number
    assert kwargs['person_name'] == identity.person_name
    assert kwargs['person_ricn'] == identity.person_ricn
    assert kwargs['sms_code'] == '610591'


@patch('core.models.wallet.facade.zslib')
def test_purchase_step_1(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    r = client.post(testing_urls['deposit'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000'})
    assert r.status_code == 200
    assert r.data['success'] is True
    assert zslib.send_sms.call_count == 1
    args, kwargs = zslib.send_sms.call_args
    assert args == ()
    assert kwargs['mobile_phone'] == '13800138000'
    assert kwargs['user_id']
    assert kwargs['transaction_id']


@patch('core.models.wallet.facade.zslib')
def test_purchase_step_2(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)
    # bind bankcard
    r = client.post(testing_urls['bankcard'].format(bankcard.id_), data={
        'sms_code': '610591',
    })
    assert r.status_code == 200
    assert r.data['success'] is True
    assert zslib.create_account.call_count == 1
    args, kwargs = zslib.create_account.call_args
    assert args == ()
    assert kwargs['sms_code'] == '610591'

    # transaction
    r = client.get(testing_urls['transaction'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'] == []

    # despoit
    r = client.post(testing_urls['deposit'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000',
        'sms_code': '123456'})
    assert r.status_code == 200
    assert r.data['success'] is True
    assert zslib.purchase.call_count == 1
    args, kwargs = zslib.purchase.call_args
    assert args == ()
    assert kwargs['sms_code'] == '123456'
    assert r.data['data']['profile'] == {
        'balance': 1000.0,
        'latest_profit_amount': 0.0,
        'weekly_profit_amount': 0.0,
        'monthly_profit_amount': 0.0,
        'total_profit_amount': 0.0,
        'total_transations': 1}


@patch('core.models.wallet.facade.zslib')
def test_redeem_step_1(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    r = client.post(testing_urls['withdraw'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000'})
    assert r.status_code == 200
    assert r.data['success'] is True
    assert zslib.send_sms.call_count == 1
    args, kwargs = zslib.send_sms.call_args
    assert args == ()
    assert kwargs['mobile_phone'] == '13800138000'
    assert kwargs['user_id']
    assert kwargs['transaction_id']


@freeze_time('2015-10-20')
@patch('core.models.wallet.facade.zslib')
def test_redeem_step_2(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    # bind bankcard
    r = client.post(testing_urls['bankcard'].format(bankcard.id_), data={
        'sms_code': '610591',
    })
    assert r.status_code == 200
    assert r.data['success'] is True
    assert zslib.create_account.call_count == 1
    args, kwargs = zslib.create_account.call_args
    assert args == ()
    assert kwargs['sms_code'] == '610591'

    # transaction
    r = client.get(testing_urls['transaction'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'] == []

    # redeem
    r = client.post(testing_urls['withdraw'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000',
        'sms_code': '123456'})
    assert r.status_code == 200
    assert r.data['success'] is True
    assert zslib.redeem.call_count == 1
    args, kwargs = zslib.redeem.call_args
    assert args == ()
    assert kwargs['sms_code'] == '123456'
    assert r.data['data']['profile'] == {
        'balance': -1000.0,
        'latest_profit_amount': 0.0,
        'weekly_profit_amount': 0.0,
        'monthly_profit_amount': 0.0,
        'total_profit_amount': 0.0,
        'total_transations': 1}


@patch('core.models.wallet.facade.zslib')
def test_list_transactions(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    # first bind bankcard
    r = client.post(testing_urls['bankcard'].format(bankcard.id_), data={
        'sms_code': '610591',
    })
    assert r.status_code == 200
    assert r.data['success'] is True
    assert zslib.create_account.call_count == 1
    args, kwargs = zslib.create_account.call_args
    assert args == ()
    assert kwargs['sms_code'] == '610591'

    # desposit
    r = client.post(testing_urls['deposit'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000',
        'sms_code': '123456'})
    assert r.status_code == 200
    assert r.data['success'] is True
    args, kwargs = zslib.purchase.call_args
    assert args == ()
    assert kwargs['sms_code'] == '123456'
    assert r.data['data']['profile']['total_transations'] == 1

    # transaction
    r = client.get(testing_urls['transaction'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'][0]['amount'] == 1000.0
    assert r.data['data'][0]['transation_type'] == u'P'


@patch('core.models.wallet.facade.zslib')
def test_wallet_purchase_suspend(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    bank = bank_collection.get_bank(4)
    suspend = wallet_bank_suspend['purchase'][bank]
    suspend.open_time = datetime.combine(datetime.now(), time(0, 0))
    suspend.close_time = datetime.combine(suspend.open_time, time(23, 59))
    error_msg = u'{0}至{1}'.format(_cn_time(suspend.open_time), _cn_time(suspend.close_time))

    r = client.post(testing_urls['deposit'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000'})
    assert r.status_code == 403
    assert r.data['success'] is False
    assert error_msg in r.data['messages']['_'][0]


@patch('core.models.wallet.facade.zslib')
def test_wallet_redeem_suspend(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    bank = bank_collection.get_bank(4)
    suspend = wallet_bank_suspend['redeem'][bank]
    suspend.open_time = datetime.combine(datetime.now(), time(0, 0))
    suspend.close_time = datetime.combine(suspend.open_time, time(23, 59))
    error_msg = u'{0}至{1}'.format(_cn_time(suspend.open_time), _cn_time(suspend.close_time))

    r = client.post(testing_urls['withdraw'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000'})
    assert r.status_code == 403
    assert r.data['success'] is False
    assert error_msg in r.data['messages']['_'][0]


@patch('core.models.wallet.facade.zslib')
def test_wallet_withdraw_suspend(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    suspend = wallet_suspend['withdraw']
    suspend.open_time = datetime.combine(datetime.now(), time(0, 0))
    suspend.close_time = datetime.combine(suspend.open_time, time(23, 59))
    error_msg = u'{0}至{1}'.format(_cn_time(suspend.open_time), _cn_time(suspend.close_time))

    r = client.post(testing_urls['withdraw'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000'})
    assert r.status_code == 403
    assert r.data['success'] is False
    assert error_msg in r.data['messages']['_'][0]


@patch('core.models.wallet.facade.zslib')
def test_wallet_deposit_suspend(zslib, client, oauth_token, bankcard, identity):
    client.load_token(oauth_token)

    suspend = wallet_suspend['deposit']
    suspend.open_time = datetime.combine(datetime.now(), time(0, 0))
    suspend.close_time = datetime.combine(suspend.open_time, time(23, 59))
    error_msg = u'{0}至{1}'.format(_cn_time(suspend.open_time), _cn_time(suspend.close_time))

    r = client.post(testing_urls['deposit'], data={
        'bankcard_id': bankcard.id_,
        'amount': '1000'})
    assert r.status_code == 403
    assert r.data['success'] is False
    assert error_msg in r.data['messages']['_'][0]


def _cn_time(dt):
    return dt.strftime(b'%Y年%m月%d日%H点%M分').decode('utf-8')
