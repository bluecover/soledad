from datetime import datetime, timedelta

from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.user.account import Account
from .client import OAuthClient


class OAuthGrant(EntityModel):
    """The grant token record."""

    cache_key = 'user:oauth:grant:{id_}'

    def __init__(self, id_, client_id, code, user_id, scopes, redirect_uri,
                 creation_time):
        self.id_ = id_
        self.client_id = client_id
        self.code = code
        self.user_id = user_id
        self.scopes = scopes.split(',')
        self.redirect_uri = redirect_uri
        self.creation_time = creation_time

    @cached_property
    def expires(self):
        return self.creation_time + timedelta(seconds=120)

    @cached_property
    def user(self):
        return Account.get(self.user_id)

    @cached_property
    def client(self):
        return OAuthClient.get(self.client_id)

    def delete(self):
        sql = 'delete from oauth_grant where id = %s'
        params = (self.id_,)

        db.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)

    @classmethod
    def add(cls, client_pk, code, redirect_uri, scopes, user_id):
        scopes = ','.join(scope.strip() for scope in scopes)
        now = datetime.utcnow()

        sql = ('insert into oauth_grant (client_id, code, user_id, scopes,'
               ' redirect_uri, creation_time) '
               'values (%s, %s, %s, %s, %s, %s)')
        params = (client_pk, code, user_id, scopes, redirect_uri, now)

        id_ = db.execute(sql, params)
        db.commit()

        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, client_id, code, user_id, scopes, redirect_uri,'
               ' creation_time from oauth_grant where id = %s')
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_by_code(cls, client_id, code):
        sql = 'select id from oauth_grant where client_id = %s and code = %s'
        params = (client_id, code)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))
