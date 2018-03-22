# coding: utf-8

from solar.utils.storify import storify

from jupiter.utils import get_repository_root
from core.models.product.consts import P2P_TYPE
from core.models.product.fund import Fund
from core.models.product.p2p import P2P
from core.models.product.insure import Insure


fund = storify(dict(
    name=0,
    type=1,
    organization=2,
    code=3,
    found_date=4,
    index=5,
    risk=6,
    manager=7,
    year_rate=8,
    nickname=9,
    rec_reason=10,
    rec_rank=11,
    link=12,
    phone=13,
))

p2p = storify(dict(
    name=0,
    organization=1,
    year_rate=2,
    pay_return_type=3,
    deadline=4,
    min_money=5,
    protect=6,
    rec_reason=7,
    rec_rank=8,
    link=9,
    phone=10,
))


insure = storify(dict(
    name=0,
    organization=1,
    type=2,
    duration=3,
    pay_duration=4,
    insure_duty=5,
    throng=6,
    prospect=7,
    rec_reason=8,
    rec_rank=9,
    link=10,
    phone=11,
))


def parse_p2p(path):
    with open(path) as f:
        d = f.read()
        lines = d.split('\n')
        for l in lines[2:]:
            s = l.split(',')
            id = P2P.add(P2P_TYPE.P2P, s[p2p.rec_rank])
            i = P2P.get(id)
            i.name = s[p2p.name]
            i.organization = s[p2p.organization]
            i.year_rate = s[p2p.year_rate]
            i.pay_return_type = s[p2p.pay_return_type]
            i.deadline = s[p2p.deadline]
            i.min_money = s[p2p.min_money]
            i.protect = s[p2p.protect]
            i.rec_reason = s[p2p.rec_reason]
            i.link = s[p2p.link]
            i.phone = s[p2p.phone]


def parse_fund(path):
    with open(path) as f:
        d = f.read()
        lines = d.split('\n')
        for l in lines[2:]:
            s = l.split(',')
            id = Fund.add(s[fund.type], s[fund.rec_rank])
            i = Fund.get(id)
            i.name = s[fund.name]
            i.code = s[fund.code]
            i.organization = s[fund.organization]
            i.found_date = s[fund.found_date]
            i.index = s[fund.index]
            i.risk = s[fund.risk]
            i.manager = s[fund.manager]
            i.year_rate = s[fund.year_rate]
            i.nickname = s[fund.nickname]
            i.rec_reason = s[fund.rec_reason]
            i.link = s[fund.link]
            i.phone = s[fund.phone]


def parse_insure(path):
    with open(path) as f:
        d = f.read()
        lines = d.split('\n')
        for l in lines[2:]:
            s = l.split(',')
            id = Insure.add(s[insure.type], s[insure.rec_rank])
            i = Insure.get(id)
            i.name = s[insure.name]
            i.organization = s[insure.organization]
            i.duration = s[insure.duration]
            i.pay_duration = s[insure.pay_duration]
            i.insure_duty = s[insure.insure_duty]
            i.throng = s[insure.throng]
            i.prospect = s[insure.prospect]
            i.rec_reason = s[insure.rec_reason]
            i.link = s[insure.link]
            i.phone = s[insure.phone]


if __name__ == '__main__':
    print 'start parse fund'
    parse_fund('%s/tests/init/fund.csv' % get_repository_root())
    print 'start parse insure'
    parse_insure('%s/tests/init/insure.csv' % get_repository_root())
    print 'start parse p2p'
    parse_p2p('%s/tests/init/p2p.csv' % get_repository_root())
