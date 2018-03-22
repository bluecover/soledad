# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from libs.db.secretdb import SecretDB
from libs.db.couchdb import cdb

sdb = SecretDB(cdb, db_name='secret')


class SecretDBTest(BaseTestCase):
    def test_secret_db_could_set(self):
        sdb.set('user1', dict(a=1))

    def test_secret_db_set_invalidate_json(self):
        def test():
            pass
        d = dict(a=1, b=test)
        with self.assertRaises(Exception) as cm:
            sdb.set('user1', d)
        self.assertEqual(cm.exception.args[0], 'value should be jsonize')

    def test_secret_db_could_get(self):
        r = sdb.set('user1', dict(a=1))
        r = sdb.get('user1')
        self.assertEqual(r['a'], 1)
