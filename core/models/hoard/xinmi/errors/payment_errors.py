# coding: utf-8


# 支付错误


class PayError(Exception):
    pass


class PayWaitError(PayError):
    pass


class PaySucceededError(PayError):
    pass


class PayTerminatedError(PayError):
    pass
