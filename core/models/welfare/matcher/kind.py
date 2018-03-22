# coding: utf-8

from weakref import WeakValueDictionary

from core.models.base import EntityModel
from core.models.hoard.common import ProfitPeriod
from core.models.hoard.providers import zhiwang, xmpay
from .matcher import ProductMatcher, FixedClosureMatcher


class ProductMatcherKind(EntityModel):

    storage = WeakValueDictionary()

    def __init__(self, id_, matcher):
        if id_ in self.storage:
            raise ValueError('id %r has been used' % id_)

        self.id_ = id_
        # 产品匹配器
        self.matcher = matcher
        self.storage[id_] = self

    @classmethod
    def get(cls, id_):
        return cls.storage.get(id_)


all_products = ProductMatcherKind(
    id_=100,
    matcher=ProductMatcher(
        u'固定期限产品可用 (新手专享除外)',
        (zhiwang, xmpay)),
)

regular_products = ProductMatcherKind(
    id_=101,
    matcher=FixedClosureMatcher(
        u'仅限90、180、270、365天产品可用',
        (zhiwang, xmpay),
        (
            ProfitPeriod(90, 'day'),
            ProfitPeriod(180, 'day'),
            ProfitPeriod(270, 'day'),
            ProfitPeriod(365, 'day')
        )
    )
)

midlong_products = ProductMatcherKind(
    id_=102,
    matcher=FixedClosureMatcher(
        u'仅限180、270天、365天产品可用',
        (zhiwang, xmpay),
        (
            ProfitPeriod(180, 'day'),
            ProfitPeriod(270, 'day'),
            ProfitPeriod(365, 'day')
        )
    )
)


longrun_products = ProductMatcherKind(
    id_=110,
    matcher=FixedClosureMatcher(
        u'仅限270天、365天产品可用',
        (zhiwang, xmpay),
        (
            ProfitPeriod(270, 'day'),
            ProfitPeriod(365, 'day')
        )
    )
)


shortrun_products = ProductMatcherKind(
    id_=111,
    matcher=FixedClosureMatcher(
        u'仅限90天产品可用',
        (zhiwang, xmpay),
        (
            ProfitPeriod(90, 'day'),
        )
    )
)

new_regular_products = ProductMatcherKind(
    id_=112,
    matcher=FixedClosureMatcher(
        u'仅限90、180、365天产品可用',
        (xmpay, ),
        (
            ProfitPeriod(90, 'day'),
            ProfitPeriod(180, 'day'),
            ProfitPeriod(365, 'day')
        )
    )
)
