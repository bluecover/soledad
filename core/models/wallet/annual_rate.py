from __future__ import print_function, absolute_import, unicode_literals

import datetime
import hashlib
import collections

import numpy as np
from werkzeug.utils import cached_property

from core.models.base import EntityModel
from libs.db.store import db
from libs.cache import mc, cache


class WalletAnnualRate(EntityModel):
    """The annual rate in global scope."""

    class Meta:
        repr_attr_names = ['date', 'annual_rate', 'fund_code']

    table_name = 'wallet_annual_rate'
    cache_key = 'wallet:annual_rate:{id_}'

    def __init__(self, id_, date, annual_rate, ttp_income, fund_code):
        self.id_ = id_
        self.date = date
        self.annual_rate = annual_rate
        self.ten_thousand_pieces_income = ttp_income
        self.fund_code = fund_code

    @classmethod
    def record(cls, date, annual_rate, ttp_income, fund_code):
        """Creates or updates one record of some day."""
        # The ``on duplicate key update`` is useful in this situation.
        # But there are some MySQL issues (Bug #11765650, Bug #58637) stop us
        # from using it.
        #
        # The annual rates could be updated by schedule tasks only. We could
        # trust it that it is far away from concurrent writting.
        # So UPDATE after SELECT is safe there.
        #
        # See also:
        # http://dev.mysql.com/doc/refman/5.6/en/insert-on-duplicate.html
        id_ = cls.get_id_by_date(date, fund_code)
        if id_:
            sql = ('update {0} set annual_rate = %s, ttp_income = %s '
                   'where id = %s').format(cls.table_name)
            params = (annual_rate, ttp_income, id_)
            db.execute(sql, params)
        else:
            sql = ('insert into {0} (date, annual_rate, ttp_income,'
                   ' fund_code) '
                   'values (%s, %s, %s, %s)').format(cls.table_name)
            params = (date, annual_rate, ttp_income, fund_code)
            id_ = db.execute(sql, params)

        db.commit()
        cls.clear_cache(id_)

        return cls.get(id_)

    @classmethod
    def record_multi(cls, fund_code, collection):
        """Creates or updates from multiple records.

        :param fund_code: The code of fund.
        :param collection: The response object which comes from return value
                           of :meth:`zslib.client.Client.list_annual_rates`.
        """
        return [
            cls.record(
                r.date, r.annual_rate, r.ten_thousand_pieces_income, fund_code)
            for r in collection.records]

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, date, annual_rate, ttp_income, fund_code from {0} '
               'where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_multi_by_date_range(cls, date_from, date_to, fund_code):
        """Gets records by date range and fund code."""
        ids = cls.get_ids_by_date_range(date_from, date_to, fund_code)
        return cls.get_multi(ids)

    @classmethod
    def get_id_by_date(cls, date, fund_code):
        sql = ('select id from {0} where date = %s and'
               ' fund_code = %s').format(cls.table_name)
        params = (date, fund_code)
        rs = db.execute(sql, params)
        return rs[0][0] if rs else None

    @classmethod
    def get_ids_by_date_range(cls, date_from, date_to, fund_code):
        sql = ('select id from {0} where date >= %s and date < %s and'
               ' (fund_code = %s)').format(cls.table_name)
        params = (date_from, date_to, fund_code)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def synchronize(cls, client, fund_code, days=14):
        """Synchronizes with remote API.

        :param client: The zslib client.
        :param fund_code: The code of fund.
        :return: The list of created records.
        """
        response = client.list_annual_rates(
            fund_code=fund_code,
            date_from=datetime.date.today() - datetime.timedelta(days=days),
            date_to=datetime.date.today() + datetime.timedelta(days=1))
        return cls.record_multi(fund_code, response)


average_item = collections.namedtuple('average_item', 'annual_rate ttp')


class WalletAnnualRateList(object):
    """The collection of annual rates."""

    cache_key_for_average = 'wallet:annual_rate_list:{self._ids}'

    def __init__(self, ids):
        self.ids = list(sorted(ids, reverse=True))

    def get_multi(self, start=None, stop=None, step=None):
        return WalletAnnualRate.get_multi(self.ids[start:stop:step])

    @cached_property
    def _ids(self):
        sha1 = hashlib.sha1(b''.join(bytes(id_) for id_ in self.ids))
        return sha1.hexdigest()

    @cache(cache_key_for_average)
    def average(self):
        records = self.get_multi()
        if not records:
            return average_item(0, 0)
        annual_rate = np.mean([r.annual_rate for r in records])
        ttp = np.mean([r.ten_thousand_pieces_income for r in records])
        return average_item(annual_rate, ttp)
