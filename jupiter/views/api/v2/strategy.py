# coding: utf-8

from core.models.hoard.common import ProfitPeriod
from core.models.hoarder.vendor import Provider
from core.models.hoard.manager import SavingsManager
from jupiter.utils.inhouse import check_is_inhouse


def wrapped_product(all_product, origin_products, recommend_products):
    if origin_products == recommend_products['low_priority_products']:
        all_product['hoarder'] = origin_products
        all_product['wallet'] = []
        return all_product
    else:
        all_product['wallet'] = origin_products
        all_product['hoarder'] = []
        return all_product


def get_recommend_products(user=None):
    recommend_products = product_pool()
    from .product import get_products
    all_product = get_products()
    if not user:
        return wrapped_product(
            all_product, recommend_products['high_priority_products'], recommend_products)

    is_new_saving_user = SavingsManager(user.id_).is_new_savings_user
    if is_new_saving_user:
        return wrapped_product(
            all_product, recommend_products['high_priority_products'], recommend_products)

    sxb_products = recommend_products['medium_priority_products']
    is_sxb_on_sale = [p.is_on_sale for p in sxb_products]
    if any(is_sxb_on_sale):
        return wrapped_product(all_product, sxb_products, recommend_products)

    xm_products = recommend_products['low_priority_products']
    is_xm_in_stock = [p.is_on_sale for p in xm_products]
    if any(is_xm_in_stock):
        return wrapped_product(all_product, xm_products, recommend_products)

    return wrapped_product(
        all_product, recommend_products['medium_priority_products'], recommend_products)


def product_pool():
    from .product import get_products
    products = get_products()
    wallet_products = [p for p in products['wallet'] if not isinstance(p, dict)]
    new_comer_products = [p for p in wallet_products if p.vendor.name == Provider.sxb.value]
    hoarder_products = [p for p in products['hoarder']]
    if check_is_inhouse():
        low_priority_products = [
            p for p in hoarder_products if p.profit_period['min'] == ProfitPeriod(90, 'day')]
    else:
        low_priority_products = [
            p for p in hoarder_products if p.profit_period['min'] == ProfitPeriod(365, 'day')]

    return {
        'high_priority_products': new_comer_products[0:1],
        'medium_priority_products': new_comer_products[1:2],
        'low_priority_products': low_priority_products}
