# coding: utf-8

from blinker import Namespace


_signal = Namespace()


# 订单信号

hoarder_order_succeeded = _signal.signal('hoarder-order-succeed')
hoarder_order_failed = _signal.signal('hoarder-order-failed')
hoarder_asset_redeemed = _signal.signal('hoarder-asset-redeem')
