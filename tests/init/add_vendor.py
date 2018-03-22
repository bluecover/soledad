# coding: utf-8

from libs.utils.log import bcolors
from core.models.hoarder.vendor import Vendor, Provider


if __name__ == '__main__':
    bcolors.run('Add product_vendor.')
    Vendor.add(Provider.sxb.value, 'sxb')
    Vendor.add(Provider.xm.value, 'xm')
    Vendor.add(Provider.zw.value, 'zw')
    Vendor.add(Provider.ms.value, 'ms')
    bcolors.success('Init product vendor done.')
