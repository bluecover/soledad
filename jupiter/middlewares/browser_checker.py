# coding: utf-8

"""
    获得browser id
"""

from collections import namedtuple
from pkg_resources import parse_version

from ua_parser.user_agent_parser import ParseDevice, ParseOS
from flask import Blueprint, request

from jupiter.views.accounts.utils.session import (
    set_account_browser_cookie, _BROWSER_COOKIE)
from core.models.consts import Platform

bp = Blueprint('middlewares.browser_checker', __name__)


class AppInfo(namedtuple('AppInfo', ['version', 'platform', 'origin'])):
    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        return bool(self.version and self.platform and self.origin)

    @classmethod
    def none(cls):
        return cls(None, None, None)


@bp.before_app_request
def check_browser():
    if not request.endpoint or request.endpoint.startswith('api'):
        return

    browser_cookie = request.cookies.get(_BROWSER_COOKIE)
    # bid = browser_cookie
    # bck = request.cookies.get(_BROWSER_CSRF_KEY)
    if not browser_cookie:
        set_account_browser_cookie()
        # set_browser_ck(bid or request.bid)
        request.original_browser_id = ''
    else:
        # once bid available, bck should right
        request.browser_id = request.bid = browser_cookie
        request.original_browser_id = browser_cookie
        # if not check_bck(bid, bck):
        #     raise ChallengeFailError()
        # request.bck = bck


TABLET_DEVICE = ['iPad', 'Kindle', 'Nexus 7', 'SCH-I800']

OSS = ['Android', 'iOS', 'Windows Phone', 'BlackBerry OS']


@bp.before_app_request
def check_useragent():
    fragments = request.user_agent.string.split()
    agents = dict(fm.split('/', 1) for fm in fragments if '/' in fm)

    # checks agents and flags them
    request.user_agent.is_weixin_browser = ('MicroMessenger' in agents)
    request.user_agent.is_guihua_app = ('Guihua' in agents)
    request.user_agent.is_talicai_app = ('talicai' in agents)

    request.user_agent.is_ios = request.user_agent.platform in ('iphone', 'ipad')
    request.user_agent.is_android = request.user_agent.platform == 'android'

    if request.user_agent.is_guihua_app:
        if request.user_agent.is_ios:
            origin = Platform.ios
        elif request.user_agent.is_android:
            origin = Platform.android
        else:
            origin = Platform.unknown
    else:
        origin = Platform.web

    device = ParseDevice(request.user_agent.string).get('family')
    os = ParseOS(request.user_agent.string).get('family')
    request.user_agent.is_tablet = any(d in device for d in TABLET_DEVICE)
    request.user_agent.is_mobile = (
        not request.user_agent.is_tablet and any(o in os for o in OSS))

    # checks app
    app_version = agents.get('Guihua')
    if request.user_agent.platform and app_version is None:
        request.user_agent.app_info = AppInfo.none()
    else:
        if app_version:
            app_version = parse_version(app_version)
        request.user_agent.app_info = AppInfo(
            version=app_version, platform=request.user_agent.platform, origin=origin)
