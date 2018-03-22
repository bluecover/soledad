import logging
import os
import pkg_resources

from flask import Flask
from werkzeug.utils import import_string
from raven import fetch_git_sha, fetch_package_version
from raven.exceptions import InvalidGitRepository

from libs.logger.rsyslog import rsyslog_handler
from jupiter.ext import sentry


blueprints = [
    'jupiter.views.home:bp',
    'jupiter.views.article:bp',
    'jupiter.views.link:bp',
    'jupiter.views.about:bp',
    'jupiter.views.help:bp',
    'jupiter.views.accounts.settings:bp',
    'jupiter.views.accounts.password:bp',
    'jupiter.views.accounts.login:bp',
    'jupiter.views.accounts.register:bp',
    'jupiter.views.mine.mine:bp',
    'jupiter.views.mine.info:bp',

    # welfare
    'jupiter.views.welfare.welfare:bp',
    'jupiter.views.welfare.compat:bp',

    # fund
    'jupiter.views.fund:bp',

    # plan
    'jupiter.views.mine.plan:bp',

    # wxplan
    'jupiter.views.wxplan.wxplan:bp',

    # insurance
    'jupiter.views.ins.children:bp',
    'jupiter.views.ins.products:bp',
    'jupiter.views.ins.landing:bp',
    'jupiter.views.ins.plan:bp',

    # product
    'jupiter.views.mine.product:bp',
    'jupiter.views.mine.weixin:bp',

    # ajax
    'jupiter.views.ajax.j:bp',
    'jupiter.views.ajax.bankcard:bp',
    'jupiter.views.ajax.wxplan:bp',
    'jupiter.views.ajax.qrcode:bp',
    'jupiter.views.ajax.auth:bp',
    'jupiter.views.ajax.account:bp',
    'jupiter.views.ajax.twofactor:bp',
    'jupiter.views.ajax.address:bp',
    'jupiter.views.ajax.savings:bp',
    'jupiter.views.ajax.zhiwang:bp',
    'jupiter.views.ajax.xinmi:bp',
    'jupiter.views.ajax.division:bp',
    'jupiter.views.ajax.fund:bp',
    'jupiter.views.ajax.wallet:bp',
    'jupiter.views.ajax.promotion:bp',
    'jupiter.views.ajax.notification:bp',
    'jupiter.views.ajax.activity:bp',

    # hook
    'jupiter.views.hook.xm_notify:bp',

    # shorten url
    'jupiter.views.a:bp',

    # download
    'jupiter.views.download:bp',

    # captcha
    'jupiter.views.captcha:bp',

    # middlewares
    'jupiter.views.errorhandlers:bp',
    'jupiter.middlewares.site:bp',
    'jupiter.middlewares.authenticate_user:bp',
    'jupiter.middlewares.profile:bp',
    'jupiter.middlewares.browser_checker:bp',
    'jupiter.middlewares.cookies:bp',
    'jupiter.middlewares.csp:bp',
    'jupiter.middlewares.channel:bp',

    # profile
    'jupiter.views.profile.auth:bp',

    # savings
    'jupiter.views.savings.auth:bp',
    'jupiter.views.savings.landing:bp',
    'jupiter.views.savings.mine:bp',
    'jupiter.views.savings.record:bp',
    'jupiter.views.savings.zhiwang:bp',
    'jupiter.views.savings.xinmi:bp',
    'jupiter.views.savings.hook:bp',

    # redeemcode
    'jupiter.views.ajax.redeemcode:bp',

    # services
    'jupiter.views.services.sms:bp',

    # notification
    'jupiter.views.notification:bp',

    # wallet
    'jupiter.views.wallet.landing:bp',
    'jupiter.views.wallet.mine:bp',
    'jupiter.views.wallet.transaction:bp',

    # invitation
    'jupiter.views.invitation:bp',

    # oauth and api
    'jupiter.views.api.oauth:bp',
    'jupiter.views.api.v1.accounts:bp',
    'jupiter.views.api.v1.savings:bp',
    'jupiter.views.api.v1.products.yixin:bp',
    'jupiter.views.api.v1.products.zhiwang:bp',
    'jupiter.views.api.v1.products.xinmi:bp',
    'jupiter.views.api.v1.products.sxb:bp',
    'jupiter.views.api.v1.profile:bp',
    'jupiter.views.api.v1.coupons:bp',
    'jupiter.views.api.v1.data:bp',
    'jupiter.views.api.v1.pusher:bp',
    'jupiter.views.api.v1.wallet:bp',
    'jupiter.views.api.v1.welfare:bp',
    'jupiter.views.api.v1.redeemcode:bp',
    'jupiter.views.api.v1.advert:bp',

    # api v2
    'jupiter.views.api.v2.homepage:bp',
    'jupiter.views.api.v2.product:bp',
    'jupiter.views.api.v2.asset:bp',
    'jupiter.views.api.v2.mine:bp',
    'jupiter.views.api.v2.savings:bp',

    # activity
    'jupiter.views.activity.four_million:bp',
    'jupiter.views.activity.cake:bp',
    'jupiter.views.activity.beauty38:bp',
    'jupiter.views.activity.lottery:bp',
    'jupiter.views.activity.promotion:bp',

    # mobile app
    'jupiter.views.app.landing:bp',

    'jupiter.views.hybrid.zhiwang:bp',
    'jupiter.views.hybrid.rules:bp',
    'jupiter.views.hybrid.invitation:bp',
    'jupiter.views.hybrid.notification:bp'
]

extensions = [
    'jupiter.ext:sentry',
    'jupiter.ext:mako',
    'jupiter.ext:oauth',
    'jupiter.ext:oauth_provider',
    'jupiter.ext:limiter',
    'jupiter.ext:seasurf',
    'jupiter.ext:yixin',
    'jupiter.ext:yxpay',
    'jupiter.ext:zslib',
    'jupiter.ext:zhiwang',
    'jupiter.ext:xinmi',
    'jupiter.ext:sxb',
    'jupiter.ext:weixin_api',
]

collected_loggers = [
    ('yxlib.client', logging.INFO),
    ('yxpay.client', logging.INFO),
    ('zhiwang.client', logging.INFO),
    ('zslib.client', logging.INFO),
    ('zwlib.client', logging.INFO),
    ('xmlib.client', logging.INFO),
    ('sxblib.client', logging.INFO),
]


def create_app(config=None):
    """Creates application instance."""

    app = Flask(__name__)

    app.config.from_pyfile('app.cfg')
    app.config.from_object('envcfg.json.solar')
    app.config.from_object(config)

    # duplicate weixin consumer key
    app.config['WEIXIN_APP_ID'] = app.config.get('WEIXIN_CONSUMER_KEY')
    app.config['WEIXIN_APP_SECRET'] = app.config.get('WEIXIN_CONSUMER_SECRET')
    app.config['RATELIMIT_STORAGE_URL'] = app.config.get('REDIS_DSN')

    for extension_qualname in extensions:
        extension = import_string(extension_qualname)
        extension.init_app(app)

    for blueprint_qualname in blueprints:
        blueprint = import_string(blueprint_qualname)
        app.register_blueprint(blueprint)

    for logger_name, logger_level in collected_loggers:
        logger = logging.getLogger(logger_name)
        logger.addHandler(rsyslog_handler)
        logger.setLevel(logger_level)

    sentry.client.release = get_current_release(app)

    if app.testing:
        blueprint = import_string('jupiter.views.webtest.webtest:bp')
        app.register_blueprint(blueprint)

    return app


def get_current_release(app):
    try:
        current_release = fetch_package_version('solar')
    except pkg_resources.DistributionNotFound:
        pass
    else:
        return current_release

    try:
        current_release = fetch_git_sha(os.path.dirname(app.instance_path))
    except InvalidGitRepository:
        pass
    else:
        return current_release
