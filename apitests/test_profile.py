# coding: utf-8

from __future__ import absolute_import, unicode_literals

from datetime import datetime

from pytest import fixture
from mock import patch

from core.models.profile.bankcard import BankCard


@fixture
def profile_bankcard(sqlstore, couchstore, redis):
    with patch('core.models.profile.bankcard.DEBUG', True):
        return BankCard.add('1', '13800138000', '6222980000000002', '1',
                            '440113', '440000', '大望路支行', True)


testing_urls = {
    'mine': '/api/v1/profile/mine',
    'bankcards_zw': '/api/v1/profile/bankcards?partner=zw',
    'bankcards_zs': '/api/v1/profile/bankcards?partner=zs',
    'bind_identity': '/api/v1/profile/identity',
    'bind_mobile': '/api/v1/profile/mobile',
    'bind_mobile_verify': '/api/v1/profile/mobile/verify',
}


def test_profile_mine(client, oauth_token):
    client.load_token(oauth_token)

    r = client.get(testing_urls['mine'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'] == {
        'coupon_count': 0,
        'red_packets': 0.0,
        'has_identity': False,
        'has_mobile_phone': False,
        'has_yixin_account': False,
        'has_zw_account': False,
        'has_xm_account': False,
        'has_sxb_account': False,
        'is_old_user_of_yrd': False,
        'masked_person_name': '',
        'user': {
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'screen_name': 'user@guihua.dev',
            'uid': '1',
        },
    }


def test_profile_bankcards_zs(client, oauth_token, profile_bankcard):
    client.load_token(oauth_token)

    r = client.get(testing_urls['bankcards_zs'])
    assert r.status_code == 200
    assert r.data['success'] is True
    if r.data['data']:
        assert r.data['data'][0] == {
            'amount_limit': 50000,
            'bank': {
                'icon_url': {
                    'hdpi':
                        'https://dn-guihua-static.qbox.me/img/logo/banks/1@2x.png',
                    'mdpi':
                        'https://dn-guihua-static.qbox.me/img/logo/banks/1.png',
                },
                'name': '\u5de5\u5546\u94f6\u884c',
                'telephone': '95588',
                'uid': '1'
            },
            'card_number': '62****0002',  # 6222980000000002
            'is_default': True,
            'is_bound_in_wallet': False,
            'local_bank_name': '\u5927\u671b\u8def\u652f\u884c',
            'mobile_phone': '138****8000',  # 13800138000
            'province_id': '440000',
            'uid': '1'
        }


def test_profile_bankcards_zw(client, oauth_token, profile_bankcard):
    client.load_token(oauth_token)

    r = client.get(testing_urls['bankcards_zw'])
    assert r.status_code == 200
    assert r.data['success'] is True
    assert r.data['data'][0] == {
        'amount_limit': 50000,
        'bank': {
            'icon_url': {
                'hdpi':
                    'https://dn-guihua-static.qbox.me/img/logo/banks/1@2x.png',
                'mdpi':
                    'https://dn-guihua-static.qbox.me/img/logo/banks/1.png',
            },
            'name': '\u5de5\u5546\u94f6\u884c',
            'telephone': '95588',
            'uid': '1'
        },
        'card_number': '62****0002',  # 6222980000000002
        'is_default': True,
        'is_bound_in_wallet': False,
        'local_bank_name': '\u5927\u671b\u8def\u652f\u884c',
        'mobile_phone': '138****8000',  # 13800138000
        'province_id': '440000',
        'uid': '1'
    }


def test_bind_identity(client, oauth_token):
    client.load_token(oauth_token)

    r = client.post(testing_urls['bind_identity'], data={
        'person_name': 'Test',
        'person_ricn': '230602199104172536'}
    )
    assert r.status_code == 400
    assert r.data == {
        'messages': {'person_name': ['请输入正确的姓名']},
        'success': False
    }

    r = client.post(testing_urls['bind_identity'], data={
        'person_name': '赵四',
        'person_ricn': '123456'}
    )
    assert r.status_code == 400
    assert r.data == {
        'messages': {'person_ricn': ['该身份证号无效，请修改后重试']},
        'success': False
    }

    r = client.post(testing_urls['bind_identity'], data={
        'person_name': '赵四',
        'person_ricn': '230602199104172536'
    })
    # assert r.status_code == 200
    assert r.data == {
        'success': True,
        'data': {
            'person_name': '赵四',
            'person_ricn': '230602199104172536'
        }
    }


def test_bind_mobile(client, oauth_token):
    client.load_token(oauth_token)

    r = client.post(testing_urls['bind_mobile'], data={
        'mobile_phone': '123456'
    })
    assert r.status_code == 400
    assert r.data == {
        'messages': {'mobile_phone': ['该手机号无效，请修改后重试']},
        'success': False,
    }

    r = client.post(testing_urls['bind_mobile'], data={
        'mobile_phone': '18000000010',
    })
    assert r.status_code == 200
    assert r.data == {
        'success': True,
        'data': {
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'screen_name': 'user@guihua.dev',
            'uid': '1',
        },
    }
