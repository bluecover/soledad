# -*- coding: utf-8 -*-
from pytest import raises
from .framework import BaseTestCase

from core.models.errors import BindError
from core.models.user.consts import ACCOUNT_REG_TYPE, ACCOUNT_STATUS
from core.models.user.bind import confirm_bind_without_check
from core.models.user.account import Account
from core.models.user.alias import (
    AliasTypeUsedError, AliasOccupiedError, InvalidAliasType)
from core.models.utils import pwd_hash
from core.models.utils import randbytes


class AccountTest(BaseTestCase):

    def test_add_account(self):
        email = 'test@guihua.com'
        password = 'test'
        salt = randbytes(4)
        passwd_hash = pwd_hash(salt, password)
        name = 'test'
        account = Account.add(email, passwd_hash, salt,
                              name, reg_type=ACCOUNT_REG_TYPE.EMAIL)
        self.assertTrue(account)
        self.assertEqual(account.name, name)
        self.assertTrue(account.has_email())
        self.assertEqual(account.email, email)
        self.assertTrue(ACCOUNT_REG_TYPE.EMAIL in account.reg_type)

    def test_get_account(self):
        account = self.add_account()
        account_id = account.id
        old_account = account
        account = Account.get(account_id)
        self.assertTrue(account)
        self.assertTrue(account.has_email())
        self.assertEqual(account.id, old_account.id)
        self.assertEqual(account.email, old_account.email)

    def test_get_account_by_alias(self):
        email = 'hello@guihua.com'
        account = self.add_account(email=email)
        self.assertEqual(account.email, email)
        old_account = account
        account = Account.get_by_alias(email)
        self.assertEqual(account.id, old_account.id)
        self.assertEqual(account.email, email)

        mobile = '13212345678'
        email_account = Account.get_by_alias(email)
        account.add_alias(mobile)
        mobile_account = Account.get_by_alias(mobile)

        self.assertEqual(account.id, mobile_account.id)
        self.assertEqual(account.id, email_account.id)
        self.assertEqual(mobile_account.email, email)
        self.assertEqual(email_account.mobile, mobile)

    def test_add_account_alias(self):
        email = 'test@guihua.com'
        mobile = '13211111111'
        mobile2 = '13211111112'
        weixin_openid = 'WX-12nfkl1h3nslk23n'
        account = self.add_account(email=email)
        result1 = account.add_alias(mobile)
        result1 = account.add_alias(
            weixin_openid, ACCOUNT_REG_TYPE.WEIXIN_OPENID)
        self.assertTrue(result1)
        self.assertEqual(account.email, email)
        self.assertEqual(account.mobile, mobile)
        self.assertEqual(account.weixin_openid, weixin_openid)
        assert account.has_mobile()
        assert account.has_email()
        assert account.has_weixin_openid()
        assert ACCOUNT_REG_TYPE.EMAIL in account.reg_type
        assert ACCOUNT_REG_TYPE.MOBILE in account.reg_type
        assert ACCOUNT_REG_TYPE.WEIXIN_OPENID in account.reg_type

        with raises(AliasOccupiedError):
            account2 = self.add_account(email='interfere@you.com')
            account2.add_alias(mobile)

        assert account.add_alias(mobile)

        with raises(AliasTypeUsedError):
            account.add_alias(mobile2)

        with raises(InvalidAliasType):
            account.add_alias('123')

        with raises(InvalidAliasType):
            account.add_alias('test')

        with raises(AliasTypeUsedError):
            account.add_alias('bazinga@guihua.com')

        with raises(InvalidAliasType):
            account.add_alias('bazinga@guihua.com', ACCOUNT_REG_TYPE.MOBILE)

    def test_bind_mobile_alias(self):
        # 1. 手机用户尝试绑定
        mobile = '13200000000'
        account = self.add_account(mobile=mobile, status=ACCOUNT_STATUS.NORMAL)
        with raises(BindError):
            confirm_bind_without_check(account.id, '13211111111')

        # 2. 邮箱用户绑定一个从未尝试过任何注册的手机号
        email = 'test1@guihua.com'
        mobile = '13222222222'
        account = self.add_account(email=email, status=ACCOUNT_STATUS.NORMAL)
        confirm_bind_without_check(account.id, mobile)
        self.assertEqual(account.email, email)
        self.assertEqual(account.mobile, mobile)

        # 3. 邮箱用户绑定一个之前注册但未通过验证的手机号
        mobile = '13233333333'
        account = self.add_account(mobile=mobile)
        account_id = account.id

        email = 'test2@guihua.com'
        account = self.add_account(email=email)
        confirm_bind_without_check(account.id, mobile)

        failed_account = Account.get(account_id)
        self.assertTrue(failed_account.is_failed_account())
        self.assertEqual(len(failed_account.reg_alias), 0)
        self.assertEqual(account.email, email)
        self.assertEqual(account.mobile, mobile)

    def test_remove_account_alias(self):
        email = 'test@guihua.com'
        mobile = '13211111111'
        account = self.add_account(email=email)
        account.add_alias(mobile)

        # remove an alias whose type is not in reg type
        result1 = account.remove_alias(ACCOUNT_REG_TYPE.WEIXIN_OPENID)

        # remove an alias that alias doesn't match the type
        result2 = account.remove_alias(
            ACCOUNT_REG_TYPE.MOBILE, 'test@guihua.com')

        # remove an alias that is not in reg alias
        result3 = account.remove_alias(
            ACCOUNT_REG_TYPE.MOBILE, '13222222222')

        # remove an removable alias
        result4 = account.remove_alias(ACCOUNT_REG_TYPE.EMAIL)

        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
        self.assertTrue(result4)
        email_account = Account.get_by_alias(email)
        assert email_account is None

        # remove the last alias
        result5 = account.remove_alias(ACCOUNT_REG_TYPE.MOBILE)
        self.assertFalse(result5)
        account = Account.get_by_alias(mobile)
        assert account is not None

        # remove mobile when email has been deleted
        account.add_alias(
            'WX-12nfkl1h3nslk23n', ACCOUNT_REG_TYPE.WEIXIN_OPENID)
        result6 = account.remove_alias(ACCOUNT_REG_TYPE.MOBILE)
        self.assertFalse(result6)
        account = Account.get_by_alias(mobile)
        assert account is not None

    def test_validate_password(self):
        password = '123456'
        account = self.add_account(password=password)
        account = Account.get_by_alias(account.email)
        r = account.verify_password(password)
        self.assertTrue(r)

    def test_unbind_mobile(self):
        mobile = '13211111111'
        account = self.add_account(mobile=mobile, status=ACCOUNT_STATUS.NORMAL)
        account.unbind_mobile()
        assert account.mobile is None

    def test_gets(self):

        accounts = Account.gets([])
        assert len(accounts) == 0

        email1 = 'test1@guihua.com'
        password1 = 'test'
        salt1 = randbytes(4)
        passwd_hash1 = pwd_hash(salt1, password1)
        name1 = 'test'
        account1 = Account.add(email1, passwd_hash1, salt1,
                               name1, reg_type=ACCOUNT_REG_TYPE.EMAIL)

        email2 = 'test2@guihua.com'
        password2 = 'test'
        salt2 = randbytes(4)
        passwd_hash2 = pwd_hash(salt2, password2)
        name2 = 'test'
        account2 = Account.add(email2, passwd_hash2, salt2,
                               name2, reg_type=ACCOUNT_REG_TYPE.EMAIL)

        email3 = 'test3@guihua.com'
        password3 = 'test'
        salt3 = randbytes(4)
        passwd_hash3 = pwd_hash(salt3, password3)
        name3 = 'test'
        account3 = Account.add(email3, passwd_hash3, salt3,
                               name3, reg_type=ACCOUNT_REG_TYPE.EMAIL)

        email4 = 'test4@guihua.com'
        password4 = 'test'
        salt4 = randbytes(4)
        passwd_hash4 = pwd_hash(salt4, password4)
        name4 = 'test'
        account4 = Account.add(email4, passwd_hash4, salt4,
                               name4, reg_type=ACCOUNT_REG_TYPE.EMAIL)

        ids = [account1.id, account2.id, account3.id, account4.id]
        accounts = Account.gets(ids)

        assert len(accounts) == 4

        assert account1 in accounts
        assert account2 in accounts
        assert account3 in accounts
        assert account4 in accounts
