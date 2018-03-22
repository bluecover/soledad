#!/usr/bin/env python
# coding:utf-8

"""
    更新零钱包七日年化收益率
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""

from jupiter.app import create_app
from jupiter.ext import zslib
from core.models.wallet.providers import zhongshan
from core.models.wallet.annual_rate import WalletAnnualRate


app = create_app()
provider = zhongshan


def main():
    with app.app_context():
        WalletAnnualRate.synchronize(zslib.client, provider.fund_code)


if __name__ == '__main__':
    main()
