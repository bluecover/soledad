# coding: utf-8


# 资产错误


class AssetError(Exception):
    pass


class AssetCreatedError(AssetError):
    pass


class UnknownAssetError(AssetError):
    pass


class UnknownOrderError(AssetError):
    pass


class UnmatchedOrderInfoError(AssetError):
    pass


class BoundBeforeError(AssetError):
    pass


class OrderBoundWithOtherError(AssetError):
    pass


class InvalidRedeemBankCardError(AssetError):
    pass
