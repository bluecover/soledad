# -*- coding: utf-8 -*-

from libs.db.store import db
from libs.cache import cache


_LOC_CACHE_PRFIX = 'loc:'

LOCATION_CACH_KEY = _LOC_CACHE_PRFIX + '%s'
LOCATION_CHILDREN_CACH_KEY = _LOC_CACHE_PRFIX + 'children:%s'


class Location(object):
    def __init__(self, id, name_cn, parent_id):
        self.id = str(id)
        self.name_cn = name_cn
        self.parent_id = str(parent_id)

    def __unicode__(self):
        return u'<Location id=%s, name_cn=%s, parent_id=%s>' % (
            self.id, self.name_cn, self.parent_id)

    def __repr__(self):
        return 'Location(id="%s", name_cn="%s", parent_id="%s")' % (
            self.id, self.name_cn.encode('utf-8'), self.parent_id)

    @classmethod
    @cache(LOCATION_CACH_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, name_cn, parent_id '
                        'from location where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def gets(cls, ids):
        return [cls.get(id) for id in ids]

    @cache(LOCATION_CHILDREN_CACH_KEY % '{self.id}')
    def get_children_ids(self):
        rs = db.execute('select id from location where parent_id=%s',
                        self.id)
        return [str(id) for (id,) in rs]

    children_ids = property(get_children_ids)

    @property
    def children(self):
        return Location.gets(self.children_ids)

    @property
    def parent(self):
        return Location.get(self.parent_id)
