# coding:utf-8

from datetime import datetime

from libs.db.store import db
from ._base import PackageDistributor


class InvitationReward(PackageDistributor):
    """被邀请人购买第一笔订单后給邀请人发放红包"""

    table_name = 'coupon_package_investment_invitation_reward'

    def can_obtain(self, user, invite):
        from core.models.invitation.invitation import Invitation
        if invite.status is Invitation.Status.accepted:
            return True

    def bestow(self, user, invite):
        from ..package import Package

        if not self.can_obtain(user, invite):
            return

        package = Package.create(self.kind)
        self._add(invite, package)
        return package

    def _add(self, invitation, package):
        sql = ('insert into {.table_name} (invitation_id, package_id,'
               ' creation_time) values (%s, %s, %s)').format(self)
        params = (invitation.id_, package.id_, datetime.now())
        db.execute(sql, params)
        db.commit()
