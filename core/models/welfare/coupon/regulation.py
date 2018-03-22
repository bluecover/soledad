# coding: utf-8

from enum import Enum


class CouponRegulation(object):
    """
    礼券规则

    """
    class Kind(Enum):
        annual_rate_supplement = 'RS'
        quota_deduction = 'QD'

    Kind.annual_rate_supplement.sequence = 0
    Kind.annual_rate_supplement.label = u'满减券'
    Kind.quota_deduction.sequence = 1
    Kind.quota_deduction.label = u'加息券'

    def __init__(self, kind):
        self.kind = kind

    def is_available_for_order(self, amount):
        """订单是否符合礼券规则，暂时只支持金额判断"""
        raise NotImplementedError

    @property
    def sort_key(self):
        return (self.kind.sequence, self.quantifier)

    @property
    def display_regulation(self):
        """礼券规则名称"""
        return self.kind.label

    @property
    def benefit_dict(self):
        """用户奖励字典"""
        raise NotImplementedError

    @property
    def display_benefit(self):
        """用户使用礼券所获利好"""
        raise NotImplementedError

    @property
    def usage_requirement_dict(self):
        """用户使用礼券的限制条件字典（供前端）"""
        raise NotImplementedError

    @property
    def display_usage_requirement(self):
        """用户使用礼券的前提"""
        raise NotImplementedError


class QuotaDeductionRegulation(CouponRegulation):
    mapped_kind = CouponRegulation.Kind.quota_deduction

    def __init__(self, fulfill_quota, deduct_quota):
        super(QuotaDeductionRegulation, self).__init__(self.mapped_kind)
        self.fulfill_quota = fulfill_quota
        self.deduct_quota = deduct_quota

        if fulfill_quota != 0 and deduct_quota > fulfill_quota:
            raise ValueError('invalid deduction %s(%s)' % (deduct_quota, fulfill_quota))

    @property
    def quantifier(self):
        return self.fulfill_quota

    @property
    def benefit_detail(self):
        return (u'减', self.deduct_quota, u'元')

    @property
    def benefit_dict(self):
        return dict(deduct_amount=self.deduct_quota)

    @property
    def display_benefit(self):
        return u'减%s元' % self.deduct_quota

    @property
    def usage_requirement_dict(self):
        return dict(fulfill_amount=self.fulfill_quota)

    @property
    def display_usage_requirement(self):
        return u'满%s元' % self.fulfill_quota

    def is_available_for_order(self, amount):
        """满减券要求订单金额高于满减要求"""
        return amount >= self.fulfill_quota


class AnnualRateSupplementRegulation(CouponRegulation):
    mapped_kind = CouponRegulation.Kind.annual_rate_supplement

    def __init__(self, supply_rate):
        super(AnnualRateSupplementRegulation, self).__init__(self.mapped_kind)
        self.supply_rate = supply_rate

    @property
    def quantifier(self):
        return self.supply_rate

    @property
    def benefit_detail(self):
        return ('+', self.supply_rate, '%')

    @property
    def benefit_dict(self):
        return dict(extra_rate=self.supply_rate)

    @property
    def display_benefit(self):
        return u'年化收益率+%s%%' % self.supply_rate

    @property
    def usage_requirement_dict(self):
        return dict()

    @property
    def display_usage_requirement(self):
        return u''

    def is_available_for_order(self, amount):
        return True
