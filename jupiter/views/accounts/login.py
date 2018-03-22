# coding: utf-8

from flask import current_app, request, redirect, g, url_for, Response
from flask_mako import render_template

from core.models.user.consts import ACCOUNT_REG_TYPE
from core.models.user.account import Account
from jupiter.ext import weixin
from jupiter.views.accounts.utils.session import login_user, logout_user
from ._blueprint import create_blueprint


bp = create_blueprint('login', __name__)


@bp.route('/login')
def login():
    if g.user:
        return redirect(url_for('mine.mine.mine'))
    redirect_url = request.args.get('next')
    dcm = request.args.get('dcm')
    dcs = request.args.get('dcs')
    if not redirect_url:
        redirect_url = url_for('mine.mine.mine')
    return render_template(
            'accounts/login_and_register.html',
            redirect_url=redirect_url, dcm=dcm, dcs=dcs)


@bp.route('/logout')
def logout():
    if g.user:
        logout_user()
    return redirect('/accounts/login')


@bp.route('/logout/savings')
def logout_savings():
    if g.user:
        logout_user()
    return redirect(url_for('savings.landing.index', _external=True))


@bp.route('/login/weixin')
def weixin_login():
    next_url = request.args.get('next', url_for(
        'savings.landing.index', _external=True))
    callback_url = url_for(
        '.login_weixin_authorized', next=next_url, _external=True)
    return weixin.authorize(callback=callback_url)


@bp.route('/login/weixin/authorized')
def login_weixin_authorized():
    next_url = request.args.get('next', '/')
    response = weixin.authorized_response()
    if not response:
        current_app.logger.debug('weixin login has been denied by user')
        return redirect(next_url)  # denied by user

    openid = response['openid']
    account = Account.get_by_alias_type(openid, ACCOUNT_REG_TYPE.WEIXIN_OPENID)

    if account:
        login_user(account)

    return redirect(next_url)


@bp.route('/unbind_weixin', methods=['POST', 'GET'])
def unbind_weixin():
    text = ''
    show_btn = True

    if not request.user_agent.is_weixin_browser:
        return Response('this is not a weixin broswer')

    if request.method == 'POST':
        if not g.user:
            login_url = url_for('.login', next=url_for('.unbind_weixin'))
            return redirect(login_url)
        weixin_openid = g.user.weixin_openid
        if weixin_openid:
            g.user.remove_alias(ACCOUNT_REG_TYPE.WEIXIN_OPENID, weixin_openid)
            current_app.logger.debug('unbind success')
            text = '解绑成功'
            logout_user()
            show_btn = False
        else:
            text = '您的账号没有绑定微信'
    else:
        text = '解绑账号'

    return render_template('accounts/weixin_bind_result.html', **locals())


@bp.route('/bind_weixin')
def bind_weixin():
    if not request.user_agent.is_weixin_browser:
        return Response('this is not a weixin broswer')
    if g.user and g.user.weixin_openid:
        next_url = url_for('.weixin_auth')
    else:
        next_url = url_for('.login', next=url_for('.weixin_auth'))
    return redirect(next_url)


@bp.route('/weixin_auth')
def weixin_auth():
    next_url = request.args.get('next', url_for(
        'savings.landing.index', _external=True))
    callback_url = url_for(
        '.bind_weixin_authorized', next=next_url, _external=True)
    return weixin.authorize(callback=callback_url)


@bp.route('/bind_weixin/authorized')
def bind_weixin_authorized():
    text = ''
    show_btn = True
    next_url = request.args.get('next', '/')
    response = weixin.authorized_response()
    if not response:
        current_app.logger.debug('weixin login has been denied by user')
        return redirect(next_url)  # denied by user

    if not g.user:
        login_url = url_for('.login', next=url_for('.weixin_auth'))
        current_app.logger.debug('need login first: %r' % login_url)
        return redirect(login_url)

    openid = response.get('openid')

    if not openid:
        return redirect(next_url)  # denied by user

    account = Account.get_by_alias_type(openid, ACCOUNT_REG_TYPE.WEIXIN_OPENID)

    if account:
        if account.id != g.user.id:
            logout_user()
            if account.has_mobile():
                binded_account = account.mobile[
                    :4] + '*' * 4 + account.mobile[-4:]
            elif account.has_email():
                username, domain = account.email.split('@')
                binded_account = username[:3] + '*' * 4 + '@' + domain
            text = '您的账号已经与' + binded_account + '绑定，请先解绑'
        else:
            text = '您已经绑定过了，无需重新绑定'
    else:
        # bind the current openid
        current_app.logger.debug('bind current weixin alias')
        g.user.add_alias(openid, ACCOUNT_REG_TYPE.WEIXIN_OPENID)
        text = '绑定成功'

    return render_template('accounts/weixin_bind_result.html', **locals())
