# coding: utf-8

from blinker import Namespace


_signals = Namespace()

# 宜人贷信号
yrd_order_paid = _signals.signal('yrd-order-paid')
yrd_order_confirmed = _signals.signal('yrd-order-confirmed')
yrd_order_failure = _signals.signal('yrd-order-failure')
yrd_order_exited = _signals.signal('yrd-order-exited')

# 指旺信号
zw_order_succeeded = _signals.signal('zw-order-succeeded')
zw_order_failure = _signals.signal('zw-order-failure')
zw_asset_redeemed = _signals.signal('zw-asset-redeemed')

# 新结算投米
xm_order_succeeded = _signals.signal('xm-order-succeeded')
xm_order_failure = _signals.signal('xm-order-failure')
xm_asset_redeemed = _signals.signal('xm-asset-redeemed')
