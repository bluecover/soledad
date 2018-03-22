# coding: utf-8

from __future__ import unicode_literals

import time

from libs.db.store import db
from core.models.user.account import Account
from core.models.user.consts import VERIFY_CODE_TYPE

from .framework import BaseTestCase


class TestForgotPassword(BaseTestCase):

    def _submit(self):
        self.browser.find_by_css('.send-btn').click()

    def test_forgot_password_for_email_account(self):
        # as email can't be used to register any more, we use the
        # auto - generated test1@guihua.com for test
        email = 'test1@guihua.com'
        browser = self.browser
        browser.visit(self.url_for('accounts.password.forgot'))
        browser.find_by_css('input[name="alias"]').fill(email)
        self._submit()

        assert browser.is_element_present_by_css('a.js-btn-resend-forgot')

        # 获取邮箱更改密码的url地址
        user = Account.get_by_alias(email)
        result = db.execute('select verify_code from user_verify '
                            'where user_id=%s and code_type=%s',
                            (user.id, VERIFY_CODE_TYPE.FORGOT_PASSWORD_EMAIL))
        browser.visit(self.url_for(
            'accounts.password.reset_for_mail_user', user_id=user.id_,
            code=str(result[0][0]), _external=True))

        assert browser.is_element_present_by_css('a.confirm-password-submit')

        browser.find_by_css('input[name="new-password"]').fill('testtest')
        browser.find_by_css('input[name="confirmed-password"]').fill('testtest')
        browser.find_by_css('a.confirm-password-submit').click()

        assert browser.is_element_present_by_css('.verification-box')
        assert browser.is_text_present('密码修改成功')

    def test_forgot_password_for_mobile_account(self):
        # register first
        mobile, password = self.register_mobile()

        # logout then
        self.logout()

        # get verify code for 1th try
        browser = self.browser
        browser.visit(self.url_for('accounts.password.forgot'))
        browser.find_by_css('input[name="alias"]').fill(mobile)
        self._submit()

        assert browser.is_element_present_by_css('a.js-btn-getcode')

        browser.find_by_css('a.js-btn-getcode').click()

        time.sleep(1)

        # 获取手机验证码
        user = Account.get_by_alias(mobile)
        result = db.execute('select verify_code from user_verify '
                            'where user_id=%s and code_type=%s',
                            (user.id, VERIFY_CODE_TYPE.FORGOT_PASSWORD_MOBILE))

        browser.find_by_css('input[name="code"]').fill(str(result[0][0]))
        browser.find_by_css('input[name="new-password"]').fill('testtest1234')
        browser.find_by_css('input[name="password"]').fill('testtest1234')

        browser.find_by_css('a.confirm-password-submit').click()

        assert browser.is_element_present_by_css('.verification-box')

        assert browser.is_text_present('密码修改成功')
