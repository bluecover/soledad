# -*- coding: utf-8 -*-

import uuid
import decimal

import arrow

from core.models.hoard import YixinService
from .framework import BaseTestCase


class HoardServiceTest(BaseTestCase):

    local_user_info = ('foo@guihua.dev', 'foobar', 'Foo')

    def setUp(self):
        super(HoardServiceTest, self).setUp()
        self.local_account = self.add_account(*self.local_user_info)
        self.service_info = ServiceInfoMock()
        self.uuid = 'aef266f6ba1d47639abb953394b0575b'

    def test_create_service(self):
        service = YixinService.get(self.uuid)
        assert service is None

        service = YixinService.add(self.service_info)
        assert service.uuid == uuid.UUID(self.uuid)
        assert service.expected_income == decimal.Decimal('5')

        service = YixinService.get(self.uuid)
        assert service.uuid == uuid.UUID(self.uuid)
        assert service.expected_income == decimal.Decimal('5')

        for name, value in ServiceInfoMock.typed_data.items():
            if name == 'id':
                name = 'uuid'
            assert getattr(service, name) == value

    def test_get_all(self):
        service = YixinService.add(self.service_info)
        service_list = YixinService.get_all()

        assert len(service_list) == 1
        for name, value in ServiceInfoMock.typed_data.items():
            if name == 'id':
                name = 'uuid'
            assert getattr(service, name) == value
            assert getattr(service_list[0], name) == value


class ServiceInfoMock(object):
    typed_data = {
        'amount': decimal.Decimal('300'),
        'begin_sale_time': arrow.get('2014-11-17T18:40:00+08:00'),
        'exist_amount': decimal.Decimal('0'),
        'expected_income': decimal.Decimal('5'),
        'for_new_user': False,
        'frozen_time': True,
        'id': uuid.UUID('aef266f6-ba1d-4763-9abb-953394b0575b'),
        'increment': decimal.Decimal('0.1'),
        'invest_max_amount': decimal.Decimal('50'),
        'invest_min_amount': decimal.Decimal('0.1'),
        'is_home_page': False,
        'keyword': None,
        'p2pservice_name': u'\u5b9c\u5b9a\u76c8V1411031',
        'p2pservice_no': u'1',
        'p2pservice_type': u'\u4e00\u4e2a\u6708\u671f',
        'product_id': u'20',
        'product_sub_id': uuid.UUID('6e8e26cb-cfa9-4e46-af87-222d6003b9c1'),
        'sale_status': 1.0,
        'server_time': arrow.get('2418-11-22T15:47:57.250000+08:00'),
        'service_sub_image_url': None,
    }

    def typed(self):
        return self.typed_data
