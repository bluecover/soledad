# coding: utf-8

from __future__ import unicode_literals

from datetime import datetime, timedelta

from mock import patch

from core.models.oauth import OAuthGrant
from .framework import BaseTestCase


class OAuthGrantTestCase(BaseTestCase):

    def setUp(self):
        super(OAuthGrantTestCase, self).setUp()
        self.user = self.add_account('foo@guihua.dev', 'foobar', 'Foo')
        self.client_patcher = patch('core.models.oauth.grant.OAuthClient')
        self.client_class = self.client_patcher.start()
        self.client = self.client_class.get(1024)
        self.client.id_ = 1024

    def tearDown(self):
        self.client_patcher.stop()
        super(OAuthGrantTestCase, self).tearDown()

    def _create_grant_token(self, code):
        return OAuthGrant.add(
            client_pk=self.client.id_,
            code=code,
            redirect_uri='http://guihua.dev',
            scopes=['foo', 'bar'],
            user_id=self.user.id_)

    def test_new_grant(self):
        grant = self._create_grant_token('000')
        assert grant.id_ > 0
        assert grant.expires <= datetime.now() + timedelta(seconds=120)
        assert grant.user == self.user
        assert grant.client == self.client

    def test_delete_grant(self):
        grant = self._create_grant_token('000')
        grant.delete()
        assert not OAuthGrant.get(grant.id_)

    def test_get_by_code(self):
        grant = self._create_grant_token('42342')
        assert OAuthGrant.get_by_code(self.client.id_, '42342') == grant
        assert not OAuthGrant.get_by_code(self.client.id_ + 1, '42342')
        grant.delete()
        assert not OAuthGrant.get_by_code(self.client.id_, '42342')
