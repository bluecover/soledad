# coding: utf-8

from __future__ import absolute_import, unicode_literals

# from pytest import mark


testing_urls = {
    'mine': '/api/v1/coupons/mine',
}


def test_coupons_mine(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['mine'])
    assert r.status_code == 410
    assert r.data['success'] is False
    assert u'版本过低' in r.data['messages']['_'][0]
