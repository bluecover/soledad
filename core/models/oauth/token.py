from time import mktime
from datetime import timedelta, datetime

from arrow import Arrow
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.user.change_password import password_changed
from .client import OAuthClient


class OAuthToken(EntityModel):
    """The bearer token."""

    class Meta:
        repr_attr_names = ['access_token', 'refresh_token', 'is_frozen']

    cache_key = 'user:oauth:bearer:{id_}:v2'
    cache_by_token_key = 'user:oauth:bearer:t:{token_type}:{token_value}'
    cache_by_user_key = 'user:oauth:bearer:u:{user_id}:ids'

    def __init__(self, id_, client_pk, user_id, access_token, refresh_token,
                 scopes, is_frozen, expires_in, creation_time):
        self.id_ = id_
        self.client_pk = client_pk  #: The primary key of OAuth client
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.scopes = scopes.split()
        self.is_frozen = bool(is_frozen)
        self.expires_in = expires_in
        self.creation_time = creation_time

    @cached_property
    def client(self):
        return OAuthClient.get(self.client_pk)

    @cached_property
    def client_id(self):
        return self.client.client_id

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def expires(self):
        creation_time = Arrow.fromdatetime(self.creation_time, 'local')
        expires_delta = timedelta(seconds=self.expires_in)
        return (creation_time.to('utc') + expires_delta).naive

    @classmethod
    def add(cls, client_pk, user_id, scopes, access_token, refresh_token,
            expires_in):
        scopes = ' '.join(scope.strip() for scope in scopes)
        is_frozen = False
        creation_time = datetime.now()

        sql = ('insert into oauth_token (client_id, user_id, access_token,'
               ' refresh_token, scopes, is_frozen, expires_in, creation_time) '
               'values (%s, %s, %s, %s, %s, %s, %s, %s) ')
        params = (client_pk, user_id, access_token, refresh_token, scopes,
                  is_frozen, expires_in, creation_time)

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_token(access_token)
        cls.clear_cache_by_token(refresh_token)
        cls.clear_cache_by_user(user_id)

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, client_id, user_id, access_token, refresh_token,'
               ' scopes, is_frozen, expires_in, creation_time '
               'from oauth_token where id = %s')
        params = (id_,)

        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_by_token_key)
    def get_id_by_token(cls, token_type, token_value):
        assert token_type in ('access_token', 'refresh_token')
        sql = 'select id from oauth_token where {0} = %s'.format(token_type)
        params = (token_value,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_access_token(cls, access_token):
        id_ = cls.get_id_by_token('access_token', access_token)
        if id_:
            return cls.get(id_)

    @classmethod
    def get_by_refresh_token(cls, refresh_token):
        id_ = cls.get_id_by_token('refresh_token', refresh_token)
        if id_:
            return cls.get(id_)

    @classmethod
    @cache(cache_by_user_key)
    def get_ids_by_user(cls, user_id):
        sql = 'select id from oauth_token where user_id = %s'
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        ids = cls.get_ids_by_user(user_id)
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_all_ids(cls):
        sql = 'select id from oauth_token order by id asc'
        rs = db.execute(sql, ())
        return [r[0] for r in rs]

    @classmethod
    def vacuum(cls, ids=None, grace_time=None):
        vacuum_time = datetime.utcnow()
        vacuum_id = mktime(vacuum_time.timetuple())
        grace_time = timedelta() if grace_time is None else grace_time
        tokens = (cls.get(id_) for id_ in ids or cls.get_all_ids())
        for token in tokens:
            if token.expires + grace_time >= vacuum_time:
                continue
            rsyslog.send(
                '[%s] %r of %r has expired' % (vacuum_id, token, token.client),
                'oauth_token_vacuum')
            try:
                token.delete()
            except:
                rsyslog.send('[%s] failed' % vacuum_id, 'oauth_token_vacuum')
                raise
        rsyslog.send('[%s] success' % vacuum_id, 'oauth_token_vacuum')

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_token(cls, token_value):
        for token_type in ('access_token', 'refresh_token'):
            mc.delete(cls.cache_by_token_key.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_by_user_key.format(**locals()))

    def clear_cache_by_instance(self):
        self.clear_cache(self.id_)
        self.clear_cache_by_token(self.access_token)
        self.clear_cache_by_token(self.refresh_token)
        self.clear_cache_by_user(self.user_id)

    def delete(self):
        sql = 'delete from oauth_token where id = %s'
        params = (self.id_,)

        db.execute(sql, params)
        db.commit()

        self.clear_cache_by_instance()

    def freeze(self):
        self._set_is_frozen(flag=True)

    def unfreeze(self):
        self._set_is_frozen(flag=False)

    def _set_is_frozen(self, flag):
        self.is_frozen = bool(flag)
        sql = 'update oauth_token set is_frozen = %s where id = %s'
        params = (self.is_frozen, self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache_by_instance()


@password_changed.connect
def revoke_user_tokens(sender):
    tokens = OAuthToken.get_multi_by_user(sender.id_)
    for token in tokens:
        rsyslog.send('freeze %r of %s' % (token, sender.id_), 'oauth_token')
        token.freeze()
