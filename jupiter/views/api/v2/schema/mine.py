# coding: utf-8

from marshmallow import Schema, fields


class AssetProfile(Schema):
    """ 资产概况 """

    #: :class:`~decimal.Decimal` 总资产
    total_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 昨日收益
    total_yesterday_profit = fields.Decimal(places=2)

    #: :class:`~decimal.Decimal` 攒钱助手资产
    hoard_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 攒钱助手每日收益
    hoard_daily_profit = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 攒钱助手昨日收益
    hoard_yesterday_profit = fields.Decimal(places=2)

    #: :class:`~decimal.Decimal` 零钱包资产
    wallet_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 零钱包昨日收益
    wallet_yesterday_profit = fields.Decimal(places=2)
