# coding: utf-8

import json

from flask import url_for

from libs.utils.log import bcolors
from core.models.oauth import OAuthClient, OAuthScope
from jupiter.app import create_app
from jupiter.integration.bearychat import BearyChat


bearychat = BearyChat('staging')
TEMPLATE = u'''\
@group 测试环境已更新
**Client ID** `{}`
**Client Secret** `{}`'''


def get_redirect_uri():
    try:
        from envcfg.json.solar import OAUTHY_REDIRECT_URI
    except ImportError:
        return 'http://oauthy.guihua.dev/login/guihua/authorized'
    else:
        return OAUTHY_REDIRECT_URI


def main():
    bcolors.run('Add OAuth client.')
    client = OAuthClient.add(
        name=u'OAuthy',
        redirect_uri=get_redirect_uri(),
        allowed_grant_types=['authorization_code', 'password', 'refresh_token'],
        allowed_response_types=['token', 'code'],
        allowed_scopes=[OAuthScope.user_info, OAuthScope.savings_r,
                        OAuthScope.savings_w, OAuthScope.wallet_r,
                        OAuthScope.wallet_w])
    client_args = (client.name, client.client_id, client.client_secret)
    bcolors.run('%s: %s %s ' % client_args, key='oauth')

    bcolors.run('Add OAuth authorization.')
    app = create_app()
    with app.app_context(), app.test_client() as http:
        r = http.post(url_for('api.oauth.access_token'), data={
            'grant_type': 'password',
            'client_id': client.client_id,
            'client_secret': client.client_secret,
            'username': 'test0@guihua.com',
            'password': 'testtest',
            'scope': 'basic user_info savings_r savings_w wallet_r wallet_w',
        })

        if not bearychat.configured:
            return
        bearychat.say(TEMPLATE.format(client.client_id, client.client_secret))

    data = json.loads(r.data)
    bcolors.run(' '.join('%s=%s' % pair for pair in data.items()), key='oauth')


if __name__ == '__main__':
    main()
