# coding: utf-8

"""
创建测试用兑换码
"""
from datetime import datetime, timedelta

from libs.utils.log import bcolors
from core.models.redeemcode.redeemcode import RedeemCode
from core.models.redeemcode.activity import fanmeeting_gold, fanmeeting_silver


def main():
    bcolors.run('Add redeem code.')
    effective_time = datetime.now() - timedelta(days=1)
    expire_time = datetime.now() + timedelta(days=30)
    try:
        # 创建100个可被使用一次的兑换码
        RedeemCode.create_multi_codes(fanmeeting_gold.id_, RedeemCode.Kind.normal_package.value,
                                      u'测试用兑换码', 1, 100, effective_time, expire_time)
        # 创建一个可使用100次的兑换码
        RedeemCode.create(fanmeeting_silver.id_, RedeemCode.Kind.normal_package.value,
                          u'测试用兑换码', 100, None, effective_time, expire_time)
        bcolors.success('Init redeemcode done.')
    except Exception as e:
        bcolors.fail('Init redeemcode fail: %s.' % e)


if __name__ == '__main__':
    main()
