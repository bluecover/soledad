# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

import collections

from core.models.bank import Partner


_ProductProvider = collections.namedtuple('ProductProvider', [
    'id_',
    'name',
    'shortcut',
    'bank_partner',
])


class ProductProvider(_ProductProvider):
    """The service provider of wallet."""

    storage = {}

    def __init__(self, id_, name, shortcut, bank_partner):
        self.storage[int(id_)] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(int(id_))

    def is_avalable_bankcard(self, bankcard):
        return self.bank_partner in bankcard.bank.available_in


yirendai = ProductProvider(
    id_=1,
    name=u'宜人贷',
    shortcut='yrd',
    bank_partner=Partner.yrd)

# NOTE 指旺这个名字不可以露出
zhiwang = ProductProvider(
    id_=2,
    name=u'指旺',
    shortcut='zw',
    bank_partner=Partner.zw)

yxpay = ProductProvider(
    id_=3,
    name=u'新结算',
    shortcut='yxpay',
    bank_partner=Partner.yxpay)

# 最初返现由财务直接划账（支持银行保持与新结算一致）
ghpay = ProductProvider(
    id_=4,
    name=u'规划支付',
    shortcut='ghpay',
    bank_partner=Partner.yxpay)

placebo = ProductProvider(
    id_=5,
    name=u'体验金',
    shortcut='placebo',
    bank_partner=Partner.yxpay)

# 投米P2P
xmpay = ProductProvider(
    id_=5,
    name=u'新结算投米',
    shortcut='xm',
    bank_partner=Partner.xm)
