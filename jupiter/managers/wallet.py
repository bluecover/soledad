# coding: utf-8

from flask_script import Manager
from zslib.errors import BusinessError

from jupiter.ext import zslib
from libs.utils.log import bcolors
from core.models.utils import round_half_up
from core.models.wallet.providers import zhongshan
from core.models.wallet.annual_rate import WalletAnnualRate


manager = Manager()
manager.__doc__ = 'The commands for wallet product.'
provider = zhongshan


@manager.command
def init():
    """Synchronize the annual rates."""
    try:
        rates = WalletAnnualRate.synchronize(zslib.client, provider.fund_code)
    except BusinessError as e:
        bcolors.fail('%s : %s : %s' % e.args)
        return

    for rate in rates:
        bcolors.success('{0}\t{1}\t{2}\t￥{3}'.format(
            rate.date,
            rate.fund_code,
            round_half_up(rate.annual_rate, 2),
            round_half_up(rate.ten_thousand_pieces_income, 2),
        ))
