# coding: utf-8

from core.models.hoarder.vendor import Provider

sale_display_text = {
    'early_morning_off_sale': (u'0点起售', u'该产品暂未开售'),
    'middle_morning_off_sale': (u'10点起售', u'该产品暂未开售'),
    'late_morning_off_sale': (u'11点起售', u'该产品暂未开售'),
    'early_morning_sold_out': (u'售罄', u'今日售罄，明日0点起售'),
    'middle_morning_sold_out': (u'售罄', u'今日售罄，明日10点起售'),
    'late_morning_sold_out': (u'售罄', u'今日售罄，明日11点起售'),
    'on_sale': (u'购买', '')}

PRODUCT_PROFILE = {
    Provider.sxb: {
        'new_comer': {
            'activity_title': u'新手专享产品是什么？',
            'activity_introduction': (
                '为了支持各位新朋友开展攒钱大业，好规划特意推出了『新手专享』福利。'
                '在原有5.6%年化收益率的基础上，为新用户准备了持有前七日加息至15%的新手专享产品。'
                '加息期间如有赎回，则加息终止，收益率恢复为5.6%'),
            'product_title': u'新手专享',
            'product_introduction': u'加息7日后收益恢复至5.6% '
            },
        'sxb': {
            'activity_title': u'随心攒产品是什么？',
            'activity_introduction': (
                '随心攒是好规划与宜信联合推出的，具有活期性质的混合型P2P产品。\n'
                '该产品具有以下特点：\n'
                '1、100元起投，最多可持有10万元 \n'
                '2、每日可提现3万元，提现后通常下一工作日到账 \n'
                '因此，随心攒是一款收益高于货币基金，'
                '同时具有固定期限产品所不具备的灵活性理财产品。'),
            'product_title': u'随心攒',
            'product_introduction': u'随时存取，按日计息'
            }
        }
    }
