# coding: utf-8

from core.models.hoarder.vendor import Provider

PERIODS = {
    'unlimited': {'value': 0, 'unit': u'活期', 'text': u'活期'},
    '7': {'value': 7, 'unit': u'天', 'text': u'7天加息'},
    '90': {'value': 90, 'unit': u'天', 'text': u'90天'},
    '180': {'value': 180, 'unit': u'天', 'text': u'180天'},
    '365': {'value': 365, 'unit': u'天', 'text': u'365天'}
}
COMMON_PRODUCT_PROFILE = {
    Provider.sxb: {
        'title': u'随心攒',
        'activity_title': u'随心攒产品是什么？',
        'activity_introduction': (
            '随心攒是好规划与宜信联合推出的，具有活期性质的混合型P2P产品。\n'
            '该产品具有以下特点：\n'
            '1、100元起投，最多可持有10万元 \n'
            '2、每日可提现3万元，提现后通常下一工作日到账 \n'
            '因此，随心攒是一款收益高于货币基金，同时具有固定期限产品所不具备的灵活性理财产品。'),
        'tags': [u'随时存取', u'按日计息'],
        'period': PERIODS.get('unlimited'),
        'withdraw_rule_url': 'hybrid.rules.sxb_withdraw'
    },
    Provider.zw: {
        'title': u'新手专享',
        'activity_title': u'新手专享',
        'activity_introduction': (
            '为了支持各位新朋友开展攒钱大业，好规划特意推出了『新手专享』福利。'
            '所有 2015年9月23日零时 之前尚未攒钱的用户，即可以新人的身份享受一笔25天封闭期，'
            '年化收益率高达10%的攒钱。机会难得，可不要错过哦!'),
        'tags': [u'新用户可享10%年化收益'],
        'period': PERIODS.get('7'),
        'withdraw_rule_url': ''
    },
    Provider.xm: {
        'title': u'产品介绍',
        'activity_title': u'',
        'activity_introduction': U'',
        'tags': [],
        'period': PERIODS.get('90'),
        'withdraw_rule_url': ''
    },
    Provider.ms: {
        'title': u'货币基金',
        'activity_title': u'货币基金产品是什么？',
        'activity_introduction': u'',
        'tags': [u'随时存取', u'按日计息'],
        'period': PERIODS.get('unlimited'),
        'vendor': None,
    }
}


class ProductStatus(object):
    def __init__(self, st, text, tip, color):
        self.st = st
        self.text = text
        self.tip = tip
        self.color = color


PRODUCT_STATUS = {
    'offsale': ProductStatus('offsale', u'售罄', u'今日售罄，明天11点起售', '#333333'),
    'wallet_onsale': ProductStatus('onsale', u'购买', u'', '#6192B3'),
    'hoarder_onsale': ProductStatus('onsale', u'购买', u'', '#F5A623'),
    'soldout': ProductStatus('soldout', u'售罄', u'今日售罄，明天11点起售', '#333333'),
    'presale': ProductStatus('presale', u'11点起售', u'11点起售，敬请期待', '#DEDEDE')
}
