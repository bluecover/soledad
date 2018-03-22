from __future__ import absolute_import

from flask import current_app
from werkzeug.local import LocalProxy
from jpush_client import make_client


@LocalProxy
def jpush():
    """The context-bound instance of Jpush gateway client."""
    if 'jpush_client' not in current_app.extensions:
        current_app.extensions['jpush_client'] = make_client(
            current_app.config.get('JPUSHSRV_HOST', '127.0.0.1'),
            current_app.config.get('JPUSHSRV_PORT', 6000),
            current_app.config.get('JPUSHSRV_TIMEOUT', 60000))
    return current_app.extensions['jpush_client']
