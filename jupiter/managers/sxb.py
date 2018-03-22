# coding: utf-8

from flask_script import Manager

from crons.hoarder.cron_updating_sxb_products import fillup_local
from libs.utils.log import bcolors
from jupiter.ext import sxb
from sxblib.consts import ProductType
from sxblib.errors import ClientError


manager = Manager()
manager.__doc__ = 'The commands for sxb services.'


@manager.command
def init():
    """Downloads the product data of sxb."""
    try:
        rs = sxb.query_products(ProductType.ririying)
    except ClientError as e:
        bcolors.fail('Fetching Sxb Product Failed:%s' % e)
    else:
        for product_info in rs:
            product = fillup_local(product_info)
            product = fillup_local(product_info, is_child_product=True)
            bcolors.success('SxbProduct: %s' % product.name)
