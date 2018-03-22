# coding:utf-8

from datetime import datetime, timedelta
from mock import patch

from core.models.group.group import Group
from core.models.welfare.package.package import Package
from core.models.redeemcode.redeemcode import RedeemCode


@patch.object(Package, 'unpack')
@patch.object(Group, 'add_member')
def test_redeem_code(group_add_member, package_unpack, client, oauth_token, identity):
    url = 'api/v1/redeemcode/code'
    client.load_token(oauth_token)
    date_begin = datetime.now()
    date_end = date_begin + timedelta(days=1)
    redeem_code = RedeemCode.create(1, 1, u'测试', 1, None, date_begin, date_end)
    redeem_code3 = RedeemCode.create(1, 1, u'测试', 1, None, date_begin, date_end)
    expire_code = RedeemCode.create(1, 1, u'测试', 1, None, date_begin, date_begin)
    ineffective_code = RedeemCode.create(1, 1, u'测试', 1, None, date_end, date_begin)

    # empty redeem_code
    r = client.post(url, data={'redeem_code': ''})
    assert r.data['messages']['redeem_code'][0] == u'请输入兑换码'
    # no redeem_code
    r = client.post(url, data={'redeem_code': 'TEST1234'})
    assert r.data['messages']['_'][0] == u'您输入的兑换码不存在'
    # expire redeem_code
    r = client.post(url, data={'redeem_code': expire_code.code})
    assert r.data['messages']['_'][0] == u'您输入的兑换码已失效'
    # ineffective redeem_code
    r = client.post(url, data={'redeem_code': ineffective_code.code})
    assert r.data['messages']['_'][0] == u'您输入的兑换码未生效，请在活动期间使用'
    # normal redeem_code
    r = client.post(url, data={'redeem_code': redeem_code.code})
    assert r.status_code == 200
    assert r.data['success'] is True
    # used redeem_code
    r = client.post(url, data={'redeem_code': redeem_code.code})
    assert r.status_code == 403
    assert r.data['messages']['_'][0] == u'您输入的兑换码已使用'
    # RedemptionBeyondLimitPerUser redeem_code3
    r = client.post(url, data={'redeem_code': redeem_code3.code})
    assert r.status_code == 403
    assert r.data['messages']['_'][0] == u'您使用兑换码的次数已超过本次活动上限'
