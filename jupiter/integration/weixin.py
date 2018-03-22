"""
    Weixin JavaScript SDK Support
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


import json

from flask import request
from jupiter.ext import weixin_api
from libs.cache import mc


__all__ = ['get_ticket', 'get_weixin_config']


CACHE_TICKET_KEY = 'weixin_api:ticket:v1'
CACHE_ACCESS_TOKEN_KEY = 'weixin_api:access_token:v1'


def get_ticket():
    ticket = mc.get(CACHE_TICKET_KEY)
    if ticket:
        return ticket

    response = weixin_api.get_js_ticket()
    if response['errcode'] != 0:
        raise RuntimeError('weixin error: %r' % response)
    ticket = response['ticket']
    expires_in = response['expires_in']

    mc.set(CACHE_TICKET_KEY, ticket, )
    mc.expire(CACHE_TICKET_KEY, expires_in)
    return ticket


@weixin_api.tokengetter
def get_access_token(app_id, app_secret):
    return mc.get(CACHE_ACCESS_TOKEN_KEY)


@weixin_api.tokensetter
def tokensetter(app_id, app_secret, access_token, expires_in):
    mc.set(CACHE_ACCESS_TOKEN_KEY, access_token)
    mc.expire(CACHE_ACCESS_TOKEN_KEY, expires_in)


def get_weixin_config(url=None, **kwargs):
    url = url or request.url
    config = weixin_api.make_sdk_config(url, ticket=get_ticket(), **kwargs)
    return json.dumps(config)
