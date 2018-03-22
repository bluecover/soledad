# coding: utf-8

from mock import patch
from pytest import raises

from core.models.profile.identity import (
    Identity, IdentityValidationError, has_real_identity)
from core.models.hoard.profile import HoardProfile
from core.models.mixin.props import PropsItem
from .framework import BaseTestCase


class IdentityTestCase(BaseTestCase):

    def setUp(self):
        super(IdentityTestCase, self).setUp()
        self.user = self.add_account(mobile='13800138000')
        self.old_user = self.add_account(email='foo@guihua.dev')

    def test_get_nothing(self):
        assert not Identity.get(self.user.id_)

    def test_create(self):
        identity = Identity.save(self.user.id_, u'张无忌', u'44011320141005001X')
        assert has_real_identity(self.user)
        assert identity and identity.id_
        assert identity.id_ == self.user.id_
        assert identity.person_name == u'张无忌'
        assert identity.person_ricn == u'44011320141005001X'
        assert identity.masked_name == u'**忌'

    def test_remove(self):
        Identity.save(self.user.id_, u'张无忌', u'44011320141005001X')
        identity = Identity.get(self.user.id_)
        assert identity.person_name == u'张无忌'
        Identity.remove(self.user.id_)
        assert not Identity.get(self.user.id_)

    def test_create_by_old_user(self):
        Identity.save(self.old_user.id_, u'张无忌', u'44011320141005001X')
        assert not has_real_identity(self.user)

    def test_create_failed(self):
        # TODO IdentityException UnitTest
        with raises(IdentityValidationError):
            Identity.save(self.user.id_, u'张无忌' * 10, u'44011320141005001X')
        with raises(IdentityValidationError):
            Identity.save(self.user.id_, u'张无忌', u'440113201410050011')
        Identity.save(self.user.id_, u'张无忌', u'44011320141005001X')

    def test_update(self):
        assert not Identity.get(self.user.id_)
        assert not has_real_identity(self.user)
        Identity.save(self.user.id_, u'张无忌', u'44011320141005001X')
        Identity.save(self.user.id_, u'谢逊', u'360426199101010071')
        identity = Identity.get(self.user.id_)
        assert has_real_identity(self.user)
        assert identity and identity.id_
        assert identity.id_ == self.user.id_
        assert identity.person_name == u'谢逊'
        assert identity.person_ricn == u'360426199101010071'
        assert identity.masked_name == u'*逊'

    @patch('core.models.profile.identity.rsyslog')
    def test_migrate(self, rsyslog):
        old_user = self.add_account('old@guihua.dev', 'foobaz', 'foo')
        assert not Identity.get(old_user.id_)
        assert not has_real_identity(self.user)

        old_profile = OldHoardProfile.add(old_user.id_)
        old_profile.person_name = u'谢逊'
        old_profile.person_ricn = u'44011320141005001X'

        identity = Identity.get(old_user.id_)
        assert rsyslog.send.called
        assert identity and identity.id_ == old_user.id_
        assert identity.person_name == u'谢逊'
        assert identity.person_ricn == u'44011320141005001X'

        # migrated automatically
        old_profile.person_name = ''
        old_profile.person_ricn = ''
        identity = Identity.get(old_user.id_)
        assert identity and identity.id_ == old_user.id_
        assert identity.person_name == u'谢逊'
        assert identity.person_ricn == u'44011320141005001X'


class OldHoardProfile(HoardProfile):
    person_name = PropsItem('person_name', default='', secret=True)
    person_ricn = PropsItem('person_ricn', default='', secret=True)
