# coding: utf-8

from flask_script import Manager

from jupiter.ext import xinmi
from xmlib.errors import ClientError
from xmlib.consts import ProductType
from libs.utils.log import bcolors

from core.models.hoard.xinmi.product import XMProduct
from crons.xinmi.cron_updating_products import update_to_hoarder_product

manager = Manager()
manager.__doc__ = 'The commands for xinmi services.'


@manager.command
def init():
    """Downloads the product data of Xinmi."""
    try:
        #: 目前只有 dingqi 产品可用
        response = xinmi.get_products(ProductType.dingqi, remark=None)
    except ClientError as e:
        bcolors.fail('Fetching Xinmi Product Failed:%s' % e)
    else:
        for product_info in response.products:
            product = XMProduct.add(product_info)
            # 增加新米产品到hoarder系统进行管理
            update_to_hoarder_product(product)
            bcolors.success('XinMiProduct: %s' % product.name)
