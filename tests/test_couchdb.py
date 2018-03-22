# -*- coding: utf-8 -*-

from solar.db.utils import encode

from libs.db.couchdb import cdb
from .framework import BaseTestCase


class CouchDBTest(BaseTestCase):
    def test_couch_db_could_set(self):
        cdb.set('test', 'name', dict(a=1))

    def test_couch_db_set_invalidate_json(self):
        def test():
            pass
        d = dict(a=1, b=test)
        with self.assertRaises(Exception) as cm:
            cdb.set('test', 'name', d)
        self.assertEqual(cm.exception.args[0], 'value should be jsonize')

    def test_couch_db_could_get(self):
        cdb.set('test', 'name', dict(a=1))
        r = cdb.get('test', 'name')
        self.assertEqual(r['a'], 1)

    def test_couchdb_encode(self):
        value = dict(a=u'haha', b=u'tete', c=dict(a='1'), e=['ha', u'la'])
        values = [1, 2, dict(a='something')]
        d = dict(key=value,
                 key1=123,
                 key2='str',
                 keys=values,
                 key3=dict(a=[], b=0, c=None))
        d = encode(d)
        self.assertTrue(d.get('key'))
        self.assertTrue(d.get('key1'))
        self.assertTrue(d.get('key2'))
        self.assertTrue(d.get('keys'))

        self.assertEqual(d.get('key').get('a'), 'haha')
        self.assertEqual(d.get('key').get('b'), 'tete')
        self.assertEqual(d.get('key').get('c').get('a'), '1')
        self.assertTrue('ha' in d.get('key').get('e'))
        self.assertTrue('la' in d.get('key').get('e'))

        self.assertTrue(1 in d.get('keys'))
        self.assertTrue(1 in d.get('keys'))

        self.assertEqual(d.get('keys')[-1].get('a'), 'something')

        self.assertEqual(d.get('key3').get('a'), [])
        self.assertEqual(d.get('key3').get('b'), 0)
        self.assertEqual(d.get('key3').get('c'), None)
