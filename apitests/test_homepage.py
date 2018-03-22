# coding: utf-8

from __future__ import absolute_import, unicode_literals


testing_urls = {
    'banner': '/api/v2/homepage/banner',
    'bulletin': '/api/v2/homepage/bulletin'
}


def test_banner(client, oauth_client):
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}
    r = client.get(testing_urls['banner'], headers=headers)
    assert r.status_code == 200
    assert r.data['success'] is True
    assert 'banners' in r.data['data']
    assert 'timestamp' in r.data['data']
    banners = r.data['data']['banners']
    assert isinstance(banners, list)
    if len(banners) > 0:
        banner = banners[0]
        assert 'image_url' in banner
        assert 'link_url' in banner


def test_bulletin(client, oauth_client):
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}
    r = client.get(testing_urls['bulletin'], headers=headers)
    assert r.status_code == 200
    assert r.data['success'] is True
    data = r.data['data']
    if data != {}:
        assert 'id' in r.data['data']
        assert 'title' in r.data['data']
        assert 'content' in r.data['data']
        assert 'link_url' in r.data['data']
        assert 'timestamp' in r.data['data']
