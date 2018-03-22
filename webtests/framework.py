# coding: utf-8

from __future__ import unicode_literals

import os
import sys
import json
import random
import time
import socket
import warnings
import datetime
from unittest import TestCase

import requests
import flask
from splinter import Browser
from selenium.webdriver.common.utils import free_port
from solar.utils.storify import storify
try:
    from envcfg.json.solar import WEBTEST_BEARYCHAT_URL, WEBTEST_QINIU_URL
except ImportError:
    WEBTEST_BEARYCHAT_URL = WEBTEST_QINIU_URL = None

from jupiter.app import create_app
from libs.db.store import db
from libs.fs.fs import QiniuFS, UploadError
from libs.captcha import digits_captcha
from core.models.user.account import Account
from core.models.user.consts import VERIFY_CODE_TYPE


WEBTEST_DIR = os.path.dirname(os.path.realpath(__file__))
SOLAR_DIR = os.path.dirname(WEBTEST_DIR)
STUBS_DIR = SOLAR_DIR + '/stubs'

sys.path.append(STUBS_DIR)
sys.path.append(SOLAR_DIR)


class BaseTestCase(TestCase):

    fs = QiniuFS('guihua-webtest', WEBTEST_QINIU_URL)

    def url_for(self, endpoint, **kwargs):
        app = create_app()
        with app.app_context():
            return flask.url_for(endpoint, **kwargs)

    def peep_session(self):
        app = create_app()
        with app.app_context():
            cookies = self.browser.cookies.all()
            return app.open_session(storify({'cookies': cookies}))

    @classmethod
    def get_debugger_port(cls):
        if not hasattr(cls, '_debugger_port'):
            cls._debugger_port = free_port()
            debugger_prompt = (
                '\nPhantomJS debugger is listening on 0.0.0.0:{port} and '
                '{host}:{port}'.format(
                    host=socket.gethostname(), port=cls._debugger_port))
            print(debugger_prompt)
        return cls._debugger_port

    def setUp(self):
        self.browser = Browser('phantomjs', service_args=[
            '--remote-debugger-autorun=true',
            '--remote-debugger-port=%d' % self.get_debugger_port(),
        ])
        self.browser.driver.set_window_size(1440, 900)

    def tearDown(self):
        _, e, _ = sys.exc_info()
        if e is not None:
            self.report_screenshot(e)

        if e is None:
            try:
                self.logout()
            except Exception as e:
                self.report_screenshot(e)
                raise
            finally:
                self.browser.quit()

    def report_screenshot(self, error):
        try:
            screenshot = self.browser.driver.get_screenshot_as_png()
            screenshot_tag = datetime.datetime.utcnow().isoformat()
            screenshot_key = screenshot_tag + '.png'

            # upload screenshot
            if WEBTEST_QINIU_URL:
                try:
                    self.fs.upload(screenshot, 'image/png', screenshot_key)
                except UploadError as e:
                    warnings.warn('Failed to upload screenshot: %s' % e)
                url = self.fs.get_url(
                    screenshot_key, is_private=True,
                    expires=datetime.timedelta(days=30))
                warnings.warn('Screenshot: %s' % url)
            else:
                if not os.path.isdir('screenshots'):
                    os.mkdir('screenshots')
                screenshot_key = os.path.join('screenshots/', screenshot_key)
                with open(screenshot_key, 'wb') as f:
                    f.write(screenshot)
                warnings.warn(
                    'Screenshot has been saved as: %s' % screenshot_key)
                return

            # notify screenshot
            if WEBTEST_BEARYCHAT_URL:
                title = u'%s %s' % (error.__class__.__name__, screenshot_tag)
                payload = {
                    'text': u'Errors occurred in webtest.',
                    'attachments': [
                        {'title': title,
                         'text': unicode(error),
                         'color': u'#ffa500',
                         'images': [{'url': url}]},
                    ]
                }
                response = requests.post(
                    WEBTEST_BEARYCHAT_URL,
                    data={'payload': json.dumps(payload)})
                if not response.ok:
                    warnings.warn('Failed to notify screenshot: %s %s' % (
                        response.status_code, response.text))
        except Exception as e:
            warnings.warn('Failed to take screenshot caused by %r' % e)

    def login(self, user_alias='15988888888', user_password='testtest'):
        login_url = self.url_for('accounts.login.login')
        mine_url = self.url_for('mine.mine.mine')

        self.browser.visit(login_url)
        self.browser.fill('alias', user_alias)
        self.browser.fill('password', user_password)
        self.browser.find_by_css('.btn-login-submit').click()

        self.browser.is_element_present_by_css('.center-products')
        final_url = self.browser.url
        assert final_url == mine_url

    def register_mobile(self, user_mobile=None, user_password=None,
                        user_nickname=None):
        self.browser.visit(self.url_for('accounts.login.login'))
        self.browser.find_by_css('.js-to-register').click()
        assert self.browser.is_element_visible_by_css('.btn-register-submit')

        mobile = user_mobile or '159%08d' % random.randint(1, 99999999)
        password = user_password or 'haoguihua123'

        assert self.browser.is_element_visible_by_css('.captcha-img')
        session = self.peep_session()
        captcha_code = digits_captcha.get(session['cap_secret'])

        self.browser.fill('mobile', mobile)
        self.browser.fill('captcha', captcha_code)
        self.browser.find_by_css('.captcha.btn').click()

        time.sleep(1)
        button_text = self.browser.find_by_css('.captcha.btn').text
        assert button_text.endswith(u'后重新发送')

        # 获取手机注册验证码
        user = Account.get_by_alias(mobile)
        result = db.execute('select verify_code from user_verify '
                            'where user_id=%s and code_type=%s',
                            (user.id_, VERIFY_CODE_TYPE.REG_MOBILE))

        self.browser.fill('verify_code', str(result[0][0]))
        self.browser.find_by_css('#reg-password').fill(password)
        self.browser.find_by_css('.btn-register-submit').click()

        return mobile, password

    def logout(self):
        logout_url = self.url_for('accounts.login.logout')
        login_url = self.url_for('accounts.login.login')

        self.browser.visit(logout_url)

        self.browser.is_element_present_by_css('.btn-login-submit')
        final_url = self.browser.url
        assert final_url == login_url
