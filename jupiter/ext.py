from flask import current_app
from flask_mako import MakoTemplates
from flask_oauthlib.client import OAuth
from flask_oauthlib.provider import OAuth2Provider
from flask_limiter import Limiter
from flask_seasurf import SeaSurf
from flask_weixinapi import WeixinAPI
from flask_yixin import Yixin
from flask_zslib import ZhongshanSecurities
from flask_zwlib import Zhiwang
from flask_xmlib import XinMi
from flask_sxblib import Sxb
from raven.contrib.flask import Sentry
from yxpay.ext.flask import YixinPay
from zslib.signals import debug_message_sent

from .compat.weixin_oauth import fixup_weixin_oauth


sentry = Sentry()
mako = MakoTemplates()
oauth = OAuth()
oauth_provider = OAuth2Provider()
limiter = Limiter()
seasurf = SeaSurf()
yixin = Yixin()
yxpay = YixinPay()
zslib = ZhongshanSecurities()
zhiwang = Zhiwang()
xinmi = XinMi()
sxb = Sxb()
weixin_api = WeixinAPI()

weixin = oauth.remote_app(
    'weixin',
    app_key='WEIXIN',
    request_token_params={'scope': 'snsapi_base'},
    base_url='https://api.weixin.qq.com',
    authorize_url='https://open.weixin.qq.com/connect/oauth2/authorize',
    access_token_url='https://api.weixin.qq.com/sns/oauth2/access_token',
    # important: ignore the 'text/plain' said by weixin api and enforce the
    #            response be parsed as json.
    content_type='application/json',
)
fixup_weixin_oauth(weixin)

seasurf.exempt_urls((
    '/api',
    '/oauth',
))


@debug_message_sent.connect
def zslib_send_message(sender, method, content, request_id):
    from .integration.bearychat import BearyChat

    bearychat = BearyChat('staging')

    if bearychat.configured and current_app.debug and method == 'sg.sms.send':
        bearychat.say(content)
