# coding: utf-8

from flask import current_app, request, redirect, g, abort
from flask_mako import render_template
from itsdangerous import URLSafeSerializer, BadSignature
from core.models.user.consts import ACCOUNT_REG_TYPE

from ._blueprint import create_blueprint


bp = create_blueprint('weixin', __name__)


@bp.route('/alias/weixin/<signed_openid>', methods=['GET', 'POST'])
def weixin(signed_openid):
    aliases = g.user.get_type_alias()
    is_bound = ACCOUNT_REG_TYPE.WEIXIN_OPENID in aliases

    # decrypt the openid (sender) which provided by weixin
    serializer = URLSafeSerializer(current_app.secret_key)
    try:
        openid = serializer.loads(signed_openid)
    except BadSignature:
        return u'bad signature', 403

    if request.method == 'GET':
        return render_template('mine/alias/weixin.html', is_bound=is_bound)

    # overrides method with a hidden field
    if request.method == 'POST':
        if request.form['method'] == 'post':
            # bind to current account
            g.user.add_alias(openid, ACCOUNT_REG_TYPE.WEIXIN_OPENID)
            return redirect('/mine/plan')

        if request.form['method'] == 'delete':
            g.user.remove_alias(ACCOUNT_REG_TYPE.WEIXIN_OPENID)
            return redirect(request.path)

        abort(400)
