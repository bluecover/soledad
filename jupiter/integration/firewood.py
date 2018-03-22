from __future__ import absolute_import

import json
import uuid
import decimal
import collections

from flask import current_app
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from werkzeug.local import LocalProxy
from werkzeug.urls import url_join
from werkzeug.http import parse_options_header
from werkzeug.utils import cached_property
from requests_oauthlib import OAuth2Session

from libs.cache import mc


class FirewoodClient(object):
    """The client for accessing firewood service.

    The detail of OAuth 2 may be hidden in this class. But you need to known
    basic HTTP knownledge and the API design of firewood service.

    Feel easy to ask your colleague if any question exists.
    """

    _token_rds_key = 'firewood:{0.client_id}:token'

    def __init__(self, base_url, token_url, client_id, client_secret, scope):
        self.base_url = base_url.rstrip('/')
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

    @cached_property
    def session(self):
        """Session with pre-loaded oauth token."""
        client = BackendApplicationClient(client_id=self.client_id)
        session = OAuth2Session(client=client)
        return self._process_token(session)

    def _process_token(self, session):
        """Loads token from cache or fetches from remote."""
        token = self._load_token()
        if token:
            # FIXME too many private methods are called
            session.token = token
            session._client.token = token
            session._client.access_token = token['access_token']
        else:
            token = session.fetch_token(
                token_url=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope=self.scope)
            self._save_token(token)
        return session

    def _save_token(self, token):
        key = self._token_rds_key.format(self)
        data = json.dumps(token)
        mc.set(key, data)
        mc.expireat(key, int(token['expires_at']))

    def _load_token(self):
        key = self._token_rds_key.format(self)
        data = mc.get(key)
        if data:
            return json.loads(data)

    def _drop_token(self):
        key = self._token_rds_key.format(self)
        mc.delete(key)
        self.__dict__.pop('session', None)

    def request(self, method, resource, *args, **kwargs):
        """Sends request to remote server.

        :param method: HTTP method to use.
        :param resource: Relative path of resource.
        :param *args: Other arguments that :class:`requests.Request` takes.
        :param *kwargs: Other arguments that :class:`requests.Request` takes.
        """
        with_exception = kwargs.pop('with_exception', FirewoodException)

        url = url_join(self.base_url + '/', resource.lstrip('/'))

        for i in reversed(xrange(3)):
            try:
                response = self.session.request(method, url, *args, **kwargs)
            except TokenExpiredError:
                self._drop_token()
                if i == 0:  # retry last time
                    raise
            else:
                if response.status_code == 401:
                    self._drop_token()
                else:
                    break

        if response.ok:
            return response

        # if the response could not be understood, we throw all errors
        content_type, _ = parse_options_header(response.headers['content-type'])
        if content_type.startswith('application/json'):
            raise with_exception.from_response(response)
        elif response.status_code == 500:
            raise FirewoodInternalError(response)
        else:
            response.raise_for_status()

    def create_account(self, person_name, person_ricn):
        """Creates an account in remote server."""
        return self.request('POST', '/account', json={
            'person_name': person_name,
            'person_ricn': person_ricn,
        })

    def show_account(self, account_uid):
        assert isinstance(account_uid, uuid.UUID)
        url = '/account/{0}'.format(account_uid)
        return self.request('GET', url)

    def create_transaction(self, account_uid, amount, tags=[]):
        assert isinstance(account_uid, uuid.UUID)
        assert isinstance(amount, decimal.Decimal)
        url = '/account/{0}/transactions'.format(account_uid)
        return self.request('POST', url, json={
            'amount': unicode(amount),
            'tags': list(tags),
        })

    def show_transaction(self, account_uid, transaction_uid):
        assert isinstance(account_uid, uuid.UUID)
        assert isinstance(transaction_uid, uuid.UUID)
        url = '/account/{0}/transaction/{1}'.format(
            account_uid, transaction_uid)
        return self.request('GET', url)

    def confirm_transaction(self, account_uid, transaction_uid):
        assert isinstance(account_uid, uuid.UUID)
        assert isinstance(transaction_uid, uuid.UUID)
        url = '/account/{0}/transaction/{1}'.format(
            account_uid, transaction_uid)
        return self.request('PATCH', url, json={
            'is_confirmed': True
        })

    def cancel_transaction(self, account_uid, transaction_uid):
        assert isinstance(account_uid, uuid.UUID)
        assert isinstance(transaction_uid, uuid.UUID)
        url = '/account/{0}/transaction/{1}'.format(
            account_uid, transaction_uid)
        return self.request('DELETE', url)

    def list_transactions(self, account_uid):
        assert isinstance(account_uid, uuid.UUID)
        url = '/account/{0}/transactions'.format(account_uid)
        return self.request('GET', url)


@LocalProxy
def firewood():
    """The context-bound instance of :class:`.FirewoodClient`."""
    if 'firewood_client' not in current_app.extensions:
        current_app.extensions['firewood_client'] = FirewoodClient(
            base_url=current_app.config['FIREWOOD_BASE_URL'],
            token_url=current_app.config['FIREWOOD_TOKEN_URL'],
            client_id=current_app.config['FIREWOOD_CLIENT_ID'],
            client_secret=current_app.config['FIREWOOD_CLIENT_SECRET'],
            scope=['basic', 'credit', 'debit'])
    return current_app.extensions['firewood_client']


class FirewoodException(Exception):
    """The basic exception of firewood client."""

    ErrorItem = collections.namedtuple('ErrorItem', 'kind field message')

    def __init__(self, errors, response=None):
        super(FirewoodException, self).__init__(errors)
        self.response = response

    @property
    def errors(self):
        """The list of error items."""
        return self.args[0]

    @classmethod
    def make_error_item(cls, error_item):
        return cls.ErrorItem(
            kind=error_item.get('kind'),
            field=error_item.get('field'),
            message=error_item.get('message'))

    @classmethod
    def from_response(cls, response):
        data = response.json()
        errors = [cls.make_error_item(item) for item in data.get('errors', [])]
        return cls(errors, response)


class FirewoodInternalError(FirewoodException):
    """The internal errors occured."""

    def __init__(self, response=None):
        errors = [{'kind', 'internal_error'}]
        super(FirewoodInternalError, self).__init__(errors, response)
