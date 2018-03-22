# coding: utf-8

from __future__ import absolute_import

import decimal
import datetime

from core.models.hoard.placebo import PlaceboProduct
from core.models.hoard.placebo.product import StrategyStorage
from .framework import BaseTestCase


class PlaceboProductTestCase(BaseTestCase):

    def setUp(self):
        super(PlaceboProductTestCase, self).setUp()
        self._original_strategy_storage = dict(PlaceboProduct.strategy_storage)

        @PlaceboProduct.strategy_storage.register(id_=1, name=u'ID 为奇数')
        def odd_user_id(user_id):
            user_id = int(user_id)
            return user_id > 0 and user_id % 2 != 0

        self.odd_user_id = odd_user_id

    def tearDown(self):
        super(PlaceboProductTestCase, self).tearDown()
        # restore oritinal strategy storage
        PlaceboProduct.strategy_storage = StrategyStorage(
            self._original_strategy_storage)

    def _create_placebo_product(
            self, frozen_days=18, annual_rate=decimal.Decimal('8.8'),
            strategy=None):
        product = PlaceboProduct.add(
            strategy=strategy or self.odd_user_id,
            min_amount=decimal.Decimal('100.00'),
            max_amount=decimal.Decimal('200.00'),
            start_sell_date=datetime.date.today() - datetime.timedelta(days=1),
            end_sell_date=datetime.date.today() + datetime.timedelta(days=1),
            frozen_days=frozen_days,
            annual_rate=annual_rate)
        return product

    def test_register_strategy(self):
        def foo(user_id):
            pass
        foo_strategy = PlaceboProduct.strategy_storage.register(
            id_='2', name=u'foo', target=foo)
        assert foo_strategy.id_ == '2'
        assert foo_strategy.name == u'foo'
        assert foo_strategy.target is foo

        product = self._create_placebo_product(strategy=foo_strategy)
        assert product.strategy is foo_strategy

    def test_get_nothing(self):
        assert PlaceboProduct.get(1) is None

    def test_create_and_get(self):
        product = self._create_placebo_product()
        assert product.id_ > 0
        assert PlaceboProduct.get(product.id_) == product
        assert product.min_amount == decimal.Decimal('100')
        assert product.max_amount == decimal.Decimal('200')

        assert PlaceboProduct.get_all_ids() == [product.id_]

        product2 = self._create_placebo_product()
        assert PlaceboProduct.get_all_ids() == [product2.id_, product.id_]

    def test_strategy(self):
        product = self._create_placebo_product()
        assert product.strategy.target('10001')
        assert not product.strategy.target('10002')
        assert product.strategy.target('10003')

        ids = [product.id_]
        assert PlaceboProduct.get_multi(ids) == [product]
        assert PlaceboProduct.get_multi(ids, user_id='2') == []
        assert PlaceboProduct.get_multi(ids, user_id='3') == [product]
        assert PlaceboProduct.get_multi(ids, user_id='4') == []

    def test_extra_methods(self):
        product = self._create_placebo_product(12, decimal.Decimal('3.4'))
        assert product.get_product_annotations(None, None) == []
        assert product.frozen_days == 12
        assert product.annual_rate == decimal.Decimal('3.4')
        assert product.profit_period['min'] == product.profit_period['max']
        assert product.profit_period['min'].value == 12
        assert product.profit_period['min'].unit == 'day'
        assert product.profit_annual_rate['min'] == product.profit_annual_rate['max']
        assert product.profit_annual_rate['min'] == decimal.Decimal('3.4')
        assert product.in_stock is True

    def test_get_by_strategy(self):
        product = self._create_placebo_product()
        result_ids = PlaceboProduct.get_ids_by_strategy(self.odd_user_id.id_)
        assert result_ids == [product.id_]

        another_product = self._create_placebo_product()
        result_ids = PlaceboProduct.get_ids_by_strategy(self.odd_user_id.id_)
        assert result_ids == [another_product.id_, product.id_]

        another_product = self._create_placebo_product()
        result_ids = PlaceboProduct.get_ids_by_strategy(self.odd_user_id.id_)
