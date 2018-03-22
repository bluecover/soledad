# coding: utf-8

from __future__ import absolute_import, unicode_literals

from pytest import mark


testing_urls = {
    'banks': '/api/v1/data/banks',
    'provinces': '/api/v1/data/division/2012/provinces',
    'prefectures': '/api/v1/data/division/2012/110000/prefectures',
    'counties': '/api/v1/data/division/2012/110100/counties',
}


@mark.parametrize('url', testing_urls.values())
def test_auth(url, client):
    client.drop_token()
    r = client.get(url)
    assert r.status_code == 401


def test_banks(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['banks'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'][0] == {
        'uid': '6',
        'name': '招商银行',
        'telephone': '95555',
        'icon_url': {
            'hdpi': 'https://dn-guihua-static.qbox.me/img/logo/banks/6@2x.png',
            'mdpi': 'https://dn-guihua-static.qbox.me/img/logo/banks/6.png',
        },
    }


def test_banks_in_partner(client, oauth_token):
    client.load_token(oauth_token)

    # 指旺
    r = client.get('{0}?partner=zw'.format(testing_urls['banks']))
    assert r.status_code == 200
    assert r.data['success'] is True

    names = {bank['name'] for bank in r.data['data']}
    assert u'工商银行' in names
    assert u'华夏银行' not in names

    # 中山证券
    r = client.get('{0}?partner=zs'.format(testing_urls['banks']))
    assert r.status_code == 200
    assert r.data['success'] is True

    names = {bank['name'] for bank in r.data['data']}
    assert u'中信银行' in names
