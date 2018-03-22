# coding: utf-8

from __future__ import absolute_import, unicode_literals
from .utils import get_testurl, get_date
from .conf_consts import ProductConsts
from pytest import fixture
from core.models.hoard.xinmi.account import XMAccount


testing_urls = {
    'xm_auth': 'savings/xm/auth',
    'xm_order': 'savings/xm/order',
    'xm_order_verify': 'savings/xm/order/{0}/verify',
    'xm_order_contract': 'savings/xm/order/{0}/contract'
}


@fixture
def xm_user(sqlstore, redis, user):
    xmuser = XMAccount.get_by_local(user.id_)
    if not xmuser:
        return XMAccount.bind(user.id_, ProductConsts.XINMI_TOKEN)
    return xmuser


def test_savings_xm_auth_without_identity(client, oauth_token):
    client.load_token(oauth_token)

    r = client.post(get_testurl(testing_urls['xm_auth']), data={})
    assert r.status_code == 403
    assert r.data['success'] is False


def test_savings_xm_auth_without_binding_xm(client, oauth_token, identity):
    """
    临时注释
    client.load_token(oauth_token)
    #  没有绑定xm账户
    r = client.post(get_testurl(testing_urls['xm_auth']), data={})
    assert r.status_code == 201
    assert r.data == {
        'data': None,
        'success': True
    }
    """
    pass


def test_savings_xm_auth(client, oauth_token, identity, xm_user):
    r = client.post(get_testurl(testing_urls['xm_auth']), data={})
    assert r.status_code == 401
    assert r.data['success'] is False

    client.load_token(oauth_token)
    #  已经绑定xm账户
    r = client.post(get_testurl(testing_urls['xm_auth']), data={})
    assert r.status_code == 200
    assert r.data == {
        'data': None,
        'success': True
    }


def test_savings_xm_order(client, oauth_token, bankcard, identity, user, xm_user,
                          xm_product):
    """
    临时注释
    :param client:
    :param oauth_token:
    :param bankcard:
    :param identity:
    :param user:
    :param xm_user:
    :param xm_product:
    :return:

    r = client.post(get_testurl(testing_urls['xm_order']), data={
        'amount': 0,
        'bankcard_id': bankcard.id_,
        'product_id': xm_product.unique_product_id,
        'due_date': get_date()
    })
    assert r.status_code == 401
    assert r.data['success'] is False

    # TODO 正常购买 201
    client.load_token(oauth_token)
    r = client.post(get_testurl(testing_urls['xm_order']), data={
        'amount': 1000,
        'bankcard_id': bankcard.id_,
        'product_id': xm_product.unique_product_id,
        'due_date': get_date()
    })
    assert r.status_code == 201
    assert r.data['success'] is True
    assert r.data['data']['amount'] == 1000.0
    assert r.data['data']['expected_profit'] == 20.96
    assert r.data['data']['bankcard'] == XINMI_RESPONSE_BANKCARD
    assert r.data['data']['product'] == XINMI_RESPONSE_PRODUCT
    # assert r.data['data']['created_at'] == get_create_at_time()
    assert r.data['data']['user']['uid'] == '1'
    assert r.data['data']['user']['screen_name'] == u'138****8001'
    assert r.data['data']['profit_annual_rate'] == 8.5
    assert r.data['data']['coupon'] is None
    assert r.data['data']['status'] == 'unpaid'
    assert r.data['data']['uid'] == '1'
    # assert r.data['data']['profit_period'] == {
    #     u'created_at': get_date(),
    #     u'unit': u'day',
    #     u'value': 90
    # }"""
    pass


def test_savings_xm_order_without_identity(client, oauth_token, bankcard, user, xm_user,
                                           xm_product):
    client.load_token(oauth_token)
    r = client.post(get_testurl(testing_urls['xm_order']), data={
        'amount': 0,
        'bankcard_id': bankcard.id_,
        'product_id': xm_product.unique_product_id,
        'due_date': get_date()
    })
    assert r.status_code == 403
    assert r.data == {
        'messages': {'_': ['尚未绑定身份信息或身份信息无效']},
        'success': False
    }


def test_savings_xm_order_without_binding_xm(client, oauth_token, bankcard, user, identity,
                                             xm_product):
    client.load_token(oauth_token)
    # 没有绑定xm账户
    r = client.post(get_testurl(testing_urls['xm_order']), data={
        'amount': 1000,
        'bankcard_id': bankcard.id_,
        'product_id': xm_product.unique_product_id,
        'due_date': get_date()
    })
    assert r.status_code == 403
    assert r.data == {
        'messages': {'_': ['未绑定新米账户']},
        'success': False
    }


def test_savings_xm_order_with_wrong_amount(client, oauth_token, bankcard, identity, user, xm_user,
                                            xm_product):
    client.load_token(oauth_token)
    # 错误的金额
    r = client.post(get_testurl(testing_urls['xm_order']), data={
        'amount': -1000,
        'bankcard_id': bankcard.id_,
        'product_id': xm_product.unique_product_id,
        'due_date': get_date()
    })
    assert r.status_code == 403
    assert r.data == {
        'messages': {'_': ['订单金额不在允许的范围内']},
        'success': False
    }


def test_savings_xm_order_with_wrong_bankcard(client, oauth_token, xm_product):
    client.load_token(oauth_token)
    # 错误的银行卡id
    r = client.post(get_testurl(testing_urls['xm_order']), data={
        'amount': 1000,
        'bankcard_id': '10',
        'product_id': xm_product.unique_product_id,
        'due_date': get_date()
    })
    assert r.status_code == 400
    assert r.data == {
        'messages': {'_': ['该银行卡不存在，请重新添加银行卡']},
        'success': False
    }


def test_savings_xm_order_with_wrong_product(client, oauth_token, bankcard):
    client.load_token(oauth_token)
    # 错误的产品id
    r = client.post(get_testurl(testing_urls['xm_order']), data={
        'amount': 1000,
        'bankcard_id': bankcard.id_,
        'product_id': 1,
        'due_date': get_date()
    })
    assert r.status_code == 400
    assert r.data['success'] is False
    assert r.data == {
        'messages': {'_': ['该产品不存在']},
        'success': False
    }


def test_savings_xm_order_verify(client, oauth_token, identity, user, xm_user):
    # 未登录 401
    r = client.post(get_testurl(testing_urls['xm_order_verify']).format('10001'), data={})
    assert r.status_code == 401
    assert r.data['success'] is False
    # TODO 正常情况


def test_savings_xm_order_verify_with_wrong_order(client, oauth_token):
    client.load_token(oauth_token)
    r = client.post(get_testurl(testing_urls['xm_order_verify']).format('10001'), data={
        'sms_code': '314159',
    })
    assert r.status_code == 404
    assert r.data == {
        'messages': {u'_': ['该订单不存在']},
        'success': False
    }


def test_savings_xm_order_verify_with_not_mine_order():
    pass  # TODO


def test_savings_xm_order_contract(client, oauth_token):
    # 未登录 401
    r = client.get(get_testurl(testing_urls['xm_order_contract']).format('10001'))
    assert r.status_code == 401
    assert r.data['success'] is False
    # TODO 正常获取


def test_savings_xm_order_contract_with_wrong_order(client, oauth_token):
    client.load_token(oauth_token)
    # 错误的order_id
    r = client.get(get_testurl(testing_urls['xm_order_contract']).format('10001'))
    assert r.status_code == 404
    assert r.data['success'] is False
    assert r.data is not None


def test_savings_xm_order_contract_with_not_mine_order():
    pass  # TODO
