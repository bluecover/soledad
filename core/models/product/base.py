# -*- coding: utf-8 -*-

'''
Base product class
'''
from libs.db.store import db
from libs.cache import cache, mc
from core.models.mixin.props import PropsMixin, PropsItem

from .consts import PRODUCT_STATUS, RECOMMEND_RANK

_PRODUCT_CACHE_KEY_PREFIX = 'product:'
_ALL_PRODUCT_CACHE_KEY = _PRODUCT_CACHE_KEY_PREFIX + 'all:%s:%s'
_PRODUCT_CACHE_KEY = _PRODUCT_CACHE_KEY_PREFIX + 'kind:%s:%s'


class ProductBase(PropsMixin):
    '''
    Base class
    '''

    kind = ''
    _table = ''

    def get_uuid(self):
        if not self.kind:
            raise NotImplementedError('product kind does not assign')
        return '%s:info:%s' % (self.kind, self.id)

    def get_db(self):
        # All the products save in one CouchDB
        return 'product'

    name = PropsItem('name', '')  # 产品名称
    organization = PropsItem('organization', '')  # 发行机构
    recommended_reason = PropsItem('recommended_reason', '')
    link = PropsItem('link', '')
    mobile_link = PropsItem('mobile_link', '')
    phone = PropsItem('phone', '')
    rec_reason = recommended_reason

    def __init__(self, id, type, status, rec_rank, create_time, update_time):
        self.id = str(id)
        self.type = str(type)
        self.status = str(status)
        self.rec_rank = rec_rank
        self.create_time = create_time
        self.update_time = update_time

    @property
    def type_name(self):
        return '未命名'

    @classmethod
    @cache(_PRODUCT_CACHE_KEY % ('{cls.kind}', '{id}'))
    def get(cls, id):
        rs = db.execute('select id, `type`, status, rec_rank, '
                        'create_time, update_time '
                        'from ' + cls._table + ' '
                        'where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, type, rec_rank=RECOMMEND_RANK.ONE, status=PRODUCT_STATUS.ON):
        id = db.execute('insert into ' + cls._table + ' '
                        '(`type`, status, rec_rank) values '
                        '(%s, %s, %s)', (type, status, rec_rank))
        if id:
            db.commit()
            for k, v in PRODUCT_STATUS.items():
                mc.delete(_ALL_PRODUCT_CACHE_KEY % (cls.kind, v))
            mc.delete(_PRODUCT_CACHE_KEY % (cls.kind, id))
            return str(id)

    def update(self, **kwargs):
        d = dict((key, value) for key, value in kwargs.iteritems() if value)
        self.update_props_items(d)

    def update_rank(self, rank):
        assert isinstance(rank, int)
        if self.rec_rank == rank:
            return
        db.execute('update ' + self._table + ' set rec_rank=%s', (rank, ))
        db.commit()
        self.clear_cache()

    def update_type(self, type):
        assert isinstance(type, str)
        if self.type == type:
            return
        db.execute('update ' + self._table + ' set type=%s', (type, ))
        db.commit()
        self.clear_cache()

    @classmethod
    def gets(cls, ids):
        return [cls.get(id) for id in ids]

    @classmethod
    @cache(_ALL_PRODUCT_CACHE_KEY % ('{cls.kind}', '{status}'))
    def _get_all_ids(cls, status, start=0, limit=20):
        rs = db.execute('select id '
                        'from ' + cls._table + ' '
                        'where status=%s '
                        'order by rec_rank desc limit %s,%s',
                        (status, start, limit))
        ids = [str(id) for (id,) in rs]
        return ids

    @classmethod
    def get_all(cls, status=PRODUCT_STATUS.ON, start=0, limit=20):
        assert cls._table
        ids = cls._get_all_ids(status=status, start=start, limit=limit)
        return cls.gets(ids)

    def hide(self):
        db.execute('update ' + self._table + ' set status=%s where id=%s',
                   (PRODUCT_STATUS.OFF, self.id))
        db.commit()
        self.clear_cache()

    def publish(self):
        db.execute('update ' + self._table + ' set status=%s where id=%s',
                   (PRODUCT_STATUS.ON, self.id))
        db.commit()
        self.clear_cache()

    delete = hide

    def clear_cache(self):
        self._clear_all_cache()
        mc.delete(_PRODUCT_CACHE_KEY % (self.kind, self.id))

    def _clear_all_cache(self):
        for k, v in PRODUCT_STATUS.items():
            mc.delete(_ALL_PRODUCT_CACHE_KEY % (self.kind, v))
