# coding: utf-8


# 支付错误


class PayError(Exception):
    pass


class LocalPayProcessingError(PayError):
    pass


class PayTerminatedError(PayError):
    pass
