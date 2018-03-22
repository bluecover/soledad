# coding: utf-8

from decimal import Decimal
from datetime import date, timedelta
from collections import namedtuple

from weakref import WeakValueDictionary

from core.models.base import EntityModel
from core.models.consts import Platform, CastKind, SetOperationKind
from core.models.pusher import PushSupport
from core.models.welfare import CouponWrapper, FirewoodWrapper
from core.models.welfare.coupon.kind import (
    deduction_500_cut_10, deduction_1000_cut_5, deduction_1000_cut_20,
    deduction_5000_cut_30, deduction_5000_cut_100, deduction_10000_cut_10,
    deduction_20000_cut_20, deduction_20000_cut_40, deduction_20000_cut_80,
    deduction_30000_cut_40, deduction_30000_cut_60, deduction_30000_cut_180,
    deduction_50000_cut_80, deduction_50000_cut_100, deduction_50000_cut_115,
    deduction_50000_cut_260,
    rate_2_permillage, rate_3_permillage, rate_5_permillage, rate_6_permillage,
    rate_7_permillage, rate_8_permillage, rate_9_permillage, rate_4_permillage
)
from core.models.welfare.matcher.kind import (
    all_products, regular_products, midlong_products,
    longrun_products, shortrun_products,  new_regular_products)
from .distributor import (
    NewcomerCenter, MaidenInvestmentAward, LegacyRebate, RecastInspirator,
    InvitationReward, RedeemCelebration, RedeemCodeGift, SpecialPrize, SunnyWorld, XinmiInvestAward)


class PackageKind(EntityModel, PushSupport):
    storage = WeakValueDictionary()

    WelfareSummary = namedtuple('WelfareSummary', 'firewood_info coupon_info')
    FirewoodInfo = namedtuple('FirewoodInfo', 'introduction worth')
    CouponInfo = namedtuple('CouponInfo', 'name amount')

    def __init__(self, id_, name, distributor, description=None, firewood_wrapper=None,
                 coupon_wrappers=None, distribution_scope=None, multicast_tags=None,
                 tags_combine_method=None, is_distributable=True):
        if id_ in self.storage:
            raise ValueError('id %r has been used' % id_)

        if distributor.kind_id != id_:
            raise ValueError('unmatched package distributor and kind %s' % id_)

        # 默认为单播
        distribution_scope = distribution_scope or CastKind.unicast
        if distribution_scope is CastKind.multicast:
            if not multicast_tags:
                # 如果通知类型支持推送组播，则必须指定推送标签
                raise ValueError('no group tags provided for multicast')
            # 默认在支持组播时，指定标签集合方式为并集计算
            tags_combine_method = tags_combine_method or SetOperationKind.union
        assert isinstance(distribution_scope, CastKind)

        if firewood_wrapper is None and coupon_wrappers is None:
            raise ValueError('package should contain at least one kind of welfare')

        self.id_ = id_
        #: 礼包名称
        self.name = name
        #: 礼包介绍
        self.description = description
        #: 礼包分发器，发包决策者和执行者
        self.distributor = distributor
        #: 礼包分发范围
        self.distribution_scope = distribution_scope
        #: 礼包分发对象标签
        self.multicast_tags = multicast_tags
        #: 礼包分发对象标签集合计算方式
        self.tags_combine_method = tags_combine_method
        #: 礼包分发上层开关
        self.is_distributable = is_distributable
        #: 红包，定义红包类型
        self.firewood_wrapper = firewood_wrapper
        #: 礼券套装，定义礼包类型中所包含的礼券名称及分发数量
        self.coupon_wrappers = coupon_wrappers
        self.storage[id_] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(id_)

    @property
    def allow_push(self):
        return self.push_platforms

    @property
    def is_unicast_push_only(self):
        return self.distribution_scope is CastKind.unicast

    @property
    def push_platforms(self):
        """推送平台（无礼券礼包默认推送全平台）"""
        platforms = []
        if self.coupon_wrappers:
            for w in self.coupon_wrappers:
                platforms.extend(w.platforms)
        else:
            platforms = [Platform.ios, Platform.android]
        return frozenset(set(platforms) - set([Platform.web]))

    def make_push_pack(self):
        """礼包类型类属于通知类型的子类型类，该方法用于【组播】推送元素的构建"""
        from core.models.notification.kind import welfare_gift_notification
        from core.models.pusher.element import (
            Pack, Notice, AllUsersAudience, UnionTagsAudience, IntersectTagsAudience)

        if self.distribution_scope is CastKind.broadcast:
            audience = AllUsersAudience()
        elif self.distribution_scope is CastKind.multicast:
            if self.tags_combine_method is SetOperationKind.union:
                audience = UnionTagsAudience(self.multicast_tags)
            elif self.tags_combine_method is SetOperationKind.intersection:
                audience = IntersectTagsAudience(self.multicast_tags)
            else:
                raise ValueError('invalid set operation kind')
        else:
            raise ValueError('package kind does not support multicast/broadcast')

        introduction = u'恭喜您获得{0}'.format(self.name)
        content = self.description or introduction
        title = introduction if self.description else None

        notice = Notice(content, title)
        return Pack(
            audience, notice, self.push_platforms,
            target_link=welfare_gift_notification.app_target_link)

    @property
    def welfare_summary(self):
        welfare_summary = self.WelfareSummary(firewood_info=[], coupon_info=[])
        if self.firewood_wrapper:
            firewood_info = self.FirewoodInfo(introduction=self.firewood_wrapper.introduction,
                                              worth=self.firewood_wrapper.worth)
            welfare_summary.firewood_info.append(firewood_info)
        if self.coupon_wrappers:
            coupon_info = {}
            for wrapper in self.coupon_wrappers:
                coupon_info.setdefault(wrapper.name, []).append(wrapper.amount)
            welfare_summary.coupon_info.extend(
                self.CouponInfo(name, sum(amount_list))
                for name, amount_list in coupon_info.items())
        return welfare_summary

    @property
    def sum_deduct(self):
        deduct_list = []
        for wrapper in self.coupon_wrappers:
            deduct_list.append(wrapper.kind.regulation.deduct_quota)
        return sum(deduct_list)

# 业务条件触发类礼包(1xxx)
first_purchase_package = PackageKind(
    id_=1005,
    name=u'普通产品首次投资礼包',
    description=u'本次攒钱助手购买成功，下次攒钱的礼包已为您准备好，查看详情 > >',
    distributor=MaidenInvestmentAward(1005),
    firewood_wrapper=FirewoodWrapper('first_purchase', Decimal('25.0'), u'首次投资奖'),
    coupon_wrappers=[
        CouponWrapper(deduction_50000_cut_260, u'新人投资券', 1, midlong_products)
    ]
)

recast_inspire_package = PackageKind(
    id_=1006,
    name=u'首笔非新手标产品到期礼包',
    description=u'您购买的攒钱助手已到期，送您一个礼包，继续来攒钱吧',
    distributor=RecastInspirator(1006),
    coupon_wrappers=[
        CouponWrapper(rate_3_permillage, u'全场加息券', 1, expires_in=timedelta(days=7)),
        CouponWrapper(deduction_30000_cut_60, u'老手投资券', 1, midlong_products)
    ])

invite_investment_package = PackageKind(
    id_=1007,
    name=u'新人邀请礼包',
    description=u'您邀请的好友已成功攒钱，送您一个礼包，感谢您的支持',
    distributor=InvitationReward(1007),
    firewood_wrapper=FirewoodWrapper('invite_investment', Decimal('20'), u'常规邀请新人奖')
)

redeem_celebration_package = PackageKind(
    id_=1008,
    name=u'到期奖励礼包',
    description=u'您购买的攒钱助手已到期，送您一张3天有效的0.3%加息券，继续来攒钱吧',
    distributor=RedeemCelebration(1008),
    coupon_wrappers=[
        CouponWrapper(
            rate_3_permillage, u'到期奖励券', 1, new_regular_products, expires_in=timedelta(days=3))
    ]
)

newcomer_package = PackageKind(
    id_=1009,
    name=u'新手注册礼包',
    description=u'欢迎加入好规划，请前往查看您的新手礼包',
    distributor=NewcomerCenter(1009),
    coupon_wrappers=[
        CouponWrapper(
            deduction_1000_cut_5, u'新人满减券', 1, expires_in=timedelta(days=30)),
        CouponWrapper(
            deduction_5000_cut_30, u'新人满减券', 1, expires_in=timedelta(days=30)),
        CouponWrapper(
            deduction_20000_cut_80, u'新人满减券', 1, midlong_products,
            expires_in=timedelta(days=30))
    ])

# 特殊活动类礼包(2xxx)
newcomer_1118_exclusive_package = PackageKind(
    id_=2001,
    name=u'1118新手注册限购礼包',
    distributor=NewcomerCenter(2001),
    coupon_wrappers=[
        CouponWrapper(rate_5_permillage, u'全场加息券', 3, expires_at=date(2015, 11, 18))
    ],
)

carnival_1118_invest_package = PackageKind(
    id_=2002,
    name=u'1118投资奖励礼包',
    distributor=SpecialPrize(2002),
    firewood_wrapper=FirewoodWrapper('1118_bonus', Decimal('50.0'), u'周年回馈'),
    coupon_wrappers=[
        CouponWrapper(deduction_10000_cut_10, u'周年回馈10元券', 1, expires_at=date(2015, 12, 30)),
        CouponWrapper(deduction_20000_cut_20, u'周年回馈20元券', 2, expires_at=date(2015, 12, 30))
    ],
)

christmas_primary_package = PackageKind(
    id_=2003,
    name=u'圣诞节蛋糕游戏三等奖礼包',
    distributor=SpecialPrize(2003),
    coupon_wrappers=[
        CouponWrapper(
            deduction_10000_cut_10, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(
            deduction_20000_cut_20, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(rate_5_permillage, u'游戏奖励券', 1, expires_at=date(2016, 1, 31))
    ],
)

christmas_medium_package = PackageKind(
    id_=2004,
    name=u'圣诞节蛋糕游戏二等奖礼包',
    distributor=SpecialPrize(2004),
    firewood_wrapper=FirewoodWrapper('christmas_2015', Decimal('5.0'), u'圣诞游戏奖励'),
    coupon_wrappers=[
        CouponWrapper(
            deduction_10000_cut_10, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(
            deduction_20000_cut_20, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(
            deduction_30000_cut_40, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(
            deduction_50000_cut_100, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(rate_5_permillage, u'游戏奖励券', 1, expires_at=date(2016, 1, 31))
    ],
)

christmas_best_package = PackageKind(
    id_=2005,
    name=u'圣诞节蛋糕游戏一等奖礼包',
    distributor=SpecialPrize(2005),
    firewood_wrapper=FirewoodWrapper('christmas_2015', Decimal('5.0'), u'圣诞游戏奖励'),
    coupon_wrappers=[
        CouponWrapper(
            deduction_10000_cut_10, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(
            deduction_20000_cut_20, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(
            deduction_30000_cut_40, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(
            deduction_50000_cut_100, u'游戏奖励券', 1,
            regular_products, expires_at=date(2016, 1, 31)),
        CouponWrapper(rate_5_permillage, u'游戏奖励券', 1, expires_at=date(2016, 1, 31)),
        CouponWrapper(rate_8_permillage, u'游戏奖励券', 1, expires_at=date(2016, 1, 31))
    ],
)

redeemcode_fanmeeting_copper_package = PackageKind(
    id_=2006,
    name=u'见面会专享礼包',
    distributor=RedeemCodeGift(2006),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_6_permillage, u'全场加息券', 1, expires_at=date(2016, 3, 31)),
    ],
)
redeemcode_fanmeeting_silver_package = PackageKind(
    id_=2007,
    name=u'见面会专享礼包',
    distributor=RedeemCodeGift(2007),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_7_permillage, u'全场加息券', 1, expires_at=date(2016, 3, 31)),
    ],
)
redeemcode_fanmeeting_gold_package = PackageKind(
    id_=2008,
    name=u'见面会专享礼包',
    distributor=RedeemCodeGift(2008),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_8_permillage, u'全场加息券', 1, expires_at=date(2016, 5, 31)),
    ],
)

women_day_2016_package = PackageKind(
    id_=2009,
    name=u'2016女人节',
    distributor=RedeemCodeGift(2009),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_9_permillage, u'女人节加息券', 1, shortrun_products,
                      expires_in=timedelta(days=30)),
    ],
)

mom_day_2016_package = PackageKind(
    id_=2010,
    name=u'LoveMom礼包',
    distributor=RedeemCodeGift(2010),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_5_permillage, u'LoveMom加息券', 1, new_regular_products,
                      expires_at=date(2016, 5, 15)),
    ],
)

yue_girl_package = PackageKind(
    id_=2011,
    name=u'越女专属礼包',
    distributor=RedeemCodeGift(2011),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_4_permillage, u' 越女专属加息券', 1, new_regular_products,
                      expires_at=date(2016, 5, 21)),
    ],
)

yue_girl_2th_package = PackageKind(
    id_=2012,
    name=u'越女读财礼包',
    distributor=RedeemCodeGift(2012),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_4_permillage, u' 越女读财加息券', 1, new_regular_products,
                      expires_in=timedelta(days=7)),
    ],
)

sangongzi_package = PackageKind(
    id_=2013,
    name=u'三公子专属礼包',
    distributor=RedeemCodeGift(2013),
    is_distributable=True,
    coupon_wrappers=[
        CouponWrapper(rate_4_permillage, u' 三公子专属加息券', 1, new_regular_products,
                      expires_in=timedelta(days=7)),
    ],
)

invest_lottery_package_2_0 = PackageKind(
    id_=2014,
    name=u'邀请抽奖红包2元',
    distributor=SpecialPrize(2014),
    firewood_wrapper=FirewoodWrapper('invest_lottery_2_0', Decimal('2.0'), u'抽奖红包'),
)

invest_lottery_package_1_8 = PackageKind(
    id_=2015,
    name=u'邀请抽奖红包1.8元',
    distributor=SpecialPrize(2015),
    firewood_wrapper=FirewoodWrapper('invest_lottery_1_8', Decimal('1.8'), u'抽奖红包'),
)

invest_lottery_package_1_0 = PackageKind(
    id_=2016,
    name=u'邀请抽奖红包1元',
    distributor=SpecialPrize(2016),
    firewood_wrapper=FirewoodWrapper('invest_lottery_1_0', Decimal('1.0'), u'抽奖红包'),
)

invest_lottery_package_0_8 = PackageKind(
    id_=2017,
    name=u'邀请抽奖红包0.8元',
    distributor=SpecialPrize(2017),
    firewood_wrapper=FirewoodWrapper('invest_lottery_0_8', Decimal('0.8'), u'抽奖红包'),
)

# 系统发放类礼包(3xxx)
carnival_1118_sunbeam_package = PackageKind(
    id_=3001,
    name=u'1118限购券礼包',
    distributor=SunnyWorld(3001),
    distribution_scope=CastKind.broadcast,
    coupon_wrappers=[
        CouponWrapper(rate_5_permillage, u'全场加息券', 3, expires_at=date(2015, 11, 18)),
    ],
)

common_compensation_package = PackageKind(
    id_=3002,
    name=u'补偿礼包',
    distributor=SpecialPrize(3002),
    coupon_wrappers=[
        CouponWrapper(rate_5_permillage, u'全场加息券', 1, expires_in=timedelta(days=60)),
    ],
)

thanksgiving_2015_package = PackageKind(
    id_=3003,
    name=u'感恩礼包',
    distributor=SunnyWorld(3003),
    distribution_scope=CastKind.broadcast,
    coupon_wrappers=[
        CouponWrapper(deduction_10000_cut_10, u'感恩礼券', 1, expires_at=date(2015, 11, 29)),
        CouponWrapper(deduction_30000_cut_40, u'感恩礼券', 1, expires_at=date(2015, 11, 29)),
        CouponWrapper(deduction_50000_cut_80, u'感恩礼券', 1, expires_at=date(2015, 11, 29)),
    ],
)

weather_blessing_package = PackageKind(
    id_=3004,
    name=u'好天气祈福礼包',
    distributor=SunnyWorld(3004),
    distribution_scope=CastKind.broadcast,
    coupon_wrappers=[
        CouponWrapper(
            rate_5_permillage, u'好天气祈福券', 1, regular_products, expires_at=date(2015, 12, 4))
    ],
)

happy_ending_package = PackageKind(
    id_=3005,
    name=u'2015年末庆礼包',
    distributor=SunnyWorld(3005),
    distribution_scope=CastKind.broadcast,
    coupon_wrappers=[
        CouponWrapper(rate_3_permillage, u'全场加息券', 1, expires_at=date(2015, 12, 13)),
        CouponWrapper(
            deduction_20000_cut_40, u'满减券', 1, regular_products, expires_at=date(2015, 12, 13)),
    ],
)

happy_birthday_package = PackageKind(
    id_=3006,
    name=u'生日祝福礼包',
    distributor=SpecialPrize(3006),
    coupon_wrappers=[
        CouponWrapper(rate_6_permillage, u'生日祝福券', 1, expires_in=timedelta(days=30))
    ],
)

migration_compensation_package = PackageKind(
    id_=3007,
    name=u'升级补偿礼包',
    distributor=SunnyWorld(3007),
    distribution_scope=CastKind.broadcast,
    coupon_wrappers=[
        CouponWrapper(rate_3_permillage, u'安心券', 1, expires_in=timedelta(days=7))
    ],
)

insurance_primary_package = PackageKind(
    id_=3008,
    name=u'保险专享 · 攒钱礼包',
    distributor=SpecialPrize(3008),
    coupon_wrappers=[
        CouponWrapper(
            deduction_500_cut_10, u'保险精选福利券', 1,
            regular_products, expires_at=date(2016, 2, 8)),
        CouponWrapper(
            deduction_1000_cut_20, u'保险精选福利券', 1,
            regular_products, expires_at=date(2016, 2, 8)),
    ],
)

insurance_medium_package = PackageKind(
    id_=3009,
    name=u'保险专享 · 攒钱礼包',
    distributor=SpecialPrize(3009),
    coupon_wrappers=[
        CouponWrapper(
            deduction_1000_cut_20, u'保险精选福利券', 1,
            regular_products, expires_at=date(2016, 2, 8)),
        CouponWrapper(
            deduction_5000_cut_100, u'保险精选福利券', 1,
            regular_products, expires_at=date(2016, 2, 8)),
    ],
)

insurance_best_package = PackageKind(
    id_=3010,
    name=u'保险专享 · 攒钱礼包',
    distributor=SpecialPrize(3010),
    coupon_wrappers=[
        CouponWrapper(
            deduction_1000_cut_20, u'保险精选福利券', 1,
            regular_products, expires_at=date(2016, 2, 8)),
        CouponWrapper(
            deduction_5000_cut_100, u'保险精选福利券', 2,
            regular_products, expires_at=date(2016, 2, 8)),
    ],
)

warm_dahan_package = PackageKind(
    id_=3011,
    name=u'大寒送温暖礼包',
    distributor=SpecialPrize(3011),
    distribution_scope=CastKind.broadcast,
    coupon_wrappers=[
        CouponWrapper(
            rate_2_permillage, u'大寒送温暖', 1, all_products,
            expires_in=timedelta(days=10)),
    ],
)

spring_2016_package = PackageKind(
    id_=3012,
    name=u'2016 新春礼包',
    distributor=SpecialPrize(3012),
    coupon_wrappers=[
        CouponWrapper(
            deduction_50000_cut_115, u'2016 新春礼包', 1, all_products,
            expires_in=timedelta(days=30)),
    ],
)
xinmi_compensation_package = PackageKind(
    id_=3013,
    name=u'购买补贴礼包',
    distributor=SunnyWorld(3013),
    distribution_scope=CastKind.broadcast,
    firewood_wrapper=FirewoodWrapper(
        'xinmi_invest', Decimal('0'), u'购买补贴', rate=Decimal('0.003'))
)
warm_heart_package = PackageKind(
    id_=3014,
    name=u'暖心加息礼包',
    distributor=SunnyWorld(3014),
    distribution_scope=CastKind.broadcast,
    coupon_wrappers=[
        CouponWrapper(
            rate_5_permillage, u'暖心加息券', 1, new_regular_products, expires_at=date(2016, 4, 22)),
        CouponWrapper(
            rate_5_permillage, u'暖心加息券', 1, new_regular_products, expires_at=date(2016, 4, 28))
    ],
)

zw_payback_delay_compensation_package = PackageKind(
    id_=3015,
    name=u'补贴礼包',
    distributor=SunnyWorld(3015),
    distribution_scope=CastKind.broadcast,
    firewood_wrapper=FirewoodWrapper(
        'zw_payback_delay', Decimal('10.0'), u'补贴')
)

# 历史遗留的礼包类型(8x)
gone_reserve_package = PackageKind(
    id_=80,
    name=u'预约礼包',
    distributor=LegacyRebate(80),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('reserve', Decimal('0'), u'预约福利')
)

gone_dtw_package = PackageKind(
    id_=81,
    name=u'2014双12礼包',
    distributor=LegacyRebate(81),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('double12', Decimal('0'), u'双12福利')
)

gone_poor_package = PackageKind(
    id_=82,
    name=u'比穷礼包',
    distributor=LegacyRebate(82),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('poorgame', Decimal('0'), u'比穷福利')
)

gone_sohu_package = PackageKind(
    id_=83,
    name=u'搜狐礼包',
    distributor=LegacyRebate(83),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('sohu', Decimal('0'), u'搜狐福利')
)

gone_common_coupon_package = PackageKind(
    id_=84,
    name=u'旧礼券福利礼包',
    distributor=LegacyRebate(84),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('yx_old_coupon', Decimal('0'), u'旧礼券福利')
)

gone_premium_coupon_package = PackageKind(
    id_=85,
    name=u'高级券福利礼包',
    distributor=LegacyRebate(85),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('yx_pro_coupon', Decimal('0'), u'高级券福利')
)

gone_promotion_bonus = PackageKind(
    id_=86,
    name=u'破亿福利礼包',
    distributor=LegacyRebate(86),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('yx_sse', Decimal('0'), u'破亿福利')
)

# 旧的邀请类红包类型，暂时关闭(9x)
gone_invite_register_invitor_package = PackageKind(
    id_=90,
    name=u'邀请注册礼包',
    distributor=LegacyRebate(90),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('invite_register', Decimal('0'), u'邀请注册奖')
)

gone_invitee_invest_invitee_package = PackageKind(
    id_=91,
    name=u'受邀投资礼包',
    distributor=LegacyRebate(91),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('invited_invest', Decimal('0'), u'受邀投资奖')
)

gone_invitee_invest_invitor_package = PackageKind(
    id_=92,
    name=u'邀请新人礼包',
    distributor=LegacyRebate(92),
    is_distributable=False,
    firewood_wrapper=FirewoodWrapper('invite_investor', Decimal('0'), u'邀请新人奖')
)


# 旧的触发式分发礼包
gone_newcomer_package = PackageKind(
    id_=1001,
    name=u'新手注册礼包',
    distributor=NewcomerCenter(1001),
    coupon_wrappers=[
        CouponWrapper(deduction_1000_cut_5, u'新人满减券', 1),
        CouponWrapper(deduction_5000_cut_30, u'新人满减券', 1),
        CouponWrapper(deduction_30000_cut_180, u'新人满减券', 1, longrun_products)
    ])

gone_first_purchase_package = PackageKind(
    id_=1002,
    name=u'普通产品首次投资礼包',
    distributor=MaidenInvestmentAward(1002),
    firewood_wrapper=FirewoodWrapper('first_purchase', Decimal('25.0'), u'首次投资奖'),
    coupon_wrappers=[
        CouponWrapper(deduction_50000_cut_260, u'新人投资券', 1, longrun_products)
    ]
)

gone_recast_inspire_package = PackageKind(
    id_=1003,
    name=u'首笔非新手标产品到期礼包',
    distributor=RecastInspirator(1003),
    coupon_wrappers=[
        CouponWrapper(rate_3_permillage, u'全场加息券', 1, expires_in=timedelta(days=7)),
        CouponWrapper(deduction_30000_cut_60, u'老手投资券', 1, longrun_products)
    ])

gone_newcomer_package_2015 = PackageKind(
    id_=1004,
    name=u'新手注册礼包',
    distributor=NewcomerCenter(1004),
    coupon_wrappers=[
        CouponWrapper(deduction_1000_cut_5, u'新人满减券', 1),
        CouponWrapper(deduction_5000_cut_30, u'新人满减券', 1),
        CouponWrapper(deduction_30000_cut_180, u'新人满减券', 1, midlong_products)
    ])

xinmi_invest_package = PackageKind(
    id_=1010,
    name=u'购买补贴礼包',
    distributor=XinmiInvestAward(1010),
    firewood_wrapper=FirewoodWrapper(
        'xinmi_invest', Decimal('0'), u'购买补贴', rate=Decimal('0.003'))
)

# 测试环境礼包(8xxx)
test_newcomer_center = PackageKind(
    id_=8001,
    name=u'测试新手注册礼包',
    distributor=NewcomerCenter(8001),
    coupon_wrappers=[
        CouponWrapper(deduction_1000_cut_5, u'测试新人满减券', 2),
        CouponWrapper(deduction_5000_cut_30, u'测试新人满减券', 2, midlong_products),
        CouponWrapper(deduction_30000_cut_180, u'测试新人满减券', 2),
        CouponWrapper(rate_3_permillage, u'测试新人加息券', 3, midlong_products)
    ])
