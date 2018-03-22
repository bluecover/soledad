# coding: utf-8

from __future__ import print_function, absolute_import, unicode_literals

from base64 import urlsafe_b64encode, urlsafe_b64decode
from mimetypes import types_map
from io import BytesIO

from flask import Blueprint, current_app, send_file, url_for, jsonify, request
from qrcode import QRCode
from qrcode.image.svg import SvgPathImage
from qrcode.image.pil import PilImage
from itsdangerous import Signer


__all__ = ['make_qrcode_image']


bp = Blueprint('jqrcode', __name__, url_prefix='/j/qr')

types_map.setdefault('.svg', 'image/svg+xml')
image_kinds = {
    'svg': SvgPathImage,
    'png': PilImage,
}


@bp.route('/<url>/<signature>')
@bp.route('/<url>/<signature>.<suffix>')
def qrcode_image(url, signature, suffix=None):
    """The endpoint for generated QRCode image."""
    try:
        url = urlsafe_b64decode(url.encode('ascii'))
    except (ValueError, UnicodeEncodeError):
        return jsonify(r=False, error='invalid_data'), 404

    if suffix is None:
        # default suffix
        suffix = 'png' if request.user_agent.browser == 'msie' else 'svg'

    kind = image_kinds.get(suffix)
    if not kind:
        return jsonify(r=False, error='invalid_format'), 404

    signer = get_qrcode_signer()
    if not signer.verify_signature(url, signature):
        return jsonify(r=False, error='invalid_signature'), 404

    image = make_qrcode_image(url, border=0, box_size=20, image_factory=kind)
    response = make_image_response(image)
    return response


def get_qrcode_signer(app=None):
    """Creates a signer by the secret key of current app."""
    app = app or current_app
    if 'qrcode.signer' not in app.extensions:
        app.extensions['qrcode.signer'] = Signer(app.secret_key)
    return app.extensions['qrcode.signer']


def make_qrcode_image(data, **kwargs):
    """Creates a QRCode image from given data."""
    qrcode = QRCode(**kwargs)
    qrcode.add_data(data)
    return qrcode.make_image()


def make_image_response(image):
    """Creates a cacheable response from given image."""
    mimetype = types_map['.' + image.kind.lower()]
    io = BytesIO()
    image.save(io)
    io.seek(0)
    return send_file(io, mimetype=mimetype, conditional=True)


def make_qrcode_url(url):
    """Creates a signed URL which pointed to a QRCode image."""
    signer = get_qrcode_signer()
    signature = signer.get_signature(url)
    url = urlsafe_b64encode(url.strip().encode('utf-8'))
    return url_for('jqrcode.qrcode_image', url=url, signature=signature)
