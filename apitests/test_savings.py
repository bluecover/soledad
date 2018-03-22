# coding: utf-8

from __future__ import absolute_import, unicode_literals


testing_urls = {
    'products': '/api/v1/savings/products',
    'mine': '/api/v1/savings/mine',
}


def test_savings_products(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['products'])
    assert r.status_code == 200
    assert r.data['success'] is True
    # assert r.data['data'] == []


def test_savings_mine(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['mine'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'] == {
        'amount': 0,
        'daily_profit': 0,
        'total_profit': 0,
        'total_orders': 0,
        'has_sxb_account': False
    }


def test_gone(client, oauth_token):
    client.load_token(oauth_token)

    r = client.post('/api/v1/savings/yixin/auth', data={})
    assert r.status_code == 410

    r = client.post('/api/v1/savings/yixin/auth/verify', data={})
    assert r.status_code == 410

    r = client.post('/api/v1/savings/order', data={})
    assert r.status_code == 410

    r = client.post('/api/v1/savings/order/10001/confirm', data={})
    assert r.status_code == 410

    r = client.post('/api/v1/savings/order/10001/verify', data={})
    assert r.status_code == 410
