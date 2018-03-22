# coding: utf-8

"""
创建测试用礼券
"""

from libs.utils.log import bcolors
from core.models.user.account import Account
from core.models.welfare.package.kind import test_newcomer_center


if __name__ == '__main__':
    bcolors.run('Add coupons.')

    # in init_user we create test%i@guihua.com
    try:
        emails = ['test%s@guihua.com' % r for r in range(9)]
        emails.append('zw@guihua.com')
        for email in emails:
            user = Account.get_by_alias(email)
            package = test_newcomer_center.distributor.bestow(user)
            package.unpack(user)
        bcolors.success('Init coupon done.')
    except Exception as e:
        bcolors.fail('Init coupon fail: %s.' % e)
