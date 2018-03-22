# coding: utf-8

import re
from datetime import datetime, timedelta

from flask import Blueprint, url_for, g, abort, redirect, request, after_this_request
from flask_mako import render_template

from core.models.profile.identity import has_real_identity, Identity
from core.models.user.account import Account
from core.models.user.consts import ACCOUNT_REG_TYPE
from core.models.user.register import generate_nickname
from core.models.utils.validator import validate_phone
from core.models.group import invitation_reminder_group
from core.models import errors
from core.models.invitation import Invitation, transform_digit
from core.models.invitation.consts import INVITER_KEY, INVITER_KEY_EXPIRE_HOURS
from core.models.welfare.package.kind import invite_investment_package
from core.models.welfare import FirewoodWorkflow
from core.models.gift import UserLottery, UserLotteryNum

bp = Blueprint('invite', __name__, url_prefix='/invite')


@bp.route('/', methods=['GET'])
def invite():
    code = request.args.get(
        'inviter', None) or request.cookies.get(INVITER_KEY)
    is_lottery = request.args.get('lottery', False)
    if not code:
        return abort(404)
    # 兼容已分享错误链接
    rs = re.search('^(\d+).*', code)
    if not rs:
        abort(404)
    code = rs.group(1)
    user_id = transform_digit(code)

    if g.user:
        if g.user.id_ == str(user_id):
            if not is_lottery:
                return redirect(url_for('.mine'))

            g.firewood_flow = FirewoodWorkflow(g.user.id_)
            if not g.firewood_flow.account_uid:
                return redirect(url_for('profile.auth.supply', next=request.path))

            user_lottery = UserLottery.get(g.user.id_)
            return render_template('activity/lottery/index.html',
                                   remain_num=user_lottery.remain_num)

        else:
            return redirect(url_for('.login'))

    user = Account.get(user_id)
    if not user:
        abort(404)

    UserLotteryNum.add_by_share(user.id_)

    @after_this_request
    def set_cookie(response):
        response.set_cookie(
            key=INVITER_KEY, value=str(code),
            expires=datetime.now() + timedelta(hours=INVITER_KEY_EXPIRE_HOURS))
        return response

    identity = Identity.get(user_id)
    inviter_name = identity.masked_name if identity else generate_nickname(user.mobile,
                                                                           ACCOUNT_REG_TYPE.MOBILE)
    return render_template('invite/invite.html', inviter_name=inviter_name)


@bp.route('/register', methods=['POST'])
def register():
    mobile = request.form.get('mobile')
    error = validate_phone(mobile)
    code = request.cookies.get(INVITER_KEY)
    if error != errors.err_ok:
        return redirect(url_for('.invite', inviter=code))

    user = Account.get_by_alias(mobile)
    if user and not user.need_verify():
        return redirect(url_for('.login', inviter=code))
    return render_template('invite/register.html', mobile=mobile)


@bp.route('/login', methods=['GET'])
def login():
    return render_template('invite/old_user.html')


@bp.route('/success')
def success():
    if not g.user:
        return redirect(url_for('accounts.login.login'))
    return render_template('invite/register_success.html')


@bp.route('/mine')
def mine():
    if not g.user:
        return redirect(url_for('accounts.login.login', next=url_for('.mine')))
    invitation_reminder_group.remove_member(g.user.id)
    code = transform_digit(int(g.user.id_))
    has_identity = has_real_identity(g.user)
    invite_url = url_for('.invite', inviter=code, _external=True)
    # 50为临时性限制单页显示数目，防止炸裂，以后考虑分页.
    invitation_ids = Invitation.get_ids_by_inviter_id(g.user.id_)[:50]
    invitations = Invitation.get_multi(invitation_ids)
    package_worth = invite_investment_package.firewood_wrapper.worth
    total_award = sum([invite_investment_package.firewood_wrapper.worth for invitation in
                       invitations if invitation.status is Invitation.Status.accepted])
    return render_template('invite/mine.html', has_identity=has_identity, invite_url=invite_url,
                           invitations=invitations, total_award=total_award,
                           package_worth=package_worth)
