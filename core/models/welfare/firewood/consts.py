# -*- coding: utf-8 -*-

import decimal


# 红包错误文案映射表
FIREWOOD_ERROR_MAPPINGS = {
    'insufficient_balance': u'您的红包余额不足，请检查是否有其他操作中的交易',
    'validation_error': u'红包使用遇到问题，请联系客服处理'
}

# 红包抵扣比例
FIREWOOD_BURNING_RATIO = decimal.Decimal('200')
