# coding: utf-8

from __future__ import absolute_import, unicode_literals

from mock import patch, Mock
from pytest import fixture
from pkg_resources import SetuptoolsVersion

from core.models.consts import Platform
from core.models.user.account import Account
from core.models.pusher import DeviceBinding, UserPushRecord
from core.models.notification import Notification


testing_urls = {
    'claim_device': '/api/v1/pusher/device/claim',
    'sleep_device': '/api/v1/pusher/device/sleep',
    'inform_push_received': '/api/v1/pusher/sensible_push/inform_received',
    'inform_push_clicked': '/api/v1/pusher/sensible_push/inform_clicked',
}


@fixture
def lucy_device_binding(user):
    lucy = user
    device_id = 'device_of_lucy'
    device_platform = Platform.android
    return DeviceBinding.create(lucy, device_id, device_platform, SetuptoolsVersion('1.0.1'))


@fixture
def lily_device_binding(sqlstore, redis):
    lily = Account.add(
        'lily@guihua.test', passwd_hash='lilypwd', salt='test', name='lily')
    device_id = 'device_of_lily'
    device_platform = Platform.android
    return DeviceBinding.create(lily, device_id, device_platform, SetuptoolsVersion('1.0.1'))


@fixture
def notification(user):
    fake_notice = Mock(spec=Notification)
    fake_notice.id_ = '100'
    fake_notice.user_id = user.id_
    return fake_notice


@fixture
def push_record(user, lucy_device_binding, notification):
    record = UserPushRecord.create(user, lucy_device_binding, notification)
    record.mark_as_pushed('20160126')
    return record


@patch('core.models.pusher.facade.jpush')
def test_claim_device(jpush, lily_device_binding, lucy_device_binding,
                      user, client, oauth_token):
    client.load_token(oauth_token)
    headers = {'User-Agent': 'Guihua/1.5.2 (Android)'}

    # 在Lily的设备上登录新的用户，将造成设备切换为Lucy(默认用户)
    r = client.post(testing_urls['claim_device'], headers=headers,
                    data={'device_id': lily_device_binding.device_id})
    assert r.status_code == 200
    assert r.data['success'] is True
    assert jpush.logoff_device.call_count == 1
    assert jpush.register_device.call_count == 1
    lucy_binding = DeviceBinding.get(lily_device_binding.id_)
    assert lucy_binding.user_id == user.id_

    # Lucy在自己的设备上再次登录
    r = client.post(testing_urls['claim_device'], headers=headers,
                    data={'device_id': lucy_device_binding.device_id})
    assert r.status_code == 200
    assert r.data['success'] is True
    assert jpush.logoff_device.call_count == 1
    assert jpush.register_device.call_count == 1

    # Lucy在自己的第二个设备上登录
    r = client.post(testing_urls['claim_device'], headers=headers,
                    data={'device_id': 'device2_of_lucy'})
    assert r.status_code == 200
    assert r.data['success'] is True
    assert jpush.register_device.call_count == 2


def test_sleep_device(lucy_device_binding, client, oauth_token):
    client.load_token(oauth_token)

    r = client.post(testing_urls['sleep_device'], data={
        'device_id': lucy_device_binding.device_id})

    assert r.status_code == 200
    assert r.data['success'] is True
    lucy_binding = DeviceBinding.get(lucy_device_binding.id_)
    assert lucy_binding.status is DeviceBinding.Status.inactive


def test_inform_received(lucy_device_binding, push_record, client, oauth_token):
    client.load_token(oauth_token)

    r = client.post(testing_urls['inform_push_received'], data={
        'device_id': push_record.device_id,
        'jpush_msg_id': '20160126'
    })
    assert r.status_code == 200
    assert r.data['success'] is True
    record = UserPushRecord.get_by_device_and_notification(
        push_record.device_id, push_record.notification_id)
    assert record.status is UserPushRecord.Status.received


def test_inform_clicked(lucy_device_binding, push_record, client, oauth_token):
    client.load_token(oauth_token)

    r = client.post(testing_urls['inform_push_clicked'], data={
        'device_id': push_record.device_id,
        'jpush_msg_id': '20160126'
    })
    assert r.status_code == 200
    assert r.data['success'] is True
    record = UserPushRecord.get_by_device_and_notification(
        push_record.device_id, push_record.notification_id)
    assert record.status is UserPushRecord.Status.clicked
