#!/usr/bin/env python
# coding:utf-8

"""
    更新所有用户收益
    ~~~~~~~~~~~~~~~~~~~~~~
"""

from core.models.hoarder.product import Product
from core.models.hoarder.asset import Asset
from core.models.hoarder.vendor import Vendor, Provider
from jupiter.workers.hoarder import hoarder_async_asset


def async_sxb_asset():
    vendor = Vendor.get_by_name(Provider.sxb)
    product_ids = Product.get_product_ids_by_vendor_id(vendor_id=vendor.id_)
    for product_id in product_ids:
        for id_ in Asset.get_ids_by_product_id(product_id):
            hoarder_async_asset.produce(str(id_))


def main():
    async_sxb_asset()


if __name__ == '__main__':
    main()
