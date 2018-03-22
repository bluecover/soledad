from werkzeug.utils import cached_property
from gb2260 import Division

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.user.account import Account


class Address(EntityModel):
    """The address information in user profile."""

    table_name = 'profile_address'
    cache_key = 'profile:address:{id_}:v1'

    def __init__(self, id_, user_id, division_id, street,
                 receiver_name, receiver_phone, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.division_id = division_id
        self.street = street
        self.receiver_name = receiver_name
        self.receiver_phone = receiver_phone
        self.creation_time = creation_time

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def division(self):
        return Division.search(self.division_id)

    @cached_property
    def region(self):
        _name, _codes = '', []
        for current in self.division.stack():
            _name += current.name
            _codes.append(int(current.code))
        return _name, _codes

    @classmethod
    def add(cls, user_id, division_id, street, receiver_name='',
            receiver_phone=''):
        """Creates an address record.

        :param user_id: The id of local account.
        :param division_id: The GB2260 division code of city.
        :param street: The concrete street information.
        :param receiver_name: The real name of express delivery receiver.
        :param receiver_phone: The phone number of express delivery receiver.
        """
        cls._validate(user_id, division_id, street)

        sql = ('insert into {0} (user_id, division_id, street, receiver_name,'
               ' receiver_phone) '
               'values (%s, %s, %s, %s, %s)').format(cls.table_name)
        params = (user_id, division_id, street, receiver_name, receiver_phone)

        id_ = db.execute(sql, params)
        db.commit()

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, division_id, street, receiver_name,'
               ' receiver_phone, creation_time from {0} '
               'where id = %s').format(cls.table_name)
        params = (id_,)

        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_ids_by_user(cls, user_id):
        sql = ('select id from {0} where user_id = %s '
               'order by creation_time desc').format(cls.table_name)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        ids = cls.get_ids_by_user(user_id)
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def delete(cls, id_):
        sql = 'delete from {0} where id = %s'.format(cls.table_name)
        params = (id_,)

        db.execute(sql, params)
        db.commit()

        cls._clear_cache(id_)

    def update(self, division_id, street, receiver_name='', receiver_phone=''):
        self._validate(self.user_id, division_id, street)

        sql = ('update {0} set division_id = %s, street = %s,'
               ' receiver_name = %s, receiver_phone = %s'
               'where id = %s').format(self.table_name)
        params = (division_id, street, receiver_name, receiver_phone, self.id_)

        db.execute(sql, params)
        db.commit()

        self._clear_cache(self.id_)
        self.street = unicode(street)
        self.receiver_name = unicode(receiver_name)
        self.receiver_phone = unicode(receiver_phone)
        self.division_id = division_id
        self.__dict__.pop('division', None)

    @classmethod
    def _validate(cls, user_id, division_id, street):
        if not Account.get(user_id):
            raise ValueError('user not found')
        if not Division.search(division_id):
            raise ValueError('administrative division not found')
        # street should be unicode instead of bytes
        if not street:
            raise ValueError('street information too short')
        if len(unicode(street)) > 80:
            raise ValueError('street information too long')

    @classmethod
    def _clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))
