# coding: utf-8

from core.models.base import EntityModel


class FirewoodWrapper(EntityModel):
    """抵扣金返现红包的包装配置

    用户在参加活动或具备某些资格时，将会由系统自动/后台主动发放抵扣返现红包.

    红包金额：可为固定金额如定额直充红包，也可为根据条件计算得出的浮动金额如多攒多送；
    红包名称及介绍：用于服务端记录标签与用户显示.

    注: 为了支持有可能添加的动态金额充值，暂时保留此类不用namedtuple.
    """

    def __init__(self, name, worth, introduction=u'红包', rate=0):
        # 红包类型名称
        self.name = name
        # 红包金额，暂时为固定值
        self.worth = worth
        # 红包类型简介
        self.introduction = introduction
        # 增加红包利率，以计算动态金额
        self.rate = rate
