from __future__ import print_function, absolute_import, unicode_literals

import datetime
import decimal
import uuid

from jupiter.workers.wallet import wallet_profit_syncronizer
from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from .account import WalletAccount


class WalletProfit(EntityModel):
    """The daily profit record."""

    table_name = 'wallet_profit'
    cache_key = 'wallet:profit:{id_}'
    cache_key_for_total = 'wallet:profit:account:{account_id}:total_amount'
    cache_key_by_account = 'wallet:profit:account:{account_id}:ids'

    def __init__(self, id_, account_id, amount, date, updated_time):
        self.id_ = str(id_)
        self.account_id = str(account_id)
        self.amount = amount
        self.date = date
        self.updated_time = updated_time

    @classmethod
    def record(cls, account, amount, date):
        """Creates or updates a profit record.

        :param account: The wallet account.
        :type account: :class:`.account.WalletAccount`
        :param amount: The profit amount.
        :type amount: :class:`decimal.Decimal`
        :param date: The profit date.
        :type date: :class:`datetime.date`
        :return: An instance of :class:`WalletProfit`
        """
        assert isinstance(account, WalletAccount)
        assert isinstance(amount, decimal.Decimal)

        # Some MySQL issues (Bug #11765650, Bug #58637) drive us to use this
        # implementation. See also ``core.models.wallet.annual_rate``.

        ids = cls.get_ids_by_date(account.id_, date)
        id_ = ids[0] if ids else None
        if id_:
            sql = ('update {0} set profit_amount = %s '
                   'where id = %s').format(cls.table_name)
            params = (amount, id_)
            db.execute(sql, params)
        else:
            sql = ('insert into {0} (account_id, profit_amount, profit_date) '
                   'values (%s, %s, %s)').format(cls.table_name)
            params = (account.id_, amount, date)
            id_ = db.execute(sql, params)

        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_for_total(account.id_)
        cls.clear_cache_by_account(account.id_)

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        """Gets an profit record.

        :param id_: The id of profit record.
        :return: An instance of :class:`WalletProfit`
        """
        sql = ('select id, account_id, profit_amount, profit_date,'
               ' updated_time from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_ids_by_date(cls, account_id, date):
        if isinstance(date, datetime.date):
            date_from, date_to = (date, date)
        elif isinstance(date, tuple):
            date_from, date_to = date
        else:
            raise ValueError('"date" should be datetime.date or tuple')
        if date_from > date_to:
            raise ValueError(
                '%r must less or equal than %r' % (date_from, date_to))

        sql = ('select id from {0} where account_id = %s and'
               ' profit_date between %s and %s').format(cls.table_name)
        params = (account_id, date_from, date_to)
        rs = db.execute(sql, params)

        return [r[0] for r in rs]

    @classmethod
    @cache(cache_key_by_account)
    def get_ids_by_account(cls, account_id):
        sql = ('select id from {0} where account_id = %s').format(cls.table_name)
        params = (account_id)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    @cache(cache_key_for_total)
    def get_total_by_account(cls, account_id):
        sql = ('select sum(profit_amount) from {0} '
               'where account_id = %s').format(cls.table_name)
        params = (account_id,)
        rs = db.execute(sql, params)
        return rs[0][0] or decimal.Decimal(0)

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_multi_by_date(cls, account, date):
        """Gets multiple profit records for displaying.

        :param account: The wallet account.
        :type account: :class:`.account.WalletAccount`
        :param date: The date or date range.
        :type date: :class:`datetime.date` or :class:`tuple`
        :return: The list of :class:`WalletProfit`.
        """
        ids = cls.get_ids_by_date(account.id_, date)
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_for_total(cls, account_id):
        mc.delete(cls.cache_key_for_total.format(**locals()))

    @classmethod
    def clear_cache_by_account(cls, account_id):
        mc.delete(cls.cache_key_by_account.format(**locals()))

    @classmethod
    def synchronize(cls, client, wallet_account, days=14):
        """Synchronizes with remote API.

        :param client: The zslib client.
        :param wallet_account: The wallet account.
        """
        date_from = datetime.date.today() - datetime.timedelta(days=days)
        date_to = datetime.date.today() + datetime.timedelta(days=1)

        with wallet_account.track_broken_account():
            response = client.list_profit_records(
                transaction_id=uuid.uuid4().hex,
                user_id=wallet_account.secret_id,
                date_from=date_from,
                date_to=date_to)

        return [
            cls.record(wallet_account, r.profit_amount, r.profit_date)
            for r in response.records]

    @classmethod
    def synchronize_async(cls, wallet_account_id):
        wallet_profit_syncronizer.produce(wallet_account_id)
