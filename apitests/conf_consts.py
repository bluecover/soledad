# coding: utf-8

from __future__ import absolute_import, unicode_literals

from .utils import get_start_date, get_op_days_time
from sxblib.consts import OrderStatus
from xmlib.consts import OrderStatus as XMOrderStatus


class ProductConsts(object):
    XINMI_TOKEN = u'1234abcd'

    XINMI_PRODUCT_ID = '2015121413474335539'

    XINMI_PRODUCT_INFO = {
        'product_id': XINMI_PRODUCT_ID,
        'name': '固定期限类产品测试',
        'category': 6,
        'status': 1,
        'pre_time': get_op_days_time(-20),  # '2016-03-08 00:00:15',
        'open_time': get_op_days_time(-20),  # '2016-03-08 00:00:15',
        'min_amount': 0.02,
        'max_amount': 1000000,
        'period_type': 2,
        'expire_date': get_op_days_time(180),  # '2016-07-13 00:00:00',
        'expire_period': 90,
        'expire_period_unit': 3,
        'lockup_period': 0,
        'lockup_period_unit': 0,
        'return_rate_type': 1,
        'return_rate': 0.085,
        'effect_day_type': 1,
        'effect_day': 1,
        'effect_day_unit': 1,
        'currency_type': 1,
        'remark': '固定期限类产品测试',
        'quota': 10000000,
        'update_time': get_op_days_time(-20),  # '2016-03-08 11:38:52',
        'create_time': '2015-02-14 13:49:35',
        'sale_time': None,
        'total_quota': 0,
        'today_quota': 0,
        'total_amount': 0,
        'today_buy_number': 0,
        'total_buy_number': 0,
        'user_buy_amount': 0,
        'user_max_amount': 0,
        'total_buy_amount': 0,
        'is_redeem': 2,
        'min_redeem_amount': 0,
        'max_redeem_amount': 0,
        'day_redeem_amount': 0,
        'add_year_rate': 0
    }

    XINMI_RESPONSE_BANKCARD = {
        u'amount_limit': 200000,
        u'bank': {
            u'icon_url': {
                u'hdpi': u'https://dn-guihua-static.qbox.me/img/logo/banks/4@2x.png',
                u'mdpi': u'https://dn-guihua-static.qbox.me/img/logo/banks/4.png'
            },
            u'name': u'建设银行',
            u'telephone': u'95533',
            u'uid': u'4'
        },
        u'card_number': u'62****0009',
        u'is_bound_in_wallet': False,
        u'is_default': True,
        u'local_bank_name': u'西夏支行',
        u'mobile_phone': u'138****8000',
        u'province_id': u'110000',
        u'uid': u'1'
    }

    XINMI_RESPONSE_PRODUCT = {
        u'activity_type': u'',
        u'annual_rate_layers': [],
        u'increasing_step': 1,
        u'is_sold_out': False,
        u'is_taken_down': False,
        u'max_amount': 1000000.0,
        u'min_amount': 1.0,
        u'partner': u'xm',
        u'profit_percent': {
            u'max': 8.5, u'min': 8.5
        },
        u'profit_period': {
            u'max': {
                u'unit': u'day',
                u'value': 90
            },
            u'min': {
                u'unit': u'day',
                u'value': 90}},
        u'start_date': get_start_date(),  # u'2016-04-18',
        u'uid': u'2015121413474335539',
        u'wrapped_product_id': u''
    }

    XINMI_RESPONSE_CREATE_USER = {
        'merchant_id': 'abc',
        'is_new': False,
        'status': '01',
        'user_id': 'NSabc0000952190',
        'remark': None
    }

    XINMI_RESPONSE_ORDER_APPLY = {
        u'effect_date': None,
        u'remark': None,
        u'total_amount': 1000.0,
        u'buy_amount': 1000.0,
        u'discount_fee': 0.0,
        u'buy_time': u'2016-05-13 11:15:29',
        u'last_buy_time': u'2016-05-13 12:15:29',
        u'return_rate': 0.085,
        'order_id': u'd148914718bb11e6b8e0ac87a',
        u'pay_code': u'Ptest1236927',
        u'order_status': XMOrderStatus.waiting,
        u'return_amount': 20.96,
        u'app_order_id': u'abcd148914718bb11e6b8e0ac87a',
        u'investment_id': u'TZ16051311360344977408',
        u'buy_fee': 0.0
    }

    XINMI_RESPONSE_CONFIRM_APPLY = {
        u'app_order_id': u'abcd148914718bb11e6b8e0ac87a',
        u'order_status': XMOrderStatus.payed,
        u'remark': None,
        'order_id': u'd148914718bb11e6b8e0ac87a'}

    SXB_VENDOR_PRODUCT_ID = ['2016030714054079034', '2016032811165314116']

    SXB_PRODUCT_INFO = {
        '2016030714054079034': {
            u'effect_day': 1,
            u'sale_time': None,
            u'is_redeem': 1,
            u'name': u'日日盈新结算测试舞动',
            u'effect_day_unit': 1,
            u'period_type': 3,
            u'return_rate_type': 2,
            u'min_amount': 1,
            u'effect_day_type': 1,
            u'min_redeem_amount': 100,
            u'product_id': u'2016030714054079034',
            u'total_quota': 30000000,
            u'max_redeem_amount': 30000,
            u'return_rate': 0.1125,
            u'total_buy_amount': 10000000,
            u'day_redeem_amount': 30000,
            u'open_time': u'2016-03-07 00:00:13',
            u'max_amount': 1000000,
            u'today_quota': 1000000,
            u'add_year_rate': 0.02,
            u'quota': 994000,
            u'remark': u'日日盈新结算测试舞动',
            u'total_amount': 20374068.0
        },
        '2016032811165314116': {
            u'effect_day': 1,
            u'sale_time': None,
            u'is_redeem': 1,
            u'name': u'日日盈新结算测试勿动',
            u'effect_day_unit': 1,
            u'period_type': 3,
            u'return_rate_type': 2,
            u'min_amount': 1,
            u'effect_day_type': 1,
            u'min_redeem_amount': 1,
            u'product_id': u'2016032811165314116',
            u'total_quota': 1000000,
            u'max_redeem_amount': 100000,
            u'return_rate': 0.05,
            u'total_buy_amount': 100000,
            u'day_redeem_amount': 100000,
            u'open_time': u'2016-03-07 00:00:13',
            u'max_amount': 100000,
            u'today_quota': 100000,
            u'add_year_rate': 0,
            u'quota': 100000,
            u'remark': u'日日盈新结算测试勿动',
            u'total_amount': 49030.0
        }
    }

    SXB_RESPONSE_ORDER_APPLY = {
        u'effect_date': None,
        u'remark': None,
        u'total_amount': 1000.0,
        u'buy_amount': 1000.0,
        u'discount_fee': 0.0,
        u'buy_time': u'2016-05-13 14:31:22',
        u'last_buy_time': u'2016-05-13 15:31:22',
        u'return_rate': 0.0,
        'order_id': u'2e8af3ee18d711e6b53bac87a',
        u'pay_code': u'Ptest1231819',
        u'order_status': OrderStatus.waiting,
        u'return_amount': 0.0,
        u'app_order_id': u'abc2e8af3ee18d711e6b53bac87a',
        u'investment_id': u'TZ16051314515613077411',
        u'buy_fee': 0.0}

    SXB_RESPONSE_CONFIRM_APPLY = {
        u'app_order_id': u'abc3b0f2f1c18f611e6af00ac87a',
        u'order_status': OrderStatus.payed,
        u'remark': None,
        'order_id': u'2e8af3ee18d711e6b53bac87a'
    }
