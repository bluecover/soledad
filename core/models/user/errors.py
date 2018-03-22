# coding:utf-8


class AccountError(Exception):
    """The base exception class for account issues."""


class FreezingPreventedError(AccountError):
    pass


class RemovingMobileAliasPreventedError(AccountError):
    pass
