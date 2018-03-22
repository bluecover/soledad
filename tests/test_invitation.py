# coding:utf-8

from mock import patch

from core.models.group.group import Group
from core.models.welfare.package.package import Package
from core.models.invitation.invitation import Invitation
from core.models.welfare.package.kind import invite_investment_package
from .framework import BaseTestCase


class InvitationTest(BaseTestCase):
    def setUp(self):
        super(InvitationTest, self).setUp()
        self.inviter = self.add_account(mobile='13800000000')
        self.invitee = self.add_account(mobile='13900000000')

        self.invite = Invitation.add(self.inviter, self.invitee, Invitation.Kind.invite_investment)

    def tearDown(self):
        super(InvitationTest, self).tearDown()

    def test_add_invitation(self):
        assert isinstance(self.invite, Invitation)
        assert self.invite.invitee_id == self.invitee.id_
        assert self.invite.inviter_id == self.inviter.id_
        assert self.invite.kind is Invitation.Kind.invite_investment
        assert self.invite.kind.award_package is invite_investment_package
        assert self.invite.status is Invitation.Status.sent

    def test_get_by_invitee_id(self):
        invite = Invitation.get_by_invitee_id(self.invitee.id_)
        assert isinstance(invite, Invitation)
        assert invite.invitee_id == self.invitee.id_

    def test_get_mutli_by_inviter_id(self):
        ids = Invitation.get_ids_by_inviter_id(self.inviter.id_)
        invites = Invitation.get_multi(ids)
        for invite in invites:
            assert invite.inviter_id == self.inviter.id_

    @patch.object(Package, 'unpack')
    @patch.object(Group, 'add_member')
    def test_update_status(self, group_add_member, package_unpack):
        invite = Invitation.get_by_invitee_id(self.invitee.id_)
        assert invite.status is Invitation.Status.sent
        assert invite.is_usable
        invite.accept()
        assert invite.status is Invitation.Status.accepted
        assert invite.is_usable is False
