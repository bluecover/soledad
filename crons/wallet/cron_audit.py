#!/usr/bin/env python
# coding:utf-8

"""
    查询每天零钱包本地与中山数据状态
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import datetime

from jupiter.ext import zslib
from jupiter.app import create_app
from core.models.wallet.audit import audit_by_account, get_active_accounts_by_date

app = create_app()


def main():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    today = datetime.date.today()
    for wallet_account in get_active_accounts_by_date(yesterday):
        audit_by_account(
            client=zslib.client,
            wallet_account=wallet_account,
            date_from=yesterday,
            date_to=today)


if __name__ == '__main__':
    with app.app_context():
        main()
