# coding: utf-8

from core.models.oauth import OAuthClient, OAuthScope
from .framework import BaseTestCase


class OAuthClientTestCase(BaseTestCase):

    def test_new_client(self):
        client = OAuthClient.add(
            name=u'规划君', redirect_uri='http://example.com')
        assert client.id_ > 0
        assert len(client.client_id) == 30
        assert len(client.client_secret) == 30
        assert client.client_type == 'confidential'
        assert client.redirect_uris == ['http://example.com']
        assert client.default_redirect_uri == 'http://example.com'
        assert client.default_scopes == ['basic']

    def test_new_client_without_callback(self):
        client = OAuthClient.add(name='规划君 Android')
        assert client.id_ > 0
        assert len(client.client_id) == 30
        assert len(client.client_secret) == 30
        assert client.client_type == 'confidential'
        assert client.redirect_uris == []
        assert client.default_redirect_uri is None
        assert client.default_scopes == ['basic']

    def test_client_edit(self):
        client = OAuthClient.add(name=u'规划君 Android',
                                 redirect_uri='http://b.cn',
                                 allowed_grant_types=['password'],
                                 allowed_response_types=['code'],
                                 allowed_scopes={OAuthScope.basic})

        assert client.name == u'规划君 Android'
        assert client.redirect_uri == 'http://b.cn'
        assert client.redirect_uris == ['http://b.cn']
        assert client.default_redirect_uri == 'http://b.cn'
        assert client.allowed_scopes == {OAuthScope.basic}
        assert client.default_scopes == ['basic']

        client.edit(u'规划',
                    'http://g.cn',
                    ['authorization_code'],
                    ['token'],
                    {OAuthScope.user_info})

        assert client.name == u'规划'
        assert client.redirect_uri == 'http://g.cn'
        assert client.redirect_uris == ['http://g.cn']
        assert client.default_redirect_uri == 'http://g.cn'
        assert client.allowed_grant_types == ['authorization_code']
        assert client.allowed_response_types == ['token']
        assert client.allowed_scopes == {OAuthScope.user_info}
        assert client.default_scopes == ['user_info']

        client = OAuthClient.get(client.id_)
        assert client.name == u'规划'
        assert client.redirect_uri == 'http://g.cn'
        assert client.redirect_uris == ['http://g.cn']
        assert client.default_redirect_uri == 'http://g.cn'
        assert client.allowed_grant_types == ['authorization_code']
        assert client.allowed_response_types == ['token']
        assert client.allowed_scopes == {OAuthScope.user_info}

    def test_get_by_client_id(self):
        client = OAuthClient.add(name=u'规划君 Android')
        assert client.get_by_client_id(client.client_id) == client

    def test_validate_scopes(self):
        client = OAuthClient.add(name=u'规划君 Android')
        assert client.validate_scopes([])
        assert client.validate_scopes(['basic'])
        assert not client.validate_scopes(['password'])
