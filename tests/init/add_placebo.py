# coding: utf-8

from __future__ import absolute_import

import decimal
import datetime

from libs.utils.log import bcolors
from core.models.hoard.placebo import PlaceboProduct, strategies


def main():
    product = PlaceboProduct.add(
        strategy=strategies.strategy_2016_spring,
        min_amount=decimal.Decimal(8888),
        max_amount=decimal.Decimal(8888),
        start_sell_date=datetime.date.today(),
        end_sell_date=datetime.date.today() + datetime.timedelta(days=3),
        frozen_days=7,
        annual_rate=decimal.Decimal('6.6'))
    bcolors.run('success: %s' % product, key='placebo')


if __name__ == '__main__':
    main()
