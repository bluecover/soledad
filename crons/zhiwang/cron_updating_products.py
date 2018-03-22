#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
指旺产品信息更新
"""

from datetime import datetime

from jupiter.app import create_app
from jupiter.ext import zhiwang
from core.models.hoard.zhiwang import ZhiwangProduct, ZhiwangWrappedProduct


app = create_app()


def main():
    """Downloads the product data of Zhiwang."""
    with app.app_context():
        response = zhiwang.product_list()

        all_products = []
        for product_info in response.products:
            base_product = ZhiwangProduct.add(product_info)
            wrapped_products = ZhiwangWrappedProduct.get_multi_by_raw(base_product.product_id)
            all_products.append(base_product)
            all_products.extend(wrapped_products)

        # 注意: 如果12点后依然没有产品，则12点后创建的产品将只能由运营人员手动上架

        hour = datetime.now().hour
        for p in all_products:
            if hour == 0 and p.is_taken_down and not p.is_either_sold_out:
                p.is_taken_down = False


if __name__ == '__main__':
    main()
