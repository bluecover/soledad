# coding: utf-8

from flask_script import Manager

from jupiter.ext import zhiwang
from zwlib.client import RemoteError
from libs.utils.log import bcolors

from core.models.hoard.zhiwang import ZhiwangProduct, ZhiwangWrappedProduct


manager = Manager()
manager.__doc__ = 'The commands for zhiwang services.'


@manager.command
def init():
    """Downloads the product data of Zhiwang."""
    try:
        response = zhiwang.product_list()
    except RemoteError as e:
        bcolors.fail('Fetching Zhiwang Product Failed:%s' % e)
    else:
        all_products = []
        for product_info in response.products:
            base_product = ZhiwangProduct.add(product_info)
            bcolors.success('ZhiwangProduct: %s' % base_product.name)

            wrapped_products = ZhiwangWrappedProduct.get_multi_by_raw(base_product.product_id)
            for wp in wrapped_products:
                bcolors.success('ZhiwangWrappedProduct: %s' % wp.name)

            all_products.append(base_product)
            all_products.extend(wrapped_products)

        for p in all_products:
            # 测试环境默认上架
            p.is_taken_down = False
