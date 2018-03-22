# coding: utf-8

from __future__ import absolute_import, unicode_literals

import json

from pytest import yield_fixture, fixture
from mock import patch
from jupiter.app import create_app
from libs.db.store import db
from libs.db.rdstore import rdstore
from libs.db.couchdb import cdb
from .conf_consts import ProductConsts
from .utils import Obj
from core.models.user.account import Account
from core.models.user.consts import ACCOUNT_REG_TYPE
from core.models.oauth.client import OAuthClient
from core.models.oauth.token import OAuthToken
from core.models.oauth.scopes import OAuthScope
from core.models.profile.identity import Identity
from core.models.profile.bankcard import BankCardManager
from core.models.hoarder.vendor import Vendor, Provider
from core.models.hoard.xinmi.product import XMProduct
from core.models.hoarder.product import Product
from crons.hoarder.cron_updating_sxb_products import check_available_for_product


@yield_fixture(scope='function')
def sqlstore():
    db.is_testing = lambda: True
    yield db
    db.execute('truncate table account')
    db.execute('truncate table account_alias')
    db.execute('truncate table oauth_client')
    db.execute('truncate table oauth_grant')
    db.execute('truncate table oauth_token')
    db.execute('truncate table hoard_bankcard')
    db.execute('truncate table profile_identity')
    db.execute('truncate table user_verify')
    db.execute('truncate table wallet_account')
    db.execute('truncate table wallet_profit')
    db.execute('truncate table wallet_transaction')
    db.execute('truncate table wallet_annual_rate')
    db.execute('truncate table wallet_bankcard_binding')
    db.execute('truncate table pusher_device_binding')
    db.execute('truncate table pusher_user_record')
    db.execute('truncate table user_tag')
    db.execute('truncate table redeem_code')
    db.execute('truncate table redeem_code_usage')
    db.execute('truncate table coupon_package_redeem_code')
    db.execute('truncate table advert_record')
    db.execute('truncate table hoard_xm_account')
    # db.execute('truncate table hoard_xm_order')
    db.execute('truncate table hoard_zhiwang_account')
    # db.execute('truncate table hoarder_order')


@yield_fixture(scope='function')
def couchstore():
    yield cdb
    cdb.server.delete('guihua_hoard')


@yield_fixture(scope='function')
def redis():
    rds_list = [rdstore.get_redis(n) for n in ['web-cache', 'couch-cache']]
    yield rds_list
    for rds in rds_list:
        rds.flushall()


@yield_fixture
def app(sqlstore, redis):
    app = create_app(TestingConfig())
    with app.app_context():
        yield app


@yield_fixture(scope='function')
def client(app):
    with app.test_client() as client:
        yield TestingClient(client)


@fixture
def user(sqlstore, redis):
    return Account.add(
        'user@guihua.dev', passwd_hash='foobar', salt='barfoo', name='user',
        reg_type=ACCOUNT_REG_TYPE.EMAIL)


@fixture
def identity(sqlstore, redis, user):
    identity = Identity.get_by_ricn('13112319920611251X')
    if not identity:
        identity = Identity.save(user.id_, '李延宗', '13112319920611251X')
        user.add_alias('13800138001', ACCOUNT_REG_TYPE.MOBILE)
    return identity


@fixture
def bankcard(sqlstore, redis, user):
    bankcards = BankCardManager(user.id_)
    with patch('core.models.profile.bankcard.DEBUG', True):
        return bankcards.create_or_update(
            mobile_phone='13800138000',
            card_number='6222000000000009',
            bank_id='4',  # 建设银行
            city_id='110100',  # 朝阳
            province_id='110000',  # 北京
            local_bank_name='西夏支行',
            is_default=True)


@fixture
def oauth_client(sqlstore, redis):
    return OAuthClient.add(
        name='Testing Client',
        allowed_grant_types=['password'],
        allowed_response_types=['token'],
        allowed_scopes=OAuthScope.__members__.values())


@fixture
def oauth_token(oauth_client, user):
    return OAuthToken.add(
        client_pk=oauth_client.id_,
        user_id=user.id_,
        scopes=[s.value for s in oauth_client.allowed_scopes],
        access_token='access',
        refresh_token='refresh',
        expires_in=3600)


@fixture
def sxb_product(sqlstore, redis, app):
    vendor = Vendor.get_by_name(Provider.sxb)
    if vendor is None:
        vendor = Vendor.add(Provider.sxb.value, 'sxb')
    product = Product.get_by_remote_id(vendor.id_, ProductConsts.SXB_VENDOR_PRODUCT_ID[0])
    if product is None:
        def add_product(product_info):
            start_sell_date, end_sell_date = check_available_for_product(product_info)
            Product.add_or_update(
                vendor.id_, product_info.product_id, product_info.name, product_info.quota,
                product_info.total_quota, product_info.today_quota, product_info.total_amount,
                product_info.total_buy_amount, product_info.min_redeem_amount,
                product_info.max_redeem_amount, product_info.day_redeem_amount,
                product_info.add_year_rate, product_info.remark, Product.Type.unlimited,
                product_info.min_amount, product_info.max_amount, product_info.return_rate_type,
                product_info.return_rate, product_info.effect_day_type, product_info.effect_day,
                product_info.effect_day_unit, product_info.is_redeem, start_sell_date,
                end_sell_date
            )
        for i in range(len(ProductConsts.SXB_PRODUCT_INFO)):
            product_info = ProductConsts.SXB_PRODUCT_INFO[ProductConsts.SXB_VENDOR_PRODUCT_ID[i]]
            add_product(Obj(product_info))
        sxb_products = Product.get_products_by_vendor_id(vendor.id_)
        for p in sxb_products:
            if p.is_taken_down:
                p.go_on_sale()
            if p.remote_id == ProductConsts.SXB_VENDOR_PRODUCT_ID[0]:
                product = p
    return product


@fixture
def xm_product(sqlstore, redis):
    vendor = Vendor.get_by_name(Provider.xm)
    if vendor is None:
        vendor = Vendor.add(Provider.xm.value, 'xm')
    product = XMProduct.get(ProductConsts.XINMI_PRODUCT_ID)
    if product is None:
        def add_product(product):
            start_sell_date, end_sell_date = check_available_for_product(product)
            Product.add_or_update(
                vendor.id_, product.product_id, product.name, float(product.quota),
                float(product.total_amount), float(product.total_amount),
                float(product.total_amount), 0,
                0, 0, 0, 0, product.remark, Product.Type.classic, product.min_amount,
                product.max_amount, 1, product.return_rate, 1, 1, 1,
                Product.RedeemType.auto.value, start_sell_date, end_sell_date,
                product.expire_period, product.expire_period_unit
            )
        add_product(Obj(ProductConsts.XINMI_PRODUCT_INFO))
        xm_products = Product.get_products_by_vendor_id(vendor.id_)
        for p in xm_products:
            if p.is_taken_down:
                p.go_on_sale()
        product = XMProduct.add(ProductConsts.XINMI_PRODUCT_INFO)
    return product


class TestingConfig(object):
    """测试环境下覆盖默认的配置."""

    RATELIMIT_ENABLED = False


class TestingClient(object):
    """Werkzeug Testing Client 的 Wrapper.

    为更方便地测试 API 而生:

    - 自动将请求响应包装成 JSON
    - 自动设置 Content Type 等 HTTP Header
    - 提供 ``load_token`` 方法快速加载 Bearer Token
    - 目前支持 ``get``, ``put``, ``post`` 三种方法, 可随时增加更多
    """

    def __init__(self, client):
        self.client = client
        self._bearer_token = None
        # Vendor.add(Provider.sxb.value, 'sxb')
        # Vendor.add(Provider.xm.value, 'xm')
        # Vendor.add(Provider.zw.value, 'zw')

    def __getattr__(self, name):
        return getattr(self.client, name)

    def _wraps(self, data, args, headers):
        data = json.dumps(data)
        args = dict(args or {})

        headers = dict(headers or {})
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Content-Length', len(data))
        if self._bearer_token:
            headers['Authorization'] = 'Bearer %s' % self._bearer_token

        return data, headers

    def load_token(self, token):
        self._bearer_token = token.access_token

    def drop_token(self):
        self._bearer_token = None

    def get(self, url, args=None, headers=None):
        _, headers = self._wraps(None, args, headers)
        r = self.client.get(url, headers=headers)
        return TestingResponse(r)

    def put(self, url, data, args=None, headers=None):
        data, headers = self._wraps(data, args, headers)
        r = self.client.put(url, headers=headers, data=data)
        return TestingResponse(r)

    def post(self, url, data, args=None, headers=None):
        data, headers = self._wraps(data, args, headers)
        r = self.client.post(url, headers=headers, data=data)
        return TestingResponse(r)


class TestingResponse(object):
    """Werkzeug Testing Client 所返回 Response 的 Wrapper.

    为将 ``data`` 属性替换成 JSON 解析过的字典.
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.wrapped, name)

    @property
    def data(self):
        return json.loads(self.wrapped.data)
