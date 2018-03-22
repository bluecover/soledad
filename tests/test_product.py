# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.product.consts import (RISK_RANK, PRODUCT_STATUS, P2P_TYPE,
                                        BANK_TYPE, DEBT_TYPE, FUND_TYPE,
                                        INSURE_TYPE, DEBT_PAY_TYPE)
from core.models.product.p2p import P2P
from core.models.product.bank import Bank
from core.models.product.debt import Debt
from core.models.product.fund import Fund
from core.models.product.insure import Insure


class ProductTest(BaseTestCase):

    def test_add_p2p(self):
        p = P2P.add(P2P_TYPE.P2P)
        p = P2P.get(p)
        assert p

        p.delete()
        p = P2P.get(p.id)
        assert p.status == PRODUCT_STATUS.OFF

        rs = P2P.get_all()
        ids = [r.id for r in rs]
        assert p.id not in ids

        p.publish()
        p = P2P.get(p.id)
        assert p.status == PRODUCT_STATUS.ON
        rs = P2P.get_all()
        ids = [r.id for r in rs]
        assert p.id in ids

    def test_update_p2p(self):
        p = P2P.add(P2P_TYPE.P2P)
        p = P2P.get(p)
        assert not p.name
        assert not p.organization
        assert not p.year_rate

        p.update(name='p2p', organization='haoguihua', year_rate=1)
        assert p.name == 'p2p'
        assert p.organization == 'haoguihua'
        assert p.year_rate == 1

    def test_add_bank(self):
        p = Bank.add('bank', BANK_TYPE.BANK, RISK_RANK.LOW, 0.1,
                     30000, '20130101', '20131230',
                     PRODUCT_STATUS.ON, 'xxxx', '1',
                     'www.guihua.com', '12333333')
        assert p
        assert p.name == 'bank'
        assert p.earning == 0.1
        assert p.rec_reason == 'xxxx'

        p = p.update('bank2', BANK_TYPE.BANK, RISK_RANK.LOW, 0.1,
                     30000, '20130101', '20131230', 'xxxx', '1',
                     'www.guihua.com', '12333333')
        assert p.name == 'bank2'

        p.delete()
        p = Bank.get(p.id)
        assert p.status == PRODUCT_STATUS.OFF

        rs = Bank.get_all()
        ids = [r.id for r in rs]
        assert p.id not in ids

        p.publish()
        p = Bank.get(p.id)
        assert p.status == PRODUCT_STATUS.ON
        rs = Bank.get_all()
        ids = [r.id for r in rs]
        assert p.id in ids

    def test_add_debt(self):
        p = Debt.add('debt', DEBT_TYPE.CERTIFICATE, RISK_RANK.LOW, 0.06,
                     30000, 3 * 365, DEBT_PAY_TYPE.DISPOSE_ALL,
                     PRODUCT_STATUS.ON, 'xxxx', '1',
                     'www.guihua.com', '12333333')
        assert p
        assert p.name == 'debt'
        assert p.rate == 0.06
        assert p.pay_type == DEBT_PAY_TYPE.DISPOSE_ALL
        assert p.rec_reason == 'xxxx'

        p = p.update('debt1', DEBT_TYPE.CERTIFICATE, RISK_RANK.LOW, 0.06,
                     30000, 3 * 365, DEBT_PAY_TYPE.DISPOSE_ALL, 'xxxx', '1',
                     'www.guihua.com', '12333333')
        assert p.name == 'debt1'

        p.delete()
        p = Debt.get(p.id)
        assert p.status == PRODUCT_STATUS.OFF

        rs = Debt.get_all()
        ids = [r.id for r in rs]
        assert p.id not in ids

        p.publish()
        p = Debt.get(p.id)
        self.assertEqual(p.status, PRODUCT_STATUS.ON)
        rs = Debt.get_all()
        ids = [r.id for r in rs]
        assert p.id in ids

    def test_add_fund(self):
        p = Fund.add(FUND_TYPE.MMF)
        p = Fund.get(p)
        assert p

        p.delete()
        p = Fund.get(p.id)
        assert p.status == PRODUCT_STATUS.OFF

        rs = Fund.get_all()
        ids = [r.id for r in rs]
        assert p.id not in ids

        p.publish()
        p = Fund.get(p.id)
        assert p.status == PRODUCT_STATUS.ON
        ids = [r.id for r in Fund.get_all()]
        assert p.id in ids

    def test_update_fund(self):
        p = Fund.add(FUND_TYPE.MMF)
        p = Fund.get(p)
        assert not p.name
        assert not p.organization
        assert not p.code

        p.update(name='fund', organization='haoguihua', code='YANZI')
        assert p.name == 'fund'
        assert p.organization == 'haoguihua'
        assert p.code == 'YANZI'

    def test_insure(self):
        p = Insure.add(INSURE_TYPE.LIFE)
        p = Insure.get(p)
        assert p

        p.delete()
        p = Insure.get(p.id)
        assert p.status == PRODUCT_STATUS.OFF

        rs = Insure.get_all()
        ids = [r.id for r in rs]
        assert p.id not in ids

        p.publish()
        p = Insure.get(p.id)
        assert p.status == PRODUCT_STATUS.ON
        rs = Insure.get_all()
        ids = [r.id for r in rs]
        assert p.id in ids

    def test_update_insure(self):
        p = Insure.add(INSURE_TYPE.LIFE)
        p = Insure.get(p)
        assert not p.name
        assert not p.organization
        assert not p.duration

        p.update(name='p2p', organization='haoguihua', duration='30')
        assert p.name == 'p2p'
        assert p.organization == 'haoguihua'
        assert p.duration == '30'
