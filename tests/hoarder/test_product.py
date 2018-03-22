# encoding:utf-8

from datetime import datetime

from ..framework import BaseTestCase

from core.models.hoarder.product import Product
from core.models.hoarder.vendor import Vendor, Provider
from decimal import Decimal


class ProductTest(BaseTestCase):

    def init_vendor(self):
        return Vendor.add(Provider.sxb.value, 'test')

    def init_product(self):
        self.init_vendor()
        vendor_id = Vendor.get_by_name(Provider.sxb).id_
        remote_id = '2015122217504424733'
        name = '随心宝测试产品01'
        quota = 1000.0
        total_quota = 200000.0
        today_quota = 10000.0
        total_amount = 3000000.0
        total_buy_amount = 10000.0
        min_redeem_amount = 1000.0
        max_redeem_amount = 10000.0
        day_redeem_amount = 1000.0
        interest_rate_hike = 0.001
        description = 'Test...'
        product_type = Product.Type.unlimited
        min_amount = 100
        max_amount = 10000
        rate_type = 3
        rate = 0.083
        effect_day_condition = 'C'
        effect_day = 1
        effect_day_unit = '3'
        redeem_type = Product.RedeemType.user.value
        start_sell_date = datetime.today().date()
        end_sell_date = datetime.today().date()
        return Product.add_or_update(vendor_id, remote_id, name, quota, total_quota, today_quota,
                                     total_amount, total_buy_amount, min_redeem_amount,
                                     max_redeem_amount,
                                     day_redeem_amount, interest_rate_hike, description,
                                     product_type,
                                     min_amount, max_amount, rate_type, rate, effect_day_condition,
                                     effect_day, effect_day_unit, redeem_type, start_sell_date,
                                     end_sell_date)

    def test_add_or_update(self):
        self.init_product()
        vendor_id = Vendor.get_by_name(Provider.sxb).id_
        remote_id = '2015122217504424733'
        name = '随心宝测试产品01'
        quota = 1000.0
        total_quota = 200000.0
        today_quota = 10000.0
        total_amount = 3000000.0
        total_buy_amount = 10000.0
        min_redeem_amount = 1000.0
        max_redeem_amount = 10000.0
        day_redeem_amount = 1000.0
        interest_rate_hike = 0.001
        description = 'Test...'
        product_type = Product.Type.unlimited
        min_amount = 100
        max_amount = 10000
        rate_type = 3
        rate = 0.083
        effect_day_condition = 'C'
        effect_day = 1
        effect_day_unit = '3'
        redeem_type = Product.RedeemType.user.value
        start_sell_date = datetime.today().date()
        end_sell_date = datetime.today().date()

        products = Product.get_products_by_vendor_id(vendor_id)
        assert len(products) > 0
        assert products[0].vendor_id == int(vendor_id)
        assert products[0].quota == quota
        quota = Decimal('4000.0')
        updated_product = Product.add_or_update(vendor_id, remote_id, name, quota, total_quota,
                                                today_quota,
                                                total_amount, total_buy_amount, min_redeem_amount,
                                                max_redeem_amount,
                                                day_redeem_amount, interest_rate_hike, description,
                                                product_type,
                                                min_amount, max_amount, rate_type, rate,
                                                effect_day_condition,
                                                effect_day, effect_day_unit, redeem_type,
                                                start_sell_date,
                                                end_sell_date)
        assert updated_product.id_ == products[0].id_
        assert updated_product.vendor_id == int(vendor_id)
        assert updated_product.quota == quota

    def test_go_on_sale(self):
        p = self.init_product()
        p.go_on_sale()
        assert p.is_on_sale

    def test_go_off_sale(self):
        p = self.init_product()
        p.go_off_sale()
        assert not p.is_on_sale

    def test_get_products_on_sale(self):
        p = self.init_product()
        p.go_on_sale()

        # assert next(p.get_products_on_sale())

    def test_can_redeem(self):
        p = self.init_product()
        assert p.can_redeem

    def test_get_product_ids_by_vendor_id(self):
        p = self.init_product()
        product_ids = Product.get_product_ids_by_vendor_id(p.vendor_id)
        assert len(product_ids) > 0
        assert product_ids[0] == p.vendor_id
