# coding: utf-8

from __future__ import absolute_import, unicode_literals
from .utils import get_testurl_v2, Obj, get_date
from .conf_consts import ProductConsts
from pytest import fixture
from core.models.hoard.xinmi.account import XMAccount
import mock
from core.models.hoarder.vendor import Vendor, Provider
from core.models.hoarder.product import Product as SXBProduct
from core.models.hoarder.account import Account as SXBAccount

testing_urls = {
    'recommend': 'products/recommend',
    'all': 'products/all',
    'order': 'savings/order',
    'order_verify': 'savings/order/{0}/verify'
}


@fixture
def xm_user(sqlstore, redis, user):
    xmuser = XMAccount.get_by_local(user.id_)
    if not xmuser:
        return XMAccount.bind(user.id_, ProductConsts.XINMI_TOKEN)
    return xmuser


@fixture
def sxb_user(sqlstore, redis, user):
    vendor = Vendor.get_by_name(Provider.sxb)
    sxbuser = SXBAccount.get_by_local(vendor.id_, user.id_)
    if not sxbuser:
        return SXBAccount.bind(vendor.id_, user.id_, u'1234abcd')
    return sxbuser


def product_schema_assert(product_schema, product_id):
    assert product_schema['uid'] == product_id
    assert 'name' in product_schema, product_schema
    assert 'title' in product_schema, product_schema
    assert 'activity_title' in product_schema, product_schema
    assert 'activity_introduction' in product_schema, product_schema
    assert 'annual_rate' in product_schema, product_schema
    assert 'max_amount' in product_schema, product_schema
    assert 'min_amount' in product_schema, product_schema
    assert 'tags' in product_schema, product_schema
    assert 'period' in product_schema, product_schema
    assert 'annotations' in product_schema, product_schema
    assert 'display_status' in product_schema, product_schema
    assert 'start_date' in product_schema, product_schema


def test_savings_import_product(xm_product, sxb_product):
    pass


def test_savings_recommend_product_with_new_comer(client, oauth_client, oauth_token,
                                                  sxb_product):
    # 推荐逻辑:未登录推荐新手标;新用户(未购买新手标), 推荐新手标, 随心攒, 365天, 随心攒
    # 未登录,访问路由,查找推荐产品
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}
    r = client.get(get_testurl_v2(testing_urls['recommend']), headers=headers)
    # 对比推荐产品, 必须为新手标
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['wallet'] != []
    wallet = r.data['data']['wallet'][0]
    product_schema_assert(wallet, str(sxb_product.id_))

    # 登录,访问路由,查找推荐产品
    client.load_token(oauth_token)
    r = client.get(get_testurl_v2(testing_urls['recommend']), headers=headers)
    # 对比推荐产品,必须为新手标(新手标会用随心攒包装)
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['wallet'] != []
    wallet = r.data['data']['wallet'][0]
    assert 'withdraw_rule' in wallet
    product_schema_assert(wallet, str(sxb_product.id_))


@mock.patch('core.models.hoarder.order.HoarderOrder.get_order_amount_by_user')
@mock.patch('core.models.hoard.xinmi.XMOrder.get_total_orders')
@mock.patch('core.models.hoard.manager.SavingsManager.has_bought_newcomer_product')
def test_savings_recommend_product_with_old_user(mock_get_order_amount_by_user,
                                                 mock_get_total_orders,
                                                 mock_has_bought_newcomer_product,
                                                 client, oauth_client, oauth_token):
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}
    # 购买新手标
    # 登录,访问路由,查找推荐产品
    client.load_token(oauth_token)
    mock_get_order_amount_by_user.return_value = 1
    mock_get_total_orders.return_value = 1
    mock_has_bought_newcomer_product.return_value = True
    # 访问路由,查找推荐产品
    r = client.get(get_testurl_v2(testing_urls['recommend']), headers=headers)
    # 对比推荐产品,必须为随心攒
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['wallet'] != []
    wallet = r.data['data']['wallet'][0]
    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_products = SXBProduct.get_products_by_vendor_id(vendor.id_)
    assert 'withdraw_rule' in wallet
    product_schema_assert(wallet, str(sxb_products[1].id_))


@mock.patch('core.models.hoarder.order.HoarderOrder.get_order_amount_by_user')
@mock.patch('core.models.hoard.xinmi.XMOrder.get_total_orders')
@mock.patch('core.models.hoard.manager.SavingsManager.has_bought_newcomer_product')
@mock.patch('jupiter.views.api.v2.strategy.check_is_inhouse')
def test_savings_recommend_product_with_sold_out(mock_get_order_amount_by_user,
                                                 mock_get_total_orders,
                                                 mock_has_bought_newcomer_product,
                                                 mock_check_is_inhouse,
                                                 client, oauth_token, oauth_client, xm_product):
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}

    client.load_token(oauth_token)
    # 买过新手标,随心攒售罄,环境准备
    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_products = SXBProduct.get_products_by_vendor_id(vendor.id_)
    for sxb in sxb_products:
        sxb.go_off_sale()
    mock_check_is_inhouse.return_value = True
    mock_get_order_amount_by_user.return_value = 1
    mock_get_total_orders.return_value = 1
    mock_has_bought_newcomer_product.return_value = True

    # 访问路由,查找推荐产品
    r = client.get(get_testurl_v2(testing_urls['recommend']), headers=headers)
    # 对比推荐产品,必须为365天
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['hoarder'] != []
    hoarder = r.data['data']['hoarder'][0]
    product_schema_assert(hoarder, str(xm_product.product_id))


@mock.patch('core.models.hoarder.order.HoarderOrder.get_order_amount_by_user')
@mock.patch('core.models.hoard.xinmi.XMOrder.get_total_orders')
@mock.patch('core.models.hoard.manager.SavingsManager.has_bought_newcomer_product')
def test_savings_recommend_product_with_all_sold_out(mock_get_order_amount_by_user,
                                                     mock_get_total_orders,
                                                     mock_has_bought_newcomer_product,
                                                     client, oauth_token, oauth_client):
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}

    client.load_token(oauth_token)
    # 买过新手标,随心攒售罄,365天售罄,环境准备
    mock_get_order_amount_by_user.return_value = 1
    mock_get_total_orders.return_value = 1
    mock_has_bought_newcomer_product.return_value = True
    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_products = SXBProduct.get_products_by_vendor_id(vendor.id_)
    for sxb in sxb_products:
        sxb.go_off_sale()
    # 访问路由,查找推荐产品
    r = client.get(get_testurl_v2(testing_urls['recommend']), headers=headers)
    # 对比推荐产品,必须为随心攒
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data']['wallet'] != []
    wallet = r.data['data']['wallet'][0]
    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_products = SXBProduct.get_products_by_vendor_id(vendor.id_)
    product_schema_assert(wallet, str(sxb_products[1].id_))


def test_savings_products_all(client, oauth_token, oauth_client, xm_product):
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}
    r = client.get(get_testurl_v2(testing_urls['all']), headers=headers)
    assert r.status_code == 200
    assert r.data['success'] is True

    assert r.data['data']['wallet'] != []
    wallet = r.data['data']['wallet']
    vendor = Vendor.get_by_name(Provider.sxb)
    sxb_products = SXBProduct.get_products_by_vendor_id(vendor.id_)
    for i in range(len(sxb_products)):
        product_schema_assert(wallet[i], str(sxb_products[i].id_))
    fund = wallet[2]
    assert 'name' in fund
    assert 'title' in fund
    assert 'activity_title' in fund
    assert 'activity_introduction' in fund
    assert 'annual_rate' in fund
    assert 'tags' in fund
    assert 'display_status' in fund

    # assert r.data['data']['hoarder'] != []
    # hoarder = r.data['data']['hoarder'][0]
    # product_schema_assert(hoarder, str(xm_product.product_id))


@mock.patch('core.models.hoard.xinmi.transaction.xinmi.order_apply')
def test_savings_xm_order_without_binding_v2(mock_order_apply, client, oauth_token, bankcard,
                                             identity, user, xm_product):
    mock_order_apply.return_value = Obj(ProductConsts.XINMI_RESPONSE_ORDER_APPLY)

    client.load_token(oauth_token)
    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': 1000,
        'bankcard_id': bankcard.id_,
        'product_id': xm_product.unique_product_id,
        'due_date': get_date(),
        'vendor': 'xm'
    })
    assert r.status_code == 201
    assert r.data['success'] is True
    assert r.data['data']['amount'] == 1000.0
    assert r.data['data']['expected_profit'] == 20.96
    assert r.data['data']['bankcard'] == ProductConsts.XINMI_RESPONSE_BANKCARD
    assert r.data['data']['product'] == ProductConsts.XINMI_RESPONSE_PRODUCT
    assert r.data['data']['user']['uid'] == '1'
    assert r.data['data']['user']['screen_name'] == u'138****8001'
    assert r.data['data']['profit_annual_rate'] == 8.5
    assert r.data['data']['coupon'] is None
    assert r.data['data']['status'] == 'unpaid'
    assert r.data['data']['uid'] == '1'


@mock.patch('core.models.hoard.xinmi.transaction.xinmi.order_apply')
def test_savings_xm_order_v2(mock_order_apply, client, oauth_token, bankcard, identity, user,
                             xm_user, xm_product):
    response = ProductConsts.XINMI_RESPONSE_ORDER_APPLY
    response['pay_code'] = u'Ptest1236921'
    mock_order_apply.return_value = Obj(response)
    client.load_token(oauth_token)
    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': 1000,
        'bankcard_id': bankcard.id_,
        'product_id': xm_product.unique_product_id,
        'due_date': get_date(),
        'vendor': 'xm'
    })
    assert r.status_code == 201
    assert r.data['success'] is True
    assert r.data['data']['amount'] == 1000.0
    assert r.data['data']['expected_profit'] == 20.96
    assert r.data['data']['bankcard'] == ProductConsts.XINMI_RESPONSE_BANKCARD
    assert r.data['data']['product'] == ProductConsts.XINMI_RESPONSE_PRODUCT
    assert r.data['data']['user']['uid'] == '1'
    assert r.data['data']['user']['screen_name'] == u'138****8001'
    assert r.data['data']['profit_annual_rate'] == 8.5
    assert r.data['data']['coupon'] is None
    assert r.data['data']['status'] == 'unpaid'
    assert r.data['data']['uid'] == '2'


@mock.patch('core.models.hoard.xinmi.transaction.xinmi.confirm_apply')
def test_savings_xm_verify_v2(mock_confirm_apply, client, oauth_token, bankcard, identity, user,
                              xm_user, xm_product):
    # 支付
    client.load_token(oauth_token)
    order_id = '2'
    mock_confirm_apply.return_value = Obj(ProductConsts.XINMI_RESPONSE_CONFIRM_APPLY)
    r = client.post(get_testurl_v2(testing_urls['order_verify']).format(order_id), data={
        'sms_code': '314159',
        'vendor': 'xm'
    })
    assert r.status_code == 201
    assert r.data['success'] is True
    assert r.data['data']['amount'] == 1000.0
    assert r.data['data']['expected_profit'] == 20.96
    # assert r.data['data']['bankcard'] == ProductConsts.XINMI_RESPONSE_BANKCARD
    assert r.data['data']['product'] == ProductConsts.XINMI_RESPONSE_PRODUCT
    assert r.data['data']['user']['uid'] == '1'
    assert r.data['data']['user']['screen_name'] == u'138****8001'
    assert r.data['data']['profit_annual_rate'] == 8.5
    assert r.data['data']['coupon'] is None
    assert r.data['data']['status'] == 'success'
    assert r.data['data']['uid'] == '2'


@mock.patch('core.models.hoarder.order.HoarderOrder.check_before_adding')
@mock.patch('core.models.hoarder.transactions.sxb.sxb.order_apply')
def test_savings_sxb_order_without_binding_v2(mock_order_apply, mock_check_before_adding,
                                              client, oauth_token, identity, user, bankcard,
                                              sxb_product):
    mock_order_apply.return_value = Obj(ProductConsts.SXB_RESPONSE_ORDER_APPLY)
    buy_amount = 1000.0

    client.load_token(oauth_token)
    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': buy_amount,
        'bankcard_id': bankcard.id_,
        'product_id': sxb_product.id_,
        'due_date': get_date(),
        'vendor': 'sxb'
    })

    assert r.status_code == 201, r.data
    assert r.data['success'] is True
    assert r.data['data']['status'] == u'unpaid'
    assert r.data['data']['status_text'] == u'未支付'
    assert r.data['data']['uid'] == '1000'


@mock.patch('core.models.hoarder.transactions.sxb.sxb.confirm_apply')
def test_savings_sxb_verify_v2(mock_confirm_apply, client, oauth_token, identity, user, bankcard,
                               sxb_product):
    mock_confirm_apply.return_value = Obj(ProductConsts.SXB_RESPONSE_CONFIRM_APPLY)

    # 支付
    buy_amount = 1000.0
    order_id = u'1000'
    client.load_token(oauth_token)
    r = client.post(get_testurl_v2(testing_urls['order_verify']).format(order_id), data={
        'sms_code': '314159',
        'vendor': 'sxb'
    })
    assert r.status_code == 201, r.data
    assert r.data['success'] is True
    assert r.data['data'] == {
        'amount': buy_amount,
        'annual_rate': 11.25,
        'expected_profit': 0.31,
        'status': u'success',
        'status_text': u'您已支付成功',
        'uid': order_id
    }


@mock.patch('core.models.hoarder.order.HoarderOrder.check_before_adding')
@mock.patch('core.models.hoarder.transactions.sxb.sxb.order_apply')
def test_savings_sxb_order_v2(mock_order_apply, mock_check_before_adding, client, oauth_token,
                              identity, user, sxb_user, bankcard, sxb_product):
    response = ProductConsts.SXB_RESPONSE_ORDER_APPLY
    response['pay_code'] = u'Ptest1231811'
    mock_order_apply.return_value = Obj(response)

    client.load_token(oauth_token)
    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': 1000.0,
        'bankcard_id': bankcard.id_,
        'product_id': sxb_product.id_,
        'due_date': get_date(),
        'vendor': 'sxb'
    })
    assert r.status_code == 201, r.data
    assert r.data['success'] is True
    assert r.data['data']['status'] == u'unpaid'
    assert r.data['data']['status_text'] == u'未支付'
    assert r.data['data']['uid'] == '1001'


def test_savings_order_with_bankcard_err(client, oauth_token, sxb_user, xm_user, xm_product,
                                         sxb_product):
    client.load_token(oauth_token)
    from jupiter.views.api.v2.products.errors import BankCardNotExistedError
    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': 1000.0,
        'bankcard_id': '1',
        'product_id': sxb_product.id_,
        'due_date': get_date(),
        'vendor': 'sxb'
    })
    assert r.status_code == 403
    assert r.data['success'] is False
    assert r.data['messages'] == {
        '_': [unicode(BankCardNotExistedError())]
    }

    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': 1000.0,
        'bankcard_id': '1',
        'product_id': xm_product.unique_product_id,
        'due_date': get_date(),
        'vendor': 'xm'
    })
    assert r.status_code == 403
    assert r.data['success'] is False
    assert r.data['messages'] == {
        '_': [unicode(BankCardNotExistedError())]
    }


def test_savings_order_with_product_err(client, oauth_token, bankcard, sxb_user, xm_user,
                                        xm_product, sxb_product):
    client.load_token(oauth_token)
    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': 1000.0,
        'bankcard_id': bankcard.id_,
        'product_id': '0',
        'due_date': get_date(),
        'vendor': 'sxb'
    })
    assert r.status_code == 403
    assert r.data['success'] is False
    from core.models.hoarder.errors import OffShelfError
    assert r.data['messages'] == {
        '_': [unicode(OffShelfError())]
    }

    r = client.post(get_testurl_v2(testing_urls['order']), data={
        'amount': 1000.0,
        'bankcard_id': bankcard.id_,
        'product_id': '0',
        'due_date': get_date(),
        'vendor': 'xm'
    })
    assert r.status_code == 403
    assert r.data['success'] is False
    from jupiter.views.api.v2.products.errors import XMProductNotExistedError
    assert r.data['messages'] == {
        '_': [unicode(XMProductNotExistedError())]
    }
