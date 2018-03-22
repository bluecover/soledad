# -*- coding: utf-8 -*-

import uuid
import decimal
from datetime import datetime

from pytest import raises
from core.models.hoard.order import HoardOrder, OrderStatus
from core.models.hoard import YixinAccount, YixinService
from core.models.hoard.errors import (
    NotFoundError, UnboundAccountError, OutOfRangeError)

from .framework import BaseTestCase


class HoardOrderTest(BaseTestCase):

    local_user_info = [
        {'mobile': '13800000000'},
        {'mobile': '13900000000'},
    ]

    def setUp(self):
        super(HoardOrderTest, self).setUp()
        self.local_account = self.add_account(**self.local_user_info[0])
        self.another_local_account = self.add_account(**self.local_user_info[1])
        self.add_identity(self.local_account.id_, u'张三', '370281197811137612')
        self.add_identity(
            self.another_local_account.id_, u'李四', '370722197812222517')

        self.yixin_service = YixinService.add(self)
        self.fin_order_id = uuid.uuid4().hex
        self.another_fin_order_id = uuid.uuid4().hex

    def test_create_with_invalid_service(self):
        fake_id = uuid.uuid4().hex
        with raises(NotFoundError) as error:
            HoardOrder.add(fake_id, self.local_account.id,
                           decimal.Decimal('10000.0'), uuid.uuid4().hex)
        assert error.value.args[0] == fake_id
        assert error.value.args[1].__name__ == 'YixinService'

    def test_create_with_invalid_account(self):
        with raises(NotFoundError) as error:
            HoardOrder.add(self.yixin_service.uuid.hex, -1,
                           decimal.Decimal('10000.0'), uuid.uuid4().hex)
        assert error.value.args[0] == -1
        assert error.value.args[1].__name__ == 'Account'

    def test_create_with_unbound_account(self):
        with raises(UnboundAccountError) as error:
            HoardOrder.add(self.yixin_service.uuid.hex, self.local_account.id,
                           decimal.Decimal('10000.0'), uuid.uuid4().hex)
        assert error.value.args[0] == self.local_account.id

    def test_create(self):
        YixinAccount.bind(self.local_account.id, 'p2p_account', 'p2p_token')
        order = HoardOrder.add(
            self.yixin_service.uuid.hex, self.local_account.id,
            decimal.Decimal('10000.12'), uuid.uuid4().hex)
        assert order
        assert not order.is_success
        assert order.is_owner(self.local_account)
        assert order.order_amount == decimal.Decimal('10000.12')

    def test_paid(self):
        YixinAccount.bind(self.local_account.id, 'p2p_account', 'p2p_token')
        YixinAccount.bind(
            self.another_local_account.id, 'p2p_account_1', 'p2p_token_1')

        order_a = HoardOrder.add(
            self.yixin_service.uuid.hex, self.local_account.id,
            decimal.Decimal('12000.0'), self.fin_order_id)
        order_b = HoardOrder.add(
            self.yixin_service.uuid.hex, self.another_local_account.id,
            decimal.Decimal('24000.12'), self.another_fin_order_id)

        assert not order_a.is_success
        assert not order_b.is_success

        order_a.mark_as_paid('102')
        assert order_a.is_success
        assert order_a.order_id == '102'
        assert not order_b.is_success

        order_a = HoardOrder.get(order_a.id_)
        order_b = HoardOrder.get(order_b.id_)
        assert order_a.is_success
        assert order_a.order_id == '102'
        assert not order_b.is_success

        order_b.mark_as_paid('101')
        assert order_b.is_success
        assert order_b.order_id == '101'

    def test_confirmed(self):
        YixinAccount.bind(self.local_account.id, 'p2p_account', 'p2p_token')
        order = HoardOrder.add(
            self.yixin_service.uuid.hex, self.local_account.id,
            decimal.Decimal('12000.0'), self.fin_order_id)
        assert not order.is_success

        order.mark_as_paid('101')
        assert order.is_success
        assert order.status is not OrderStatus.confirmed

        order.mark_as_confirmed()
        assert order.is_success
        assert order.status is OrderStatus.confirmed

    def test_amount_out_of_range(self):
        amount_range = (decimal.Decimal('5000'), decimal.Decimal('50000'))

        YixinAccount.bind(self.local_account.id, 'p2p_account', 'p2p_token')

        with raises(OutOfRangeError) as error:
            HoardOrder.add(
                self.yixin_service.uuid.hex, self.local_account.id,
                decimal.Decimal('-1'), uuid.uuid4().hex)
        assert error.value.args[0] == decimal.Decimal('-1')
        assert error.value.args[1] == amount_range

        with raises(OutOfRangeError) as error:
            HoardOrder.add(
                self.yixin_service.uuid.hex, self.local_account.id,
                decimal.Decimal('4999.99'), uuid.uuid4().hex)
        assert error.value.args[0] == decimal.Decimal('4999.99')
        assert error.value.args[1] == amount_range

        with raises(OutOfRangeError) as error:
            HoardOrder.add(
                self.yixin_service.uuid.hex, self.local_account.id,
                decimal.Decimal('50000.01'), uuid.uuid4().hex)
        assert error.value.args[0] == decimal.Decimal('50000.01')
        assert error.value.args[1] == amount_range

    def test_get_multi_by_date(self):
        YixinAccount.bind(self.local_account.id, 'p2p_account', 'p2p_token')
        YixinAccount.bind(
            self.another_local_account.id, 'p2p_account_1', 'p2p_token_1')

        order_a = HoardOrder.add(
            self.yixin_service.uuid.hex, self.local_account.id,
            decimal.Decimal('12000.0'), uuid.uuid4().hex)
        order_b = HoardOrder.add(
            self.yixin_service.uuid.hex, self.another_local_account.id,
            decimal.Decimal('24000.12'), uuid.uuid4().hex)

        start = datetime.now().strftime('%Y-%m')
        os = HoardOrder.gets_by_month(start)

        assert len(os) == 2
        assert order_a.id_ in [o.id_ for o in os]
        assert order_b.id_ in [o.id_ for o in os]

    def typed(self):
        """A mock method."""
        return {
            'id': uuid.uuid4(),
            'invest_min_amount': decimal.Decimal('5000.00'),
            'invest_max_amount': decimal.Decimal('50000.00'),
        }
