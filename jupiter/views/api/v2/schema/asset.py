# coding: utf-8

from marshmallow import Schema, fields


class AssetResponseSchema(Schema):
    """随心攒资产信息实体"""

    #: :class:`int` ID
    uid = fields.Int(default=-1)
    #: :class:`~decimal.Decimal` 昨日收益（负数判断小于0）
    yesterday_profit = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 持有资产
    hold_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 累计收益
    hold_profit = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 年化收益率
    actual_annual_rate = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 剩余可持有金额
    rest_hold_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 剩余可提现金额
    rest_redeem_amount = fields.Decimal(places=2)
    #: :class:`int` 剩余可免费提现次数
    residual_redemption_times = fields.Int()
