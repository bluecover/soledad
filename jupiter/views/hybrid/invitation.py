# coding: utf-8

from __future__ import absolute_import

from flask import url_for, g
from flask_mako import render_template

from jupiter.utils.hybrid import hybrid_view
from core.models.group import invitation_reminder_group
from core.models.invitation import Invitation, transform_digit
from core.models.welfare.package.kind import invite_investment_package
from core.models.profile.identity import has_real_identity
from .blueprint import create_blueprint


bp = create_blueprint('invitation', __name__, url_prefix='/hybrid/invite')


@bp.route('/app', methods=['GET'])
@hybrid_view(['savings_w'])
def invitation():
    invitation_reminder_group.remove_member(g.user.id)
    # 50为临时性限制单页显示数目，防止炸裂，以后考虑分页.
    invitation_ids = Invitation.get_ids_by_inviter_id(g.user.id_)[:50]
    invitations = Invitation.get_multi(invitation_ids)
    has_identity = has_real_identity(g.user)
    code = transform_digit(int(g.user.id_))
    invite_url = url_for('invite.invite', inviter=code, _external=True)
    package_worth = invite_investment_package.firewood_wrapper.worth
    total_award = sum([invite_investment_package.firewood_wrapper.worth for invitation in
                       invitations if invitation.status is Invitation.Status.accepted])
    return render_template('invite/invite_app.html', has_identity=has_identity,
                           invitations=invitations, total_award=total_award, invite_url=invite_url,
                           package_worth=package_worth)
