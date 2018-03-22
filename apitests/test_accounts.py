# coding: utf-8

from __future__ import absolute_import, unicode_literals

import datetime

test_url = {
    'reset_password': '/api/v1/accounts/reset_password',
    'reset_password_verify': '/api/v1/accounts/reset_password_verify',
    'reset_password_sms_verify': 'api/v1/accounts/reset_password_sms_verify'
    }


def test_register(client, oauth_client):
    url = '/api/v1/accounts/register'
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}
    wrong_headers = {'X-Client-ID': 'foo', 'X-Client-Secret': 'bar'}
    mobile_phone = '13800138000'

    # missing client id
    r = client.post(url, {'mobile_phone': mobile_phone})
    assert r.status_code == 401
    assert r.data == {'error': 'missing_token'}

    # wrong client id
    r = client.post(url, {'mobile_phone': mobile_phone}, headers=wrong_headers)
    assert r.status_code == 403
    assert r.data == {'error': 'invalid_token'}

    # missing mobile phone number
    r = client.post(url, {}, headers=headers)
    assert r.status_code == 400
    assert r.data['success'] is False
    assert r.data['messages']['mobile_phone'][0].startswith('Missing')

    # invalid mobile phone number
    r = client.post(url, {'mobile_phone': mobile_phone[:-1]}, headers=headers)
    assert r.status_code == 400
    assert r.data['success'] is False
    assert r.data['messages']['mobile_phone'][0] == '该手机号无效，请修改后重试'

    # success
    r = client.post(url, {'mobile_phone': mobile_phone}, headers=headers)
    assert r.status_code == 202
    assert r.data['success'] is True
    assert r.data['data']['uid']
    assert r.data['data']['screen_name'] == '138****8000'
    assert r.data['data']['created_at'] == unicode(datetime.date.today())


def test_reset_password_send_sms(client, oauth_client):
    headers = {'X-Client-ID': oauth_client.client_id,
               'X-Client-Secret': oauth_client.client_secret}
    mobile_phone = '15900000000'

    def register_account(mobile_phone, headers):
        url = '/api/v1/accounts/register'
        client.post(url, {'mobile_phone': mobile_phone}, headers=headers)

    # send msg successfully
    register_account(mobile_phone, headers)
    r = client.post(test_url['reset_password'], {'mobile_phone': mobile_phone}, headers=headers)
    assert r.status_code == 200
    assert r.data['success'] is True

    # invalid mobile phone number
    r = client.post(
            test_url['reset_password'], {'mobile_phone': mobile_phone[:-1]}, headers=headers)
    assert r.status_code == 400
    assert r.data['success'] is False
    assert r.data['messages']['mobile_phone'][0] == '该手机号无效，请修改后重试'
