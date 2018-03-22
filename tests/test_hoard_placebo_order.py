# coding: utf-8

from __future__ import absolute_import

import decimal
import datetime

from pytest import raises
from freezegun import freeze_time

from core.models.utils import round_half_up
from core.models.hoard.placebo import PlaceboProduct, PlaceboOrder, NotRunningError
from core.models.hoard.placebo.product import StrategyStorage
from core.models.hoard.errors import InvalidIdentityError
from core.models.hoard.zhiwang.errors import (
    InvalidProductError, OffShelfError, OutOfRangeError)
from .framework import BaseTestCase


class PlaceboOrderTestCase(BaseTestCase):

    def setUp(self):
        super(PlaceboOrderTestCase, self).setUp()
        self._original_strategy_storage = dict(PlaceboProduct.strategy_storage)

        @PlaceboProduct.strategy_storage.register(id_=1, name=u'白名单')
        def check_white_list(user_id):
            return user_id in self.white_list

        self.white_list = set()
        self.check_white_list = check_white_list

        self.user = self.add_account(mobile='13800138000')
        self.white_list.add(self.user.id_)
        self.product = PlaceboProduct.add(
            strategy=check_white_list,
            min_amount=decimal.Decimal('100.00'),
            max_amount=decimal.Decimal('100.00'),
            start_sell_date=datetime.date.today() - datetime.timedelta(days=1),
            end_sell_date=datetime.date.today() + datetime.timedelta(days=1),
            frozen_days=10,
            annual_rate=decimal.Decimal('12.2'))
        self.bankcard = self.add_bankcard(self.user.id_)
        self.identity = self.add_identity(
            self.user.id_, u'张无忌', u'44011320141005001X')

    def tearDown(self):
        super(PlaceboOrderTestCase, self).tearDown()
        # restore oritinal strategy storage
        PlaceboProduct.strategy_storage = StrategyStorage(
            self._original_strategy_storage)

    def test_add_order_failed_by_invalid_id(self):
        with raises(ValueError) as error:
            PlaceboOrder.add(
                user_id=self.user.id_ + '10',
                product_id=self.product.id_,
                bankcard_id=self.bankcard.id_,
                amount=decimal.Decimal('100'))
        assert error.value.args[0] == 'invalid user_id'

        with raises(ValueError) as error:
            PlaceboOrder.add(
                user_id=self.user.id_,
                product_id=self.product.id_ + '10',
                bankcard_id=self.bankcard.id_,
                amount=decimal.Decimal('100'))
        assert error.value.args[0] == 'invalid product_id'

        with raises(ValueError) as error:
            PlaceboOrder.add(
                user_id=self.user.id_,
                product_id=self.product.id_,
                bankcard_id=self.bankcard.id_ + '10',
                amount=decimal.Decimal('100'))
        assert error.value.args[0] == 'invalid bankcard_id'

    def test_add_order_failed_by_identity(self):
        self.identity.remove(self.user.id_)
        with raises(InvalidIdentityError):
            PlaceboOrder.add(
                user_id=self.user.id_,
                product_id=self.product.id_,
                bankcard_id=self.bankcard.id_,
                amount=decimal.Decimal('100'))

    def test_add_order_failed_by_strategy(self):
        self.white_list.remove(self.user.id_)
        with raises(InvalidProductError):
            PlaceboOrder.add(
                user_id=self.user.id_,
                product_id=self.product.id_,
                bankcard_id=self.bankcard.id_,
                amount=decimal.Decimal('100'))

    def test_add_order_failed_by_outdated_product(self):
        outdated_product = PlaceboProduct.add(
            strategy=self.check_white_list,
            min_amount=decimal.Decimal('100.00'),
            max_amount=decimal.Decimal('100.00'),
            start_sell_date=datetime.date.today() - datetime.timedelta(days=2),
            end_sell_date=datetime.date.today() - datetime.timedelta(days=1),
            frozen_days=10,
            annual_rate=decimal.Decimal('12.2'))
        with raises(OffShelfError):
            PlaceboOrder.add(
                user_id=self.user.id_,
                product_id=outdated_product.id_,
                bankcard_id=self.bankcard.id_,
                amount=decimal.Decimal('100'))

    def test_add_order_failed_by_amount_overflow(self):
        invalid_amount_list = [
            decimal.Decimal('-1'),
            decimal.Decimal('NaN'),
            decimal.Decimal('101'),
        ]
        for invalid_amount in invalid_amount_list:
            with raises(OutOfRangeError):
                PlaceboOrder.add(
                    user_id=self.user.id_,
                    product_id=self.product.id_,
                    bankcard_id=self.bankcard.id_,
                    amount=invalid_amount)

    def test_add_order_success(self):
        order = PlaceboOrder.add(
            user_id=self.user.id_,
            product_id=self.product.id_,
            bankcard_id=self.bankcard.id_,
            amount=decimal.Decimal('100'))
        order_with_default_amount = PlaceboOrder.add(
            user_id=self.user.id_,
            product_id=self.product.id_,
            bankcard_id=self.bankcard.id_,
            amount=None)

        assert order.amount == order_with_default_amount.amount
        assert order.status is PlaceboOrder.Status.running
        assert order.product == self.product
        assert order.bankcard == self.bankcard
        assert order.profit_period.value == 10
        assert order.profit_period.unit == 'day'
        assert order.profit_annual_rate == decimal.Decimal('12.2')
        assert order.owner == self.user

        assert order.biz_id.startswith('gh:s:p:')
        assert PlaceboOrder.get_by_biz_id(order.biz_id) == order

        all_ids = [order_with_default_amount.id_, order.id_]
        all_orders = [order_with_default_amount, order]
        assert PlaceboOrder.get_multi(all_ids) == all_orders
        assert PlaceboOrder.get_multi(all_ids[1:]) == all_orders[1:]
        assert PlaceboOrder.get_multi(all_ids[:-1]) == all_orders[:-1]

        assert PlaceboOrder.get_ids_by_user(self.user.id_) == all_ids

    def test_status(self):
        order = PlaceboOrder.add(
            user_id=self.user.id_,
            product_id=self.product.id_,
            bankcard_id=self.bankcard.id_,
            amount=None)
        assert order.status is PlaceboOrder.Status.running
        assert order.transfer_status(PlaceboOrder.Status.exiting) is PlaceboOrder.Status.exiting
        assert order.status is PlaceboOrder.Status.exiting
        assert order.transfer_status(PlaceboOrder.Status.exited) is PlaceboOrder.Status.exited
        assert order.status is PlaceboOrder.Status.exited

    def test_get_multi(self):
        orders = [
            PlaceboOrder.add(
                user_id=self.user.id_,
                product_id=self.product.id_,
                bankcard_id=self.bankcard.id_,
                amount=None)
            for _ in xrange(5)]
        ids = [o.id_ for o in orders]
        assert PlaceboOrder.get_multi(ids) == orders
        assert list(PlaceboOrder.iter_multi_for_exiting()) == []

        with freeze_time(orders[0].creation_time + datetime.timedelta(days=10)):
            exiting_orders = list(PlaceboOrder.iter_multi_for_exiting())
            assert exiting_orders == [
                (order, order.product) for order in reversed(orders)]

            for order, _ in exiting_orders:
                order.transfer_status(PlaceboOrder.Status.exiting)
            exiting_orders = list(PlaceboOrder.iter_multi_for_exiting())
            assert exiting_orders == []

    def test_assign_hike(self):
        order = PlaceboOrder.add(
            user_id=self.user.id_,
            product_id=self.product.id_,
            bankcard_id=self.bankcard.id_,
            amount=None)
        assert order.profit_annual_rate == decimal.Decimal('12.2')
        assert order.annual_rate_hike == decimal.Decimal('0')

        order.assign_annual_rate_hike(decimal.Decimal('0.11'))
        assert order.profit_annual_rate == decimal.Decimal('12.31')
        assert order.annual_rate_hike == decimal.Decimal('0.11')

        order = PlaceboOrder.get(order.id_)
        assert order.profit_annual_rate == decimal.Decimal('12.31')
        assert order.annual_rate_hike == decimal.Decimal('0.11')

    def test_assign_hike_failure(self):
        order = PlaceboOrder.add(
            user_id=self.user.id_,
            product_id=self.product.id_,
            bankcard_id=self.bankcard.id_,
            amount=None)

        with raises(ValueError):
            order.assign_annual_rate_hike(decimal.Decimal('-0.11'))

        order.transfer_status(PlaceboOrder.Status.exiting)
        with raises(NotRunningError):
            order.assign_annual_rate_hike(decimal.Decimal('0.11'))

    def test_calculation(self):
        order = PlaceboOrder.add(
            user_id=self.user.id_,
            product_id=self.product.id_,
            bankcard_id=self.bankcard.id_,
            amount=None)
        order.creation_time = datetime.datetime(2009, 10, 11, 12, 13, 14)
        assert order.start_date == datetime.date(2009, 10, 11)
        assert order.due_date.date() == datetime.date(2009, 10, 21)
        assert unicode(round_half_up(order.calculate_profit_amount(), 2)) == '0.33'
