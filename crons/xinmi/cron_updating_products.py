#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
新投米产品信息更新
"""

from jupiter.app import create_app
from jupiter.ext import xinmi
from xmlib.consts import ProductType
from core.models.hoard.xinmi import XMFixedDuedayProduct
from core.models.hoarder.product import Product
from core.models.hoarder.vendor import Vendor, Provider
from libs.logger.rsyslog import rsyslog

app = create_app()


def update_to_hoarder_product(product):
    vendor_id = Vendor.get_by_name(Provider.xm).id_
    Product.add_or_update(vendor_id,
                          product.product_id,
                          product.name,
                          float(product.quota),
                          float(product.total_amount),
                          float(product.total_amount),
                          float(product.total_amount),
                          float(product.sold_amount),
                          0,
                          0,
                          0,
                          0,
                          product.description,
                          Product.Type.classic,
                          product.min_amount,
                          product.max_amount,
                          # 固定收益率
                          1,
                          product.annual_rate/100,
                          1,
                          1,
                          1,
                          Product.RedeemType.auto.value,
                          product.start_sell_date,
                          product.end_sell_date,
                          product.expire_period,
                          product.expire_period_unit)


def main():
    """Downloads the product data of Xinmi."""
    with app.app_context():
        response = xinmi.get_products(ProductType.dingqi, remark=None)
        products = [
            XMFixedDuedayProduct.add(info) for info in response.products if
            info.get('product_id') != '2015122217504424733']
        rsyslog.send(','.join([str(p.product_id) for p in products]),
                     tag='xm_updating_products')
        # (暂时取消)增加新米产品到hoarder系统进行管理
        """
        for p in products:
            update_to_hoarder_product(p)
        """


if __name__ == '__main__':
    main()
