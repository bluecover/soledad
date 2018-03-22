from oauthlib.common import generate_token
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from .scopes import OAuthScope


class OAuthClient(EntityModel):
    """The registered OAuth Application.

    Flask-OAuthlib have following features but we don't need them for now.

     - client_type be "public"
     - multiple redirect URIs (by redirect_uris and default_redirect_uri field)
     - multiple scopes (by default_scopes)

    We provide them as static properties to satisfy the protocol.
    """

    cache_key = 'user:oauth:client:{id_}:v1'
    cache_by_client_id_key = 'user:oauth:client:client_id:{client_id}'

    def __init__(self, id_, name, client_id, client_secret, redirect_uri,
                 allowed_grant_types, allowed_response_types, allowed_scopes):
        self.id_ = id_
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.allowed_grant_types = allowed_grant_types.split()
        self.allowed_response_types = allowed_response_types.split()
        self._allowed_scopes = allowed_scopes.split()

    @cached_property
    def client_type(self):
        return 'confidential'

    @cached_property
    def redirect_uris(self):
        return [self.redirect_uri] if self.redirect_uri else []

    @cached_property
    def default_redirect_uri(self):
        if self.redirect_uri:
            return self.redirect_uri

    @cached_property
    def allowed_scopes(self):
        return {OAuthScope(value) for value in self._allowed_scopes}

    @cached_property
    def default_scopes(self):
        if self.allowed_scopes:
            return [scope.value for scope in self.allowed_scopes]
        return [OAuthScope.basic.value]

    def _clear_cached_properties(self):
        self.__dict__.pop('redirect_uris', None)
        self.__dict__.pop('default_redirect_uri', None)
        self.__dict__.pop('allowed_scopes', None)
        self.__dict__.pop('default_scopes', None)

    @classmethod
    def add(cls, name, redirect_uri='', allowed_grant_types=None,
            allowed_response_types=None, allowed_scopes=None):
        client_id = generate_token()
        client_secret = generate_token()
        allowed_grant_types = allowed_grant_types or ['authorization_code']
        allowed_response_types = allowed_response_types or ['token']
        allowed_scopes = set(allowed_scopes or []) | {OAuthScope.basic}

        sql = ('insert into oauth_client'
               ' (name, client_id, client_secret, redirect_uri,'
               '  allowed_grant_types, allowed_response_types,'
               '  allowed_scopes) '
               'values (%s, %s, %s, %s, %s, %s, %s)')
        params = (
            name, client_id, client_secret, redirect_uri,
            ' '.join(allowed_grant_types), ' '.join(allowed_response_types),
            ' '.join(scope.value for scope in allowed_scopes))

        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)

        return cls.get(id_)

    def validate_scopes(self, scopes):
        allowed_scopes = {scope.value for scope in self.allowed_scopes}
        return allowed_scopes.issuperset(set(scopes))

    def edit(self, name, redirect_uri, allowed_grant_types,
             allowed_response_types, allowed_scopes):
        allowed_grant_types = list(allowed_grant_types)
        allowed_response_types = list(allowed_response_types)
        allowed_scopes = [scope.value for scope in allowed_scopes]

        sql = ('update oauth_client set name = %s, redirect_uri = %s,'
               ' allowed_grant_types = %s, allowed_response_types = %s,'
               ' allowed_scopes = %s '
               'where id = %s')
        params = (
            name, redirect_uri, ' '.join(allowed_grant_types),
            ' '.join(allowed_response_types), ' '.join(allowed_scopes),
            self.id_)
        db.execute(sql, params)
        db.commit()

        self.clear_cache(self.id_)
        self._clear_cached_properties()

        self.name = name
        self.redirect_uri = redirect_uri
        self.allowed_grant_types = allowed_grant_types
        self.allowed_response_types = allowed_response_types
        self._allowed_scopes = allowed_scopes

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, name, client_id, client_secret, redirect_uri,'
               ' allowed_grant_types, allowed_response_types, allowed_scopes '
               'from oauth_client where id = %s')
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_by_client_id_key)
    def get_id_by_client_id(cls, client_id):
        sql = 'select id from oauth_client where client_id = %s'
        params = (client_id,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_all(cls):
        sql = 'select id from oauth_client order by id asc'
        rs = db.execute(sql)
        return [cls.get(r[0]) for r in rs]

    @classmethod
    def get_by_client_id(cls, client_id):
        id_ = cls.get_id_by_client_id(client_id)
        if id_:
            return cls.get(id_)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))
