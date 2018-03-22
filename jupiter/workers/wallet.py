# coding: utf-8

from __future__ import absolute_import

from jupiter.ext import zslib
from . import pool


@pool.async_worker('guihua_wallet_profit_mq')
def wallet_profit_syncronizer(wallet_account_id):
    """更新零钱包用户收益."""
    from core.models.wallet.account import WalletAccount
    from core.models.wallet.profit import WalletProfit

    wallet_account = WalletAccount.get(wallet_account_id)
    if wallet_account.status is not WalletAccount.Status.success:
        return
    WalletProfit.synchronize(zslib.client, wallet_account, days=3)
