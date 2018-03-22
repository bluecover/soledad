# -*- coding: utf-8 -*-

import random


class Server(object):
    _database = dict()

    def __init__(self, url):
        self.base_url = url

    def __repr__(self):
        return '<Test Couch Server>'

    def database(self, name):
        if not self._database.get(name):
            self._database[name] = Database()
        return self._database[name]

    def clear(self):
        self._database = dict()


class Database(object):
    def __init__(self):
        # Need to add rev
        self._db = dict()

    def get(self, name):
        return self._db.get(name, None)

    def save(self, value):
        name = value.get('_id')
        self._db[name] = value
        _id = random.randint(0, 9)
        _hash = '0775cd28a8736bbd0e0f541f657b9aa2'
        _d = value
        _d['_rev'] = '%s-%s' % (_id, _hash)
        return _d

    def clear(self):
        self._db = dict()

    def delete(self, doc):
        self._db = dict()
