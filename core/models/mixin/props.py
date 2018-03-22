# -*- coding: utf-8 -*-

'''
基于couchdb开发的提供基本的属性的存储

各种Props的类不能混用！

例如一个类不能继承SecretPropsMixin，然后又继承PropsMixin

所有的Props都会自动持久化，不需要开发人员关心
'''

import copy
import pickle

from solar.utils.aes import encode as aes_encode, decode as aes_decode
from solar.db.utils import encode
from envcfg.json.solar import DEBUG

from libs.cache import mc
from libs.db.couchdb import cdb
from libs.db.secretdb import SecretDB


SCRETDB_MC_KEY = 'secret:db:%s'
SCRETDB_MC_REV_KEY = 'secret:db:%s:%s'
SCRETDB_DATA_MC_KEY = 'secret:db:item:%s:%s'

PROPS_MC_KEY = 'props:%s:%s'


'''
class Test(PropsMixin):
    # t = Test(1)
    # t.p = 12
    # print t.p

    def __init__(self, id):
        self.id = id

    def get_db(self):
        return 'test'

    def get_uuid(self):
        return 'test_%s' % self.id

    p = PropsItem('python', '')
'''


class BasePropsMixin(object):
    prefix = ''

    @property
    def _props_name(self):
        return '%s' % self.get_uuid()

    @property
    def _props_db_key(self):
        return '%s_%s' % (self.prefix, self.get_db())


class SecretPropsMixin(BasePropsMixin):
    """
    This is a secret props mixin

    继承这个类之后，类成员默认包含data属性，data为持久化的数据

    通过以下几个函数可以拿到相应的版本

    - @property: rev        : 获取当前数据的版本
    - @function: get_by_rev : 通过一个版本获得data的值
    - @property: data       : 获取当前数据
    """

    prefix = 'guihua_secret'
    _secret_props_pool = None

    @property
    def _secret_db(self):
        return SecretDB(cdb=cdb, db_name=self._props_db_key)

    def _get_secret_data(self):
        if self._secret_props_pool:
            return self._secret_props_pool
        r = SecretPropsData(self._secret_db, self._props_name)
        self._secret_props_pool = r
        return r

    data = property(_get_secret_data)


class SecretPropsData(object):
    """
    继承SecretPropsMixin后data实际的类SecretPropsData

    data的接口都可以看这个类
    """

    def __init__(self, secret_db, props_name):
        self.secret_db = secret_db
        self.props_name = props_name

    def __nonzero__(self):
        if self.data:
            return True
        return False

    def __repr__(self):
        return '<SecretPropsData %s>' % id(self)

    def update(self, **kwargs):
        _d = self.data or {}
        data = dict((k, v) for k, v in kwargs.iteritems() if v is not None)
        _d.update(data)
        self.secret_db.set(self.props_name, _d)
        self._clear_props_cache()

    def get(self, name):
        return encode(self.data.get(name))

    def _get_data(self):
        r = mc.get(SCRETDB_MC_KEY % self.props_name)
        if r:
            return r
        r = self.secret_db.get(self.props_name) or {}
        mc.set(SCRETDB_MC_KEY % self.props_name, r)
        return r

    def _clear_props_cache(self):
        mc.delete(SCRETDB_MC_KEY % self.props_name)

    def get_by_rev(self, rev):
        r = mc.get(SCRETDB_MC_REV_KEY % (self.props_name, rev))
        if r:
            return r
        r = self.secret_db.get(self.props_name, rev=rev)
        mc.set(SCRETDB_MC_REV_KEY % (self.props_name, rev), r)
        return r

    def get_rev(self):
        return self.data.get('_rev', None)

    def __getattr__(self, attr):
        return encode(self.data.get(attr, ''))

    data = property(_get_data)


class PropsMixin(BasePropsMixin):
    prefix = 'guihua'
    _props = None

    @property
    def props(self):
        if self._props is None:
            props = cdb.get(self._props_db_key, self._props_name) or {}
            staging = {}
            for key, value, descriptor in self.__iteritems(props, strict=DEBUG):
                if descriptor and descriptor.secret:
                    value = descriptor._decode(value)
                staging[key] = value
            self._props = staging
        return self._props

    @props.setter
    def props(self, props):
        staging = {}
        for key, value, descriptor in self.__iteritems(props, strict=DEBUG):
            if descriptor and descriptor.secret:
                value = descriptor._encode(value)
            staging[key] = value
        cdb.set(self._props_db_key, self._props_name, staging)
        self._props = None

    def update_props_items(self, props):
        self.props = props

    def clean_props_item(self):
        cdb.delete(self._props_db_key, self._props_name)

    def __iteritems(self, props, strict):
        for key, value in props.iteritems():
            if key.startswith('_'):
                descriptor = None
            else:
                try:
                    descriptor = getattr(self.__class__, key)
                except AttributeError:
                    descriptor = getattr(self.__class__, '_' + key, None)
                if not isinstance(descriptor, PropsItem):
                    # if strict:
                    #     raise TypeError('%s is not PropsItem' % key)
                    # else:
                    descriptor = None
            yield key, value, descriptor


class PropsItem(object):

    def __init__(self, name, default=None, out_filter=None, secret=False,
                 secret_key=None):
        assert name
        assert not name.startswith('_'), 'PropsItem名称第一个字符不能为下划线'
        self.name = str(name)
        self.default = default
        self.out_filter = out_filter
        self.secret = secret

        # 如果是加密的话
        if secret:
            # 创建默认的加密key
            if not secret_key:
                # 如果长度小于32，设置为32
                if len(name) < 32:
                    secret_key = str(name).rjust(32, name[0])
                else:
                    # 否则截取32位长度
                    secret_key = name[:32]
            assert len(secret_key) == 32

        self.secret_key = secret_key

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance.props.get(self.name)
        if value is None:
            return copy.deepcopy(self.default)
        elif self.out_filter:
            return self.out_filter(value)
        else:
            return value

    def __set__(self, instance, value):
        props = dict(instance.props)
        props[self.name] = value
        instance.update_props_items(props)

    def __del__(self, instance):
        props = dict(instance.props)
        props.pop(self.name, None)
        instance.update_props_items(props)

    def _encode(self, value):
        return aes_encode(pickle.dumps(value), self.secret_key)

    def _decode(self, value):
        return pickle.loads(aes_decode(bytes(value), self.secret_key))
