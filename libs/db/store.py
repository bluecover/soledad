from __future__ import absolute_import

from solar.db.store.context import init_context
from solar.db.store import SqlStore


db = SqlStore.init_by_context(init_context('solar'))
