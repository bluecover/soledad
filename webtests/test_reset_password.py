# coding: utf-8

from __future__ import unicode_literals

from .framework import BaseTestCase


class TestResetPassword(BaseTestCase):

    def test_reset_password_for_email_account(self):
        # as email can't be used to register any more, we use the
        # auto-generated test1@guihua.com for test
        email, password = 'test2@guihua.com', 'testtest'
        # login and reset password
        self.login(user_alias=email, user_password=password)
        self.browser.visit(self.url_for('accounts.settings.settings'))

        assert self.browser.is_element_present_by_css(
            'a.js-modify-text', wait_time=3)

        self.browser.find_by_css('a.js-modify-text').first.click()

        new_pwd = 'testtest'
        self.browser.find_by_css('input[name="old-password"]').fill(password)
        self.browser.find_by_css('input[name="new-password"]').fill(new_pwd)
        self.browser.find_by_css('input[name="repwd-txt"]').fill(new_pwd)
        self.browser.find_by_css('a.js-confirm-password').first.click()
        self.browser.execute_script('$.onemodal.close()')

        self.login(user_alias=email, user_password=new_pwd)

    def test_reset_password_for_mobile_account(self):
        # register first
        mobile, password = self.register_mobile()

        # login and reset password
        self.logout()
        self.login(user_alias=mobile, user_password=password)

        self.browser.visit(self.url_for('accounts.settings.settings'))

        assert self.browser.is_element_present_by_css(
            'a.js-modify-text', wait_time=3)

        self.browser.find_by_css('a.js-modify-text').first.click()

        new_pwd = 'testtest'

        self.browser.find_by_css('input[name="old-password"]').fill(password)
        self.browser.find_by_css('input[name="new-password"]').fill(new_pwd)
        self.browser.find_by_css('input[name="repwd-txt"]').fill(new_pwd)
        self.browser.find_by_css('a.js-confirm-password').first.click()
        self.browser.execute_script('$.onemodal.close()')

        self.login(user_alias=mobile, user_password=new_pwd)
