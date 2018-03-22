# coding: utf-8

from datetime import datetime, timedelta

from sxblib.consts import ProductType

from libs.logger.rsyslog import rsyslog
from core.models.hoarder.product import Product
from core.models.hoarder.vendor import Vendor, Provider
from jupiter.ext import sxb
from jupiter.app import create_app


app = create_app()


def check_available_for_product(product_info):
    # 上下架时间很可能不会传回来
    # 默认上架时间为开售时间,默认下架时间为开售1年后
    end_sell_date = (
        product_info.sale_time.date()
        if product_info.sale_time else (datetime.now() + timedelta(days=365)).date())
    start_sell_date = (
        product_info.open_time.date()
        if product_info.open_time else datetime.now().date())

    return start_sell_date, end_sell_date


def fillup_local(product_info, is_child_product=None):

    start_sell_date, end_sell_date = check_available_for_product(product_info)
    vendor_id = Vendor.get_by_name(Provider.sxb).id_
    return Product.add_or_update(
        vendor_id,
        product_info.id_,
        product_info.name,
        product_info.quota,
        product_info.total_quota,
        product_info.today_quota,
        product_info.total_amount,
        product_info.total_buy_amount,
        product_info.min_redeem_amount,
        product_info.max_redeem_amount,
        product_info.day_redeem_amount,
        product_info.add_year_rate,
        product_info.remark,
        Product.Type.unlimited,
        product_info.min_amount,
        product_info.max_amount,
        product_info.return_rate_type.value,
        product_info.return_rate,
        product_info.effect_day_type.value,
        product_info.effect_day,
        product_info.effect_day_unit.value,
        product_info.is_redeem,
        start_sell_date,
        end_sell_date,
        is_child_product=is_child_product
    )


def main():
    """Downloads the product data of sxb."""
    with app.app_context():
        rs = sxb.query_products(ProductType.ririying)
        products = [fillup_local(product_info) for product_info in rs]
        new_comer_products = [
            fillup_local(product_info, is_child_product=True) for product_info in rs]
        products.extend(new_comer_products)
        rsyslog.send(','.join([str(p.remote_id) for p in products]),
                     tag='sxb_updating_products')

        # 短时策略：0点-10点产品默认下架售罄，10点开售新手标，10~11点普通产品仍为下架状态，11点后开售普通类产品
        # 注意: 如果12点后依然没有产品，则12点后创建的产品将只能由运营人员手动上架

        hour = datetime.now().hour
        for p in products:
            if hour < 10:
                p.go_off_sale()
            elif hour == 10:
                if p.kind is Product.Kind.child:
                    if p.is_taken_down:
                        p.go_on_sale()
                else:
                    p.go_off_sale()
            else:
                if p.is_taken_down:
                    p.go_on_sale()

if __name__ == '__main__':
    main()
