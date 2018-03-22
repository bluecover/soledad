# coding: utf-8

from marshmallow import Schema, fields


class ProductStatusSchema(Schema):
    """产品状态"""

    #: :class:`str` 状态标示 可为`offsale` 下架，`onsale` 在售, `soldout` 售罄，`presale` 预售
    st = fields.String(default='offsale')
    #: :class:`str` 状态文本描述 可为 `购买`，`售罄`，`11点起售`
    text = fields.String(default=u'售罄')
    #: :class:`str` 状态文本描述 可为 `今日售罄，明天11点起售` 或``空``则无提示内容
    tip = fields.String(default=u'')
    #: :class:`str` 状态对应颜色
    color = fields.String(default='#334234')


class AnnotationSchema(Schema):
    """福利"""

    #: :class:`boolean` 有礼券
    #:
    #: .. note:: 还可以扩展其他福利内容
    has_coupons = fields.Boolean(default=False)


class PeriodSchema(Schema):
    """期限"""

    #: :class:`int` 期限值（可判断值大于0，区分活期与定期，大于0为固定期限，否则为活期，可以取``unit``单位，``text``
    #: 为文案）
    value = fields.Int(default=0)
    #: :class:`str` 期限单位：可为``年``、``月``、``天``
    unit = fields.String(default=u'天')
    #: :class:`str` 期限文案, 如``活期``、``90天`` 等
    text = fields.String(default=u'活期')


class VendorSchema(Schema):
    """合作伙伴"""

    #: :class:`int` ID，
    uid = fields.Int(attribute='id_', default=0)
    #: :class:`str` 名称(申购时需要使用)
    name = fields.String(required=True)
    #: :class:`str` 协议
    protocol = fields.String()
    #: :class:`str` 状态
    status = fields.String(attribute='_status')


class WalletProductSchema(Schema):
    """零钱包产品"""

    #: :class:`str` 产品ID
    uid = fields.String()
    #: :class:`str` 产品名称
    name = fields.String()
    #: :class:`.VendorSchema` 合作伙伴信息
    vendor = fields.Nested(VendorSchema)
    #: :class:`str` 产品标题
    title = fields.String()
    #: :class:`str` 活动标题
    activity_title = fields.String()
    #: :class:`str` 活动介绍
    activity_introduction = fields.String()
    #: :class:`~decimal.Decimal` 年化收益率
    annual_rate = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最大可攒金额
    max_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最小可攒金额
    min_amount = fields.Decimal(places=2)
    #: :class:`list` of :class:`str` 标签列表
    tags = fields.List(fields.String())
    #: :class:`.PeriodSchema` 期限, 如 `活期` 等
    period = fields.Nested(PeriodSchema)
    #: :class:`.AnnotationSchema` 礼券可用信息如`has_coupons=True` (可扩展的ICON列表)
    annotations = fields.Nested(AnnotationSchema)
    #: :class:`.ProductStatusSchema` 状态
    display_status = fields.Nested(ProductStatusSchema)
    #: :class:`.Date` 起息日
    start_date = fields.Date()
    #: :class:`.Date` 首次查看收益日期
    check_benefit_date = fields.Date(default='0000-00-00')
    #: :class:`.url` 提现规则
    withdraw_rule = fields.Url()
    #: :class:`str` 产品公司
    company = fields.String()
    #: :class:`str` 产品代码
    code = fields.String()
    #: :class:`str` 银行名称
    bank_name = fields.String()
    #: :class:`~decimal.Decimal` 剩余可购买金额
    quota = fields.Decimal(places=2)


class HoarderProductSchema(Schema):
    """攒钱助手产品"""

    #: :class:`str` 产品ID
    uid = fields.String()
    #: :class:`str` 产品名称
    name = fields.String()
    #: :class:`.VendorSchema` 合作伙伴信息
    vendor = fields.Nested(VendorSchema)
    #: :class:`str` 产品标题
    title = fields.String()
    #: :class:`str` 活动标题
    activity_title = fields.String()
    #: :class:`str` 活动介绍
    activity_introduction = fields.String()
    #: :class:`~decimal.Decimal` 年化收益率
    annual_rate = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最大可攒金额
    max_amount = fields.Decimal(places=2)
    #: :class:`~decimal.Decimal` 最小可攒金额
    min_amount = fields.Decimal(places=2)
    #: :class:`list` of :class:`str` 标签列表
    tags = fields.List(fields.String())
    #: :class:`.PeriodSchema` 期限, 如 `90天`、`180天` 等
    period = fields.Nested(PeriodSchema)
    #: :class:`.AnnotationSchema` 礼券可用信息如`has_coupons=True` (可扩展的ICON列表)
    annotations = fields.Nested(AnnotationSchema)
    #: :class:`.ProductStatusSchema` 状态
    display_status = fields.Nested(ProductStatusSchema)
    #: :class:`.Date` 起息日
    start_date = fields.Date()
    #: :class:`.Date` 预计到期日
    expect_due_date = fields.Date()
    #: :class:`.Date` 首次查看收益日期
    check_benefit_date = fields.Date()
    #: :class:`.url` 提现规则
    withdraw_rule = fields.Url()
    #: :class:`~decimal.Decimal` 剩余可购买金额
    quota = fields.Decimal(places=2)


class ProductResponseSchema(Schema):
    """产品"""

    #: :class:`.HoarderProductSchema` 攒钱助手产品（定期产品）
    hoarder = fields.Nested(HoarderProductSchema, many=True)
    #: :class:`.WalletProductSchema` 零钱包产品（活期产品)
    wallet = fields.Nested(WalletProductSchema, many=True)
    #: :class:`url` 产品帮助链接
    help_url = fields.URL()
