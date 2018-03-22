# coding: utf-8

from blinker import Namespace

from core.models.user.utils import get_passwd_hash
from core.models.user.account import Account


_namespace = Namespace()
password_changed = _namespace.signal('password_changed')


def change_password(user_id, password):
    salt, passwd_hash = get_passwd_hash(password)
    account = Account.get(user_id)
    if account:
        account.change_passwd_hash(salt, passwd_hash)
        password_changed.send(account)
        return True
    return False
