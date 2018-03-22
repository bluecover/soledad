# -*- coding: utf-8 -*-

import decimal
import datetime

ZWLIB_ERROR_MAPPING = {
    'param inconsistent reserve_phone':
        u'您输入的手机号与银行预留手机号不一致，请检查后重新提交',
}

ZWLIB_OFFLINE_TEXT = u'''
    攒钱助手 1 月 7 日凌晨 1:00 ~ 2:00 进行服务升级，请于升级完成后进行购买
'''.strip()

FETCH_LOANS_TIMEOUT = int(datetime.timedelta(days=1).total_seconds())
FETCH_LOANS_LIMIT_TIMES = 2

# fdb milestone decides newcomer ladder
FDB_ALLOCATION_MILESTONE = (decimal.Decimal('500000'), decimal.Decimal('1000000'))
NEWCOMER_ALLOCATION_LADDER = (decimal.Decimal('200000'), decimal.Decimal('400000'))

# zhiwang reserved amount to keep safe ending sale
ZW_SAFE_RESERVATION_AMOUNT = decimal.Decimal('5000')
