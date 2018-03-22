# coding: utf-8

from datetime import datetime, timedelta
from warnings import warn

from MySQLdb import IntegrityError
from werkzeug.security import safe_str_cmp

from libs.db.store import db
from libs.cache import (mc, static_mc, cache)
from core.models.base import EntityModel
from core.models.consts import SESSION_EXPIRE_DAYS
from core.models.utils import pwd_hash, randbytes2
from core.models.user.consts import ACCOUNT_STATUS, ACCOUNT_GENDER, ACCOUNT_REG_TYPE
from core.models.user.errors import FreezingPreventedError
from .alias import AliasMixin
from .channel import ChannelMixin
from .signals import before_freezing_user

REGISTERED_USER_COUNT_CACHE_KEY = 'register_users_count'


class Account(EntityModel, AliasMixin, ChannelMixin):
    """好规划站点账号"""

    class Meta:
        repr_attr_names = ['name', 'status', 'create_time']

    cache_key = 'user_account:{account_id}'

    def __init__(self, id_, password, salt, name, gender, status,
                 session_id, session_expire_time, create_time, update_time):
        self.id_ = str(id_)
        self.password = password
        self.salt = salt
        self.name = name
        self.gender = str(gender)
        self.status = str(status)
        self.session_id = session_id
        self.session_expire_time = session_expire_time
        self.create_time = create_time
        self.update_time = update_time

    @property
    def id(self):
        warn(DeprecationWarning('use user.id_ instead'))
        return self.id_

    @property
    def creation_date(self):
        return self.create_time.date()

    # 如果手机用户A在获取注册验证码后未完成注册，而后用户B申请绑定该手机号，则A用户状态变成FAILED
    def is_failed_account(self):
        return self.status == ACCOUNT_STATUS.FAILED

    def is_normal_account(self):
        return self.status == ACCOUNT_STATUS.NORMAL

    def need_verify(self):
        return self.status == ACCOUNT_STATUS.NEED_VERIFY

    @classmethod
    @cache(cache_key)
    def get(cls, account_id):
        rs = db.execute('select id, password, '
                        'salt, name, gender, status,'
                        'session_id, session_expire_time, '
                        'create_time, update_time from account '
                        'where id=%s', (account_id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id) for id in ids]

    @classmethod
    def gets(cls, ids):
        warn(DeprecationWarning('use user.id_ instead'))
        return cls.get_multi(ids)

    @classmethod
    def get_users_count(cls):
        if not static_mc.exists(REGISTERED_USER_COUNT_CACHE_KEY):
            sql = 'select count(1) from account where status = %s'
            params = (1,)
            rs = db.execute(sql, params)
            static_mc.set(REGISTERED_USER_COUNT_CACHE_KEY, int(rs[0][0]))
        return static_mc.get(REGISTERED_USER_COUNT_CACHE_KEY)

    @classmethod
    def add(cls, alias, passwd_hash, salt, name,
            reg_type=ACCOUNT_REG_TYPE.MOBILE,
            gender=ACCOUNT_GENDER.UNKNOWN,
            status=ACCOUNT_STATUS.NEED_VERIFY):
        if Account.get_by_alias(alias):
            return
        try:
            id = db.execute('insert into account '
                            '(password, salt, name, gender, '
                            'status, create_time)'
                            'values(%s, %s, %s, %s, %s, %s)',
                            (passwd_hash, salt, name, gender,
                             status, datetime.now()))
            if id:
                db.execute('insert into account_alias (`id`, alias, reg_type) '
                           'values(%s, %s, %s)', (id, alias, reg_type))
                db.commit()
                return cls.get(id)
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert account failed')

    def update_status(self, status):
        if status == self.status or status not in ACCOUNT_STATUS.values():
            return False
        db.execute('update account set status=%s where id=%s',
                   (status, self.id_))
        db.commit()
        self.clear_cache()
        return True

    def clear_cache(self):
        mc.delete(self.cache_key.format(account_id=self.id_))
        ta = self.get_type_alias()
        mc.delete(self.alias_cache_key % self.id_)
        for type_, alias in ta.iteritems():
            mc.delete(self.alias_cache_by_type_key % (alias, type_))

    def verify_password(self, password):
        passwd_hash = pwd_hash(self.salt, password)
        return safe_str_cmp(passwd_hash, self.password)

    def change_passwd_hash(self, salt, passwd_hash):
        db.execute('update account set password=%s, salt=%s where id=%s',
                   (passwd_hash, salt, self.id_))
        db.commit()
        self.clear_cache()

    def change_nickname(self, nickname):
        db.execute('update account set name=%s where id=%s',
                   (nickname, self.id_))
        db.commit()
        self.clear_cache()

    def has_valid_session(self):
        if not self.session_id:
            return False
        if not self.session_expire_time:
            return False
        return self.session_expire_time > datetime.now()

    def is_valid_session(self, key):
        return self.session_id == key

    def create_session(self):
        session_id = randbytes2(6)

        expire_time = datetime.now() + timedelta(days=SESSION_EXPIRE_DAYS)
        db.execute('update account set session_id=_latin1%s, '
                   'session_expire_time=%s where id=%s',
                   (session_id, expire_time, self.id_))
        db.commit()
        self.session_expire_time = expire_time
        self.session_id = session_id
        self.clear_cache()

    def clear_session(self):
        db.execute('update account set session_id=NULL, '
                   'session_expire_time=%s where id=%s',
                   ('0000-00-00 00:00:00', self.id_))
        db.commit()
        self.session_id = None
        self.clear_cache()
        return True

    def freeze(self):
        result = before_freezing_user.send(self)
        owned_services = [func.product_name for func, r in result if r is True]
        if owned_services:
            raise FreezingPreventedError(owned_services)
        self.unbind_mobile()
        self.update_status(ACCOUNT_STATUS.BANNED)
        self.clear_session()
        return result


# @user_register_completed.connect
def on_user_register_complete():
    ''' function that increase the register user count '''
    static_mc.incr(REGISTERED_USER_COUNT_CACHE_KEY)
