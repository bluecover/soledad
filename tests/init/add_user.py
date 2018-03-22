# -*- coding: utf-8 -*-

"""
创建测试用账号

密码统一为：testtest。
"""


from libs.utils.log import bcolors
from core.models.plan.plan import Plan
from core.models.user.register import register_without_confirm
from core.models.user.consts import ACCOUNT_REG_TYPE


d = {'age': 30,
     'career': '6',
     'children': [{
         'age': '8',
         'biz_insure': None,
         'career': '5',
         'child_society_insure': '2'}],
     'city': '110101',
     'consumer_loans': '5001',
     'deposit_current': '10000',
     'deposit_fixed': '10001',
     'expend_month_ent': '1000',
     'expend_month_extra': '800',
     'expend_month_house': '700',
     'expend_month_shopping': '600',
     'expend_month_trans': '500',
     'expend_year_extra': '900',
     'funds_bond': '2002',
     'funds_hybrid': '2001',
     'funds_money': '2000',
     'funds_other': '2004',
     'funds_stock': '2003',
     'gender': 'male',
     'income_month_extra': '101',
     'income_month_salary': '20000',
     'income_year_bonus': '102',
     'income_year_extra': '103',
     'invest_bank': '3001',
     'invest_concern': '2',
     'invest_exp': '3',
     'invest_handle': '4',
     'invest_increase': '1',
     'invest_insure': None,
     'invest_metal': None,
     'invest_national_debt': '3003',
     'invest_other': None,
     'invest_p2p': '3004',
     'invest_stock': '3002',
     'mine_biz_insure': None,
     'mine_society_insure': '4',
     'phone': '18618193877',
     'province': '110000',
     'real_estate': None,
     'real_estate_loan': None,
     'real_estate_value': None,
     'spouse': '1',
     'spouse_age': '50',
     'spouse_biz_insure': None,
     'spouse_career': '2',
     'spouse_society_insure': '3',
     'target': [{'money': '10000', 'target': '2', 'year': '5'}]
     }


def add_user(name, alias, reg_type):
    passwd = 'testtest'
    return register_without_confirm(alias, passwd, reg_type)

if __name__ == '__main__':
    bcolors.run('Add users.')
    try:
        # add special account
        add_user('zw', 'zw@guihua.com', reg_type=ACCOUNT_REG_TYPE.EMAIL)

        for i in range(10):
            name = 'test%s' % i
            email = '%s@guihua.com' % name
            u = add_user(name, email, reg_type=ACCOUNT_REG_TYPE.EMAIL)
            if i < 5:
                p = Plan.add(u.id)
                p.data.secret_db.set(p.data.props_name, d)
                p.update_step(6)
                bcolors.run(
                    'email=%s, password=%s, plan=%s' %
                    (email, 'testtest', p.id), key='user')
            else:
                bcolors.run(
                    'email=%s, password=%s' %
                    (email, 'testtest'), key='user')

        for i in range(10):
            name = 'mobiletest%s' % i
            mobile = '159%s' % (repr(i) * 8)
            u = add_user(name, mobile, reg_type=ACCOUNT_REG_TYPE.MOBILE)
            if i < 5:
                p = Plan.add(u.id)
                p.data.secret_db.set(p.data.props_name, d)
                p.update_step(6)
                bcolors.run(
                    'mobile=%s, password=%s, plan=%s' %
                    (mobile, 'testtest', p.id), key='user')
            else:
                bcolors.run(
                    'mobile=%s, password=%s' %
                    (mobile, 'testtest'), key='user')

        bcolors.success('Init user done.')
    except Exception as e:
        bcolors.fail('Init user fail: %s.' % e)
