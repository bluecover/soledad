from datetime import datetime
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.account import Account
from core.models.user.signals import before_freezing_user
from .errors import RemoteAccountOccupiedError, RepeatlyRegisterError
from ..errors import NotFoundError


class ZhiwangAccount(object):
    table_name = 'hoard_zhiwang_account'
    cache_by_local_key = 'hoard:zhiwang:account:{account_id}'

    def __init__(self, account_id, zhiwang_id, bind_time):
        self.account_id = str(account_id)
        self.zhiwang_id = zhiwang_id
        self.bind_time = bind_time

    @cached_property
    def local_account(self):
        return Account.get(self.account_id)

    @classmethod
    def bind(cls, account_id, zhiwang_id):
        if not Account.get(account_id):
            raise NotFoundError(account_id, Account)

        if cls.get_by_local(account_id):
            raise RepeatlyRegisterError(account_id)

        if cls.get_by_remote(zhiwang_id):
            raise RemoteAccountOccupiedError(zhiwang_id)

        sql = ('insert into {.table_name} (account_id, zhiwang_id, '
               'bind_time) values (%s, %s, %s)').format(cls)
        params = (account_id, zhiwang_id, datetime.now())
        db.execute(sql, params)
        db.commit()

        cls.clear_cache(account_id)

    @classmethod
    def unbind(cls, account_id):
        sql = ('delete from {.table_name} where account_id=%s').format(cls)
        params = (account_id,)

        db.execute(sql, params)
        db.commit()

        cls.clear_cache(account_id)

    @classmethod
    @cache(cache_by_local_key)
    def get_by_local(cls, account_id):
        sql = ('select account_id, zhiwang_id, bind_time from {.table_name} '
               'where account_id=%s').format(cls)
        params = (account_id,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_by_remote(cls, zhiwang_id):
        sql = ('select account_id from {.table_name} '
               'where zhiwang_id=%s').format(cls)
        params = (zhiwang_id,)
        rs = db.execute(sql, params)
        return cls.get_by_local(rs[0][0]) if rs else None

    @classmethod
    def clear_cache(cls, account_id):
        mc.delete(cls.cache_by_local_key.format(account_id=account_id))


@before_freezing_user.connect
def check_zw_account_existence(user):
    return bool(ZhiwangAccount.get_by_local(user.id_))

check_zw_account_existence.product_name = 'zhiwang'
