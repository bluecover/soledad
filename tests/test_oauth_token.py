# coding: utf-8

from datetime import datetime, timedelta

from mock import patch

from core.models.oauth import OAuthToken
from .framework import BaseTestCase


class OAuthTokenTestCase(BaseTestCase):

    def setUp(self):
        super(OAuthTokenTestCase, self).setUp()
        self.user = self.add_account('foo@guihua.dev', 'foobar', 'Foo')
        self.client_patcher = patch('core.models.oauth.token.OAuthClient')
        self.client_class = self.client_patcher.start()
        self.client = self.client_class.get(1024)
        self.client.id_ = 1024

    def tearDown(self):
        self.client_patcher.stop()
        super(OAuthTokenTestCase, self).tearDown()

    def _add_token(self, access_token='access', refresh_token='refresh',
                   client_id=None, expires_in=3600):
        return OAuthToken.add(
            client_id or self.client.id_, self.user.id_, ['foo', 'bar'],
            access_token, refresh_token, expires_in)

    def test_new_token(self):
        token = self._add_token(expires_in=42)
        assert token.id_ > 0
        assert token.client == self.client
        assert token.user == self.user
        assert token.expires.date() == datetime.utcnow().date()
        assert token.expires <= datetime.utcnow() + timedelta(seconds=42)
        assert token.access_token == 'access'
        assert token.refresh_token == 'refresh'
        assert token.scopes == ['foo', 'bar']

    def test_delete_token(self):
        token = self._add_token()
        token_id = token.id_
        token.delete()
        assert not OAuthToken.get(token_id)

    def test_get_by_token(self):
        token = self._add_token()
        assert OAuthToken.get_by_access_token('access') == token
        assert OAuthToken.get_by_refresh_token('refresh') == token

    def test_get_by_user(self):
        token1 = self._add_token('access1', 'refresh1')
        token2 = self._add_token('access2', 'refresh2')
        tokens = OAuthToken.get_multi_by_user(self.user.id_)
        assert {token1, token2} == set(tokens)

    def test_freeze_token(self):
        token1 = self._add_token('access1', 'refresh1')
        token2 = self._add_token('access2', 'refresh2', client_id=42)
        assert not token1.is_frozen
        assert not token2.is_frozen

        token1.freeze()
        assert token1.is_frozen
        assert not token2.is_frozen

        token1 = OAuthToken.get(token1.id_)
        token2 = OAuthToken.get(token2.id_)
        assert token1.is_frozen
        assert not token2.is_frozen

    def test_vacuum(self):
        token1 = self._add_token('access1', 'refresh1', expires_in=0)
        token2 = self._add_token('access2', 'refresh2', client_id=42)

        assert OAuthToken.get(token1.id_)
        assert OAuthToken.get(token2.id_)

        OAuthToken.vacuum()
        assert not OAuthToken.get(token1.id_)
        assert OAuthToken.get(token2.id_)
