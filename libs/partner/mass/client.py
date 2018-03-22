# -*- coding:utf-8 -*-
from requests import Session
from requests.auth import AuthBase
from datetime import datetime
from six import string_types


class HTTPTokenAuth(AuthBase):
    """Attaches HTTP Token Authentication to the given Request object."""
    def __init__(self, token):
        if not isinstance(token, string_types) or not token:
            raise ValueError('invalid token')
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Token ' + self.token
        return r


class MassClient(object):
    """The client of mass API."""

    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.session = Session()
        self.auth = HTTPTokenAuth(token) if token else None

    def url_for(self, endpoint, params={}):
        url = '%s%s/?format=json' % (self.base_url, endpoint)
        for k in params:
            url += '&%s=%s' % (k, params[k])
        return url

    def request(self, endpoint, params={}, **kwargs):
        url = self.url_for(endpoint, params)
        response = self.session.get(url, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def response(self, json, datatype):
        return MassResponse(json, datatype)

    def get_fundata(self, fund_code, day):
        """ 得到某只基金指定日期的净值数据 """
        raw = self.request('funddaydata', {
            'fund': fund_code,
            'day': day.strftime('%Y-%m-%d')
        })
        return self.response(raw, MassDataFundata)

    def get_siv(self, day, stockindex='000001'):
        """ 得到股票指数 """
        raw = self.request('stockindexvalue', {
            'stockIndex': stockindex,
            'day': day.strftime('%Y-%m-%d')
        })
        return self.response(raw, MassDataStockIndexValue)


class MassData(object):

    fields = {}

    def __init__(self, json):
        params = {}
        for field in self.fields:
            if self.fields[field]:
                params[field] = getattr(self, self.fields[field])(json[field])
            else:
                params[field] = json[field]
        self.__dict__.update(params)

    def to_int(self, value):
        return int(value)

    def to_float(self, value):
        return float(value)

    def to_str(self, value):
        return str(value)

    def to_datetime(self, value):
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')

    def to_date(self, value):
        return datetime.strptime(value, '%Y-%m-%d')


class MassDataFundata(MassData):

    fields = {
        'NAV': 'to_float',
        'NCV': 'to_float',
        'NRR': 'to_float',
        'created': 'to_datetime',
        'day': 'to_date',
        'fund': 'to_str',
        'id': 'to_int',
        'updated': 'to_datetime',
    }


class MassDataStockIndexValue(MassData):

    fields = {
        'day': 'to_date',
        'close_price': 'to_float',
        'created': 'to_datetime',
        'updated': 'to_datetime',
        'id': 'to_int',

    }


class MassResponse(object):

    limit = 0
    total_count = 0
    offset = 0
    previous = None
    next = None
    objects = []

    def __init__(self, json, datatype):
        self.total_count = int(json['count'])
        self.previous = json['previous']
        self.next = json['next']
        self.objects = []
        for obj in json['results']:
            self.objects.append(datatype(obj))
