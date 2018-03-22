# coding:utf-8

from weakref import WeakValueDictionary

from core.models.base import EntityModel
from core.models.welfare.package.package import PackageKind
from core.models.welfare.package.kind import (
    redeemcode_fanmeeting_gold_package, redeemcode_fanmeeting_silver_package,
    redeemcode_fanmeeting_copper_package, women_day_2016_package, mom_day_2016_package,
    yue_girl_package, yue_girl_2th_package, sangongzi_package)


class RedeemCodeActivity(EntityModel):
    """兑换码所属活动

    兑换码所属活动记录了活动名称、兑换码是否可以叠加使用以及
    兑换码所包含的奖励

    :param name: 兑换码所属活动
    :param max_usage_limit_per_user: 本次活动允许用户累加兑换的最大次数
    :param reward_welfare_pacakge_kind: 本次活动所包含礼包
    """
    storage = WeakValueDictionary()

    def __init__(self, id_, name, max_usage_limit_per_user,
                 reward_welfare_package_kind):
        assert max_usage_limit_per_user >= 1
        assert isinstance(reward_welfare_package_kind, PackageKind)

        if id_ in self.storage:
            raise ValueError('id %r has been used' % id_)

        self.id_ = str(id_)
        self.name = unicode(name)
        self.max_usage_limit_per_user = max_usage_limit_per_user
        self.reward_welfare_package_kind = reward_welfare_package_kind
        self.storage[self.id_] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(id_)

fanmeeting_gold = RedeemCodeActivity(
    id_=1,
    name=u'见面会',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=redeemcode_fanmeeting_gold_package
)

fanmeeting_silver = RedeemCodeActivity(
    id_=2,
    name=u'见面会',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=redeemcode_fanmeeting_silver_package
)

fanmeeting_copper = RedeemCodeActivity(
    id_=3,
    name=u'见面会',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=redeemcode_fanmeeting_copper_package
)
women_day_2016 = RedeemCodeActivity(
    id_=4,
    name=u'2016女人节',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=women_day_2016_package
)

mom_day_2016 = RedeemCodeActivity(
    id_=5,
    name=u'2016母亲节',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=mom_day_2016_package
)

yue_girl_activity = RedeemCodeActivity(
    id_=6,
    name=u'越女活动',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=yue_girl_package
)

yue_girl_2th_activity = RedeemCodeActivity(
    id_=7,
    name=u'越女读财活动',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=yue_girl_2th_package
)

sangongzi_activity = RedeemCodeActivity(
    id_=8,
    name=u'三公子活动',
    max_usage_limit_per_user=1,
    reward_welfare_package_kind=sangongzi_package
)
