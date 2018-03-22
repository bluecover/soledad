# coding: utf-8

from core.models.advert import advert_list
from jupiter.utils.inhouse import check_is_inhouse


test_url = {
    'show': 'api/v1/advert/show',
    'mark': 'api/v1/advert/mark'
    }


def test_advert_show(client, oauth_token):
    client.load_token(oauth_token)

    #: common
    r = client.get(test_url['show'])
    assert r.status_code == 200
    assert isinstance(r.data['data']['is_read'], bool)
    assert 'advert' in r.data['data']

    def check_advert_for_available():
        advert_available = (
            [advert for advert in advert_list if advert.is_effective] if check_is_inhouse() else [])
        return len(advert_available) == 1

    if check_advert_for_available():

        r = client.get(test_url['show'])
        assert r.status_code == 200
        assert r.data['data']['is_read'] is False
        assert r.data['data']['advert']['advert_id']
        advert_id = r.data['data']['advert']['advert_id']

        r = client.post(test_url['mark'], data={'advert_id': advert_id})
        assert r.status_code == 200
        assert r.data['data']['advert_id'] == advert_id

        r = client.get(test_url['show'])
        assert r.status_code == 200
        assert r.data['data']['is_read'] is True
