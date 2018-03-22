# coding: utf-8

from core.models.hoard.common import ProfitPeriod
from core.models.hoard.providers import zhiwang


class ProductMatcher(object):
    """
    通用产品匹配规则
    """

    def __init__(self, description, providers):
        self.description = description
        self.providers = providers

    @property
    def sort_key(self):
        return self.quantifier

    @property
    def quantifier(self):
        return

    @property
    def display_product_requirement(self):
        """优惠的适用产品"""
        return u'全场产品可用'

    def is_available_for_product(self, product):
        # 首要检查产品是否接受使用优惠(新手产品等二次包装产品暂不支持)
        if not product.is_accepting_bonus:
            return False

        # 其次检查产品合作方是否被支持
        if product.provider not in self.providers:
            return False
        return True


class FixedClosureMatcher(ProductMatcher):
    """
    定期产品匹配规则
    """

    def __init__(self, description, providers, profit_periods):
        super(FixedClosureMatcher, self).__init__(description, providers)
        assert all([isinstance(p, ProfitPeriod) for p in profit_periods])

        self.profit_periods = profit_periods

    @property
    def quantifier(self):
        return min(self.profit_periods).value

    @property
    def display_product_requirement(self):
        return u'仅限%s产品可用' % u'或'.join([p.display_text for p in self.profit_periods])

    def is_available_for_product(self, product):
        from core.models.hoard.zhiwang import ZhiwangProduct
        if not super(FixedClosureMatcher, self).is_available_for_product(product):
            return False
        if product.provider is zhiwang and product.product_type is not ZhiwangProduct.Type.classic:
            return False
        return product.profit_period['min'] in self.profit_periods
