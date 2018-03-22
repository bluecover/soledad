# coding: utf-8

import decimal
import datetime
import math
import uuid

from mock import patch

from libs.utils.log import bcolors
from core.models.user.account import Account
from core.models.profile.bankcard import BankCard
from core.models.wallet.providers import zhongshan
from core.models.wallet.annual_rate import WalletAnnualRate
from core.models.wallet.account import WalletAccount
from core.models.wallet.transaction import WalletTransaction
from core.models.wallet.profit import WalletProfit


provider = zhongshan


def generate_fake_annual_rates():
    for days in reversed(range(10)):
        date = datetime.date.today() - datetime.timedelta(days=days)
        annual_rate = decimal.Decimal(abs(math.sin(decimal.Decimal(days)))) * 3
        annual_rate = annual_rate + decimal.Decimal('1.1')
        ttp_income = decimal.Decimal('1.0')
        rate = WalletAnnualRate.record(
            date, annual_rate, ttp_income, provider.fund_code)
        bcolors.run(repr(rate), key='wallet')


def generate_fake_transactions():
    user = Account.get_by_alias('test0@guihua.com')
    if not user:
        return
    with patch('core.models.profile.bankcard.DEBUG', True):
        b1 = BankCard.add(
            user_id=user.id_,
            mobile_phone='13800138000',
            card_number='6222000000000009',
            bank_id='4',  # 建设银行
            city_id='110100',  # 朝阳
            province_id='110000',  # 北京
            local_bank_name='西夏支行',
            is_default=True)
        b2 = BankCard.add(
            user_id=user.id_,
            mobile_phone='13800138000',
            card_number='6222000000010008',
            bank_id='10002',  # 中信银行
            city_id='110100',  # 朝阳
            province_id='110000',  # 北京
            local_bank_name='天龙寺支行',
            is_default=True)

    bcolors.run(repr(b1), key='wallet')
    bcolors.run(repr(b2), key='wallet')

    wallet_account = WalletAccount.get_or_add(user, zhongshan)
    t1 = WalletTransaction.add(
        wallet_account, b1, decimal.Decimal('40'),
        WalletTransaction.Type.purchase, uuid.uuid4().hex, WalletTransaction.Status.failure)
    t2 = WalletTransaction.add(
        wallet_account, b1, decimal.Decimal('42'),
        WalletTransaction.Type.purchase, uuid.uuid4().hex, WalletTransaction.Status.success)
    t3 = WalletTransaction.add(
        wallet_account, b2, decimal.Decimal('10'),
        WalletTransaction.Type.redeeming, uuid.uuid4().hex, WalletTransaction.Status.success)

    bcolors.run(repr(t1), key='wallet')
    bcolors.run(repr(t2), key='wallet')
    bcolors.run(repr(t3), key='wallet')


def generate_fake_profits():
    user = Account.get_by_alias('test0@guihua.com')
    wallet_account = WalletAccount.get_or_add(user, zhongshan)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    WalletProfit.record(wallet_account, decimal.Decimal('1.2'), yesterday)


def main():
    generate_fake_annual_rates()
    generate_fake_transactions()
    generate_fake_profits()


if __name__ == '__main__':
    main()
