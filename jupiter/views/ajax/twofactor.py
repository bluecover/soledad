# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from flask import g, abort, jsonify, url_for, request
from qrcode.image.svg import SvgPathImage
from cryptography.hazmat.primitives.twofactor.totp import InvalidToken

from core.models.security.twofactor import TwoFactor
from .blueprint import create_blueprint
from .qrcode import make_qrcode_image, make_image_response


bp = create_blueprint('twofactor', __name__, url_prefix='/j/twofactor')


@bp.before_request
def inititalize():
    if not g.user:
        abort(401, '请先登录再继续设置')
    g.twofactor = TwoFactor.get(g.user.id_)


@bp.route('/provision', methods=['POST'])
def provision():
    """申请两步认证."""
    if not g.user.mobile:
        abort(403, '开启两步认证需要先绑定手机号')
    if g.twofactor:
        g.twofactor.renew()
    else:
        g.twofactor = TwoFactor.add(g.user.id_)
    return jsonify(r=True, preview_url=url_for('.provision_preview'))


@bp.route('/provision', methods=['DELETE'])
def provision_disable():
    """停用两步认证."""
    if not g.twofactor or not g.twofactor.is_enabled:
        abort(403, '两步认证尚未开启')
    if g.twofactor.verify(request.form['password'].encode('utf-8')):
        g.twofactor.disable()
    else:
        abort(403, '验证码输入有误')
    return jsonify(r=not g.twofactor.is_enabled)


@bp.route('/provision/verify', methods=['POST'])
def provision_verify():
    """输入验证码启用两步认证."""
    if not g.twofactor:
        abort(403, '两步认证尚未开启, 请先开启两步认证')
    if g.twofactor.is_enabled:
        return jsonify(r=True)
    try:
        g.twofactor.enable(request.form['password'].encode('utf-8'))
    except InvalidToken:
        abort(403, '验证码输入有误')
    return jsonify(r=g.twofactor.is_enabled)


@bp.route('/provision/preview')
def provision_preview():
    """显示设备设置二维码."""
    if not g.twofactor or g.twofactor.is_enabled:
        abort(404)
    provisioning_uri = g.twofactor.get_provisioning_uri()
    image = make_qrcode_image(
        provisioning_uri, border=0, box_size=5, image_factory=SvgPathImage)
    response = make_image_response(image)
    return response
