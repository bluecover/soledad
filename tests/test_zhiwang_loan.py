# coding:utf-8

from mock import Mock
from zwlib.wrappers import AssetInvestInfoResponse

from core.models.hoard.zhiwang import ZhiwangAsset
from core.models.hoard.zhiwang.loan import ZhiwangLoansDigest, ZhiwangLoan
from .framework import BaseTestCase


class ZhiwangLoansDigestTest(BaseTestCase):
    def setUp(self):
        super(ZhiwangLoansDigestTest, self).setUp()
        self.asset = Mock(spec=ZhiwangAsset)
        self.asset.id_ = 1

        self.loan = {
            'loan_receipt_no': 'P604010150408_I1304505',
            'bc_name': u'刘**',
            'debtor_identity_no': '320921********1445',
            'lending_amt': 20000,
            'debtor_type': u'经营人群',
            'debt_purpose': u'经营周转',
            'start_date': '20150831',
            'invest_id': 2
        }

        _fake_loans_digest = {
            'contract_no': 'QXF201508061001001023187556',
            'invest_start_date': '20150810',
            'reinvest': u'零投',
            'plan_invest_amount': 20000,
            'principle_amount': 20000,
            'surplus_amount': 0,
            'total_count': 1,
            'loans': [self.loan]
        }

        self.fake_loans_digest = AssetInvestInfoResponse(_fake_loans_digest)
        self.loans_digest = ZhiwangLoansDigest.create(self.asset, self.fake_loans_digest)

    def tearDown(self):
        super(ZhiwangLoansDigestTest, self).tearDown()

    def test_zhiwang_loans_digest(self):
        assert isinstance(self.loans_digest, ZhiwangLoansDigest)
        assert self.loans_digest.asset_id == self.asset.id_
        assert self.loans_digest.contract_no == self.fake_loans_digest.contract_no
        assert len(self.loans_digest.loans) == 1

    def test_get_by_asset_id(self):
        loans_digest = ZhiwangLoansDigest.get_by_asset_id(self.asset.id_)
        assert loans_digest.asset_id == self.asset.id_

        loans_digest_loans = self.loans_digest.loans
        for loan in loans_digest_loans:
            assert isinstance(loan, ZhiwangLoan)
            assert loan.loans_digest_id == self.loans_digest.id_
            assert loan.debtor_name == self.loan.get('bc_name')

    def test_update(self):
        _fake_loans_digest = {
            'contract_no': 'QXF201508061001001023187556',
            'invest_start_date': '20150810',
            'reinvest': u'零投',
            'plan_invest_amount': 50000,
            'principle_amount': 20000,
            'surplus_amount': 0,
            'total_count': 1,
            'loans': [{
                'loan_receipt_no': 'P604010150408_I1304506',
                'bc_name': u'刘**',
                'debtor_identity_no': '320921********1445',
                'lending_amt': 80000,
                'debtor_type': u'经营人群',
                'debt_purpose': u'经营周转',
                'start_date': '20150831',
                'invest_id': 2
            }, self.loan]
        }
        assert len(self.loans_digest.loans) == 1
        fake_loans_digest = AssetInvestInfoResponse(_fake_loans_digest)
        loans_digest = ZhiwangLoansDigest.update(self.loans_digest, fake_loans_digest)
        assert len(loans_digest.loans) == 2
