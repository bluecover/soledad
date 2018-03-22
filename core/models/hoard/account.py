from libs.db.store import db
from libs.cache import mc, cache
from core.models.user.account import Account
from core.models.user.signals import before_freezing_user
from .errors import NotFoundError, RemoteAccountUsedError, HoarderReboundError


class YixinAccount(object):
    """The relationship between Yixin accounts and local accounts.

    :param account_id: the primary key of local account.
    :param p2p_account: the account identity which provided by the Yixin API.
    :param p2p_token: the secret token which provided by the Yixin API.
    """

    table_name = 'hoard_yixin_account'
    cache_by_local_key = 'hoard:yixin:account:account_id:%s'

    def __init__(self, account_id, p2p_account, p2p_token):
        self.account_id = str(account_id)
        self.p2p_account = p2p_account
        self.p2p_token = p2p_token

    @classmethod
    def check_before_binding(cls, account_id):
        from .order import HoardOrder  # TODO may use signals here
        if HoardOrder.get_id_list_by_user_id(account_id):
            raise HoarderReboundError

    @classmethod
    def bind(cls, account_id, p2p_account, p2p_token, commit=True):
        """Creates new binding relationship and cancels all existent."""
        cls.check_before_binding(account_id)

        params = (account_id, p2p_account, p2p_token)

        if not Account.get(account_id):
            raise NotFoundError(account_id, Account)

        existent = cls.get_by_local(account_id)

        if existent:
            cls.unbind(account_id, commit=False)

        if cls.get_by_remote(p2p_account) or cls.get_by_p2p_token(p2p_token):
            raise RemoteAccountUsedError(p2p_account)

        sql = ('insert into {.table_name} (account_id, p2p_account, p2p_token)'
               'values (%s, %s, %s)').format(cls)
        db.execute(sql, params)
        if commit:
            db.commit()

        cls.clear_cache(account_id)

        return cls.get_by_local(account_id)

    @classmethod
    def unbind(cls, account_id, commit=True):
        """Cancels all bound relationships of the specific local account."""
        sql = ('delete from {.table_name} where account_id = %s').format(cls)
        params = (account_id,)

        db.execute(sql, params)
        if commit:
            db.commit()

        cls.clear_cache(account_id)

    @classmethod
    @cache(cache_by_local_key % '{account_id}')
    def get_by_local(cls, account_id):
        """Gets the relationship by the id of local account."""
        sql = ('select account_id, p2p_account, p2p_token from {.table_name} '
               'where account_id = %s').format(cls)
        params = (account_id,)
        rs = db.execute(sql, params)
        if not rs:
            return
        return cls(*rs[0])

    @classmethod
    def get_by_remote(cls, p2p_account):
        sql = ('select account_id from {.table_name} '
               'where p2p_account = %s').format(cls)
        params = (p2p_account,)
        rs = db.execute(sql, params)
        if not rs:
            return
        return cls.get_by_local(rs[0][0])

    @classmethod
    def get_by_p2p_token(cls, p2p_token):
        sql = ('select account_id from {.table_name} '
               'where p2p_token = %s').format(cls)
        params = (p2p_token,)
        rs = db.execute(sql, params)
        if not rs:
            return
        return cls.get_by_local(rs[0][0])

    @classmethod
    def clear_cache(cls, account_id):
        mc.delete(cls.cache_by_local_key % account_id)


@before_freezing_user.connect
def check_yixin_account_existence(user):
    return bool(YixinAccount.get_by_local(user.id_))

check_yixin_account_existence.product_name = 'yixin'
