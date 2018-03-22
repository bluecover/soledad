#!/usr/bin/env python
# coding:utf-8

"""
    更新所有零钱包用户收益
    ~~~~~~~~~~~~~~~~~~~~~~
"""

from core.models.wallet.account import WalletAccount
from core.models.wallet.profit import WalletProfit


def main():
    for id_ in WalletAccount.get_all_ids():
        WalletProfit.synchronize_async(id_)


if __name__ == '__main__':
    main()
