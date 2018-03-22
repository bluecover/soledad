# coding: utf-8


# 包装产品错误


class ProductWrappingError(Exception):
    pass


class ImproperAmountAllocation(ProductWrappingError):
    pass


class UnknownProductInheritance(ProductWrappingError):
    pass


class InvalidWrapRule(ProductWrappingError):
    pass


class WrappedProductCreated(ProductWrappingError):
    pass
