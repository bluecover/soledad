# coding: utf-8

from __future__ import absolute_import, unicode_literals


testing_urls = {
    'record': '/api/v1/welfare/red-packets/record',
    'red-packets': 'api/v1/welfare/mine/red-packets',
    'mine-coupon': 'api/v1/welfare/mine/coupons'
}

SPEC_DESCRIPTION = '''
1.攒钱时，可按5‰比例抵扣，最小抵扣单位1元
2.攒钱红包无有效期限制
3.攒钱红包可用于“自由期限”及“固定期限产品”
4.好规划网保留最终解释权'''.strip()


def test_mine_coupon(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['mine-coupon'])
    assert r.status_code == 200
    assert r.data['success'] is True
    # TODO fake data
    assert r.data['data'] == {
        'total_available_coupons': 0,
        'coupons': []
    }


def test_records(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['record'])
    assert r.status_code == 200
    assert r.data['success'] is True
    # TODO fake data
    assert r.data['data'] == {
        'records': []}


def test_red_packets(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['red-packets'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'] == {
        'balance': 0,
        'spec_description': SPEC_DESCRIPTION
    }
