# coding: utf-8

from __future__ import unicode_literals

import time

from selenium.common.exceptions import (
    ElementNotVisibleException,
    StaleElementReferenceException,
)

from .framework import BaseTestCase


class TestPlan(BaseTestCase):

    def _submit(self):
        self.browser.find_by_css('a.js-submit-form').first.click()

    def _fill_step_1(self, with_members=False):
        self.with_members = with_members
        assert self.browser.is_element_present_by_css('a.js-submit-form')

        self.browser.fill('age', '30')
        self.browser.select('career', '6')
        self.browser.fill('phone', '18618193877')
        self.browser.select('mine_society_insure', '2')

        if self.with_members:
            try:
                self.browser.find_by_css('.js-add-spouse').click()
                time.sleep(1)
                self.browser.fill('spouse_age', '31')
                self.browser.select('spouse_career', '5')
            except ElementNotVisibleException:
                pass
        else:
            try:
                self.browser.find_by_css('.js-del-spouse').click()
            except ElementNotVisibleException:
                pass

        self._submit()

    def _fill_step_2(self):
        assert self.browser.is_element_present_by_css(
            'a.js-submit-form', wait_time=3)

        if self.with_members:
            assert self.browser.is_text_present('您的家庭')
        else:
            assert self.browser.is_text_present('您的个人')

        _forms = dict(
            income_month_salary=20000,
            income_month_extra=101,
            income_year_bonus=102,
            income_year_extra=103,
            expend_month_ent=1000,
            expend_month_trans=500,
            expend_month_shopping=600,
            expend_month_house=700,
            expend_month_extra=800,
            expend_year_extra=900,
        )
        for k, v in _forms.items():
            self.browser.find_by_name(k).first.fill('')
            self.browser.find_by_name(k).first.fill(v)

        self._submit()

    def _fill_step_3(self):
        assert self.browser.is_element_present_by_css(
            'a.js-submit-form', wait_time=3)

        for i in self.browser.find_by_css('a.option-item'):
            try:
                if not i.has_class('on'):
                    i.click()
            except StaleElementReferenceException:
                pass

        _forms = dict(
            deposit_current=10000,
            deposit_fixed=10001,
            funds_money=2000,
            funds_hybrid=2001,
            funds_bond=2002,
            funds_stock=2003,
            funds_other=2004,
            invest_bank=3001,
            invest_stock=3002,
            invest_national_debt=3003,
            invest_p2p=3004,
            consumer_loans=5001,
        )

        for k, v in _forms.items():
            r = self.browser.find_by_name(k)
            if r:
                r.first.fill(v)

        self._submit()

    def _fill_step_4(self):
        assert self.browser.is_element_present_by_css(
            '.js-target-type', wait_time=3)

        self.browser.execute_script('''
            $(".js-target-type").val("4");
            $(".js-target-money").val(10000);
            $(".js-target-year").val(5);
            ''')

        self.browser.find_by_css('label[for="exp1"]').first.click()
        self.browser.find_by_css('label[for="concern2"]').first.click()
        self.browser.find_by_css('label[for="increase2"]').first.click()
        self.browser.find_by_css('label[for="handle2"]').first.click()

        self._submit()

    def test_plan(self):
        plan_url = self.url_for('mine.info.mine_info_1')

        self.login()
        self.browser.visit(plan_url)
        assert self.browser.url == plan_url

        self._fill_step_1()
        self._fill_step_2()
        self._fill_step_3()
        self._fill_step_4()

    def test_plan_with_members(self):
        plan_url = self.url_for('mine.info.mine_info_1')

        self.login()
        self.browser.visit(plan_url)
        assert self.browser.url == plan_url

        self._fill_step_1(with_members=True)
        self._fill_step_2()
        self._fill_step_3()
        self._fill_step_4()
