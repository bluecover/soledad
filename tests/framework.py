# coding: utf-8

from __future__ import absolute_import

import os
import sys
from datetime import datetime
from unittest import TestCase

from mock import patch


TEST_DIR = os.path.dirname(os.path.realpath(__file__))

APP_DIR = os.path.dirname(TEST_DIR)

sys.path.insert(0, APP_DIR + '/stubs')
sys.path.insert(0, TEST_DIR + '/stubs')


def init_modules_from_config():
    from libs.db.store import db

    def is_testing():
        return True
    db.is_testing = is_testing
    return db

init = init_modules_from_config

CACHE_NAME = 'web-cache'
COUCH_NAME = 'couch-cache'
STATIC_NAME = 'static-cache'


class BaseTestCase(TestCase):

    def setUp(self):
        from libs.db.rdstore import rdstore
        from libs.db.couchdb import cdb
        self.db = init_modules_from_config()
        self.rds = [rdstore.get_redis(n) for n in [CACHE_NAME,
                                                   COUCH_NAME]]
        self.cdb = cdb
        self.fillup()

    def fillup(self):
        self.db.execute('truncate table location')
        locs = [('110000', '北京市', '100000'),
                ('110105', '朝阳区', '110000')]
        for (id, name_cn, parent_id) in locs:
            self.db.execute('insert into location '
                            '(id, name_cn, parent_id) '
                            'values (%s, %s, %s)',
                            (id, name_cn, parent_id))
            self.db.commit()
        self.db.execute('truncate table insurance')
        self.add_insurance()

    def tearDown(self):
        self.db.execute('truncate table account')
        self.db.execute('truncate table account_alias')
        self.db.execute('truncate table user_plan')
        self.db.execute('truncate table user_channel')
        self.db.execute('truncate table user_channel_register')
        self.db.execute('truncate table article')
        self.db.execute('truncate table location')
        self.db.execute('truncate table oauth_client')
        self.db.execute('truncate table oauth_grant')
        self.db.execute('truncate table oauth_token')
        self.db.execute('truncate table hoard_rebate')
        self.db.execute('truncate table hoard_yixin_account')
        self.db.execute('truncate table hoard_yixin_service')
        self.db.execute('truncate table hoard_profile')
        self.db.execute('truncate table hoard_order')
        self.db.execute('truncate table hoard_bankcard')  # profile_bankcard
        self.db.execute('truncate table profile_address')
        self.db.execute('truncate table profile_identity')
        self.db.execute('truncate table wallet_account')
        self.db.execute('truncate table wallet_profit')
        self.db.execute('truncate table wallet_transaction')
        self.db.execute('truncate table wallet_annual_rate')
        self.db.execute('truncate table wallet_bankcard_binding')
        self.db.execute('truncate table download_project')
        self.db.execute('truncate table download_release')
        self.db.execute('truncate table shorten_url')
        self.db.execute('truncate table insurance')
        self.db.execute('truncate table funcombo_group')
        self.db.execute('truncate table funcombo_group_fund')
        self.db.execute('truncate table funcombo_income')
        self.db.execute('truncate table funcombo_income_user')
        self.db.execute('truncate table funcombo_fund')
        self.db.execute('truncate table funcombo_data')
        self.db.execute('truncate table funcombo_userlike')
        self.db.execute('truncate table wxplan_plan')
        self.db.execute('truncate table wxplan_salary')
        self.db.execute('truncate table wxplan_report')
        self.db.execute('truncate table wxplan_wage_level')
        self.db.execute('truncate table security_twofactor')
        self.db.execute('truncate table site_announcement')
        self.db.execute('truncate table invitation')
        self.db.execute('truncate table coupon_package_investment_invitation_reward')
        self.db.execute('truncate table redeem_code')
        self.db.execute('truncate table redeem_code_usage')
        self.db.execute('truncate table coupon_package_redeem_code')
        self.db.execute('truncate table hoard_zhiwang_loans_digest')
        self.db.execute('truncate table hoard_zhiwang_loan')
        self.db.execute('truncate table hoard_placebo_product')
        self.db.execute('truncate table hoard_placebo_order')
        self.db.execute('truncate table insurance_plan')
        self.db.execute('truncate table hoarder_product')
        self.db.execute('truncate table hoarder_vendor')
        for r in self.rds:
            r.flushall()
        if hasattr(self.cdb.server, 'clear'):
            self.cdb.server.clear()

    def add_insurance(self):
        sql = ('insert into insurance '
               '( kind, insurance_id, name, status, rec_rank, '
               'create_time, update_time) '
               'values ( %s, %s, %s, %s, %s, %s, %s)')
        params = (0, 1, u'享人生-安联个人保障计划（幼儿版） 计划二', 1, 1,
                  datetime.now(), datetime.now())
        self.db.execute(sql, params)
        self.db.commit()

        sql = ('insert into insurance '
               '(kind, insurance_id, name, status, rec_rank, '
               'create_time, update_time) '
               'values ( %s, %s, %s, %s, %s, %s, %s)')
        params = (1, 8, u'泰康e顺少儿重大疾病保险', 1, 1,
                  datetime.now(), datetime.now())
        self.db.execute(sql, params)
        self.db.commit()

        sql = ('insert into insurance '
               '(kind, insurance_id, name, status, rec_rank, '
               'create_time, update_time) '
               'values ( %s, %s, %s, %s, %s, %s, %s)')
        params = (2, 10, u'阳光旅程教育金保障计划（分红型）', 1, 1,
                  datetime.now(), datetime.now())
        self.db.execute(sql, params)
        self.db.commit()

    def add_account(self, email=None, mobile=None,
                    password=None, name=None, status=0):
        from core.models.user.consts import ACCOUNT_REG_TYPE
        from core.models.user.account import Account
        from core.models.utils import pwd_hash
        from core.models.utils import randbytes

        if not email and not mobile:
            email = 'test@guihua.com'

        alias_type = ACCOUNT_REG_TYPE.MOBILE \
            if mobile else ACCOUNT_REG_TYPE.EMAIL

        alias = mobile or email
        password = password or 'test'
        salt = randbytes(4)
        passwd_hash = pwd_hash(salt, password)
        name = name or 'test'
        return Account.add(alias, passwd_hash, salt,
                           name, reg_type=alias_type, status=status)

    def add_identity(self, user_id, person_name, person_ricn):
        from core.models.profile.identity import Identity
        return Identity.save(user_id, person_name, person_ricn)

    def add_bankcard(self, user_id, bank_id='10005',
                     card_number='6222980000000002',
                     mobile_phone='13800138000', division_code='440300',
                     local_bank_name=u'深大支行', is_default=False):
        from core.models.profile.bankcard import BankCard

        with patch('core.models.profile.bankcard.DEBUG', True):
            province_code = division_code[:2] + '00'
            prefecture_code = division_code[:4] + '00'
            return BankCard.add(
                user_id, mobile_phone, card_number, bank_id, prefecture_code,
                province_code, local_bank_name, is_default)
