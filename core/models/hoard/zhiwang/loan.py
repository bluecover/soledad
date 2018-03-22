# coding:utf-8

import datetime
from decimal import Decimal

from zwlib.wrappers import AssetInvestInfoResponse

from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.hoard.zhiwang import ZhiwangAsset
from core.models.utils.types import unicode_type, date_type


class ZhiwangLoansDigest(PropsMixin):
    table_name = 'hoard_zhiwang_loans_digest'
    cache_key = 'hoard:zhiwang:loans_digest:id:{id_}:v1'
    cache_key_by_asset_id = 'hoard:zhiwang:loans_digest:asset_id:{asset_id}:v1'

    # 出借咨询与服务协议
    contract_no = PropsItem('contract_no', '', unicode_type)

    # 资金出借/回收方式
    reinvest = PropsItem('reinvest', '', unicode_type)

    # 申请出借金额
    plan_invest_amount = PropsItem('plan_invest_amount', 0, Decimal)

    # 实际出借金额
    principle_amount = PropsItem('principle_amount', 0, Decimal)

    # 剩余未出借金额
    surplus_amount = PropsItem('surplus_amount', 0, Decimal)

    # 借贷人人数
    total_count = PropsItem('total_count', 0, int)

    # 初始出借日期
    invest_start_date = PropsItem('invest_start_date', None, date_type)

    def __init__(self, id_, asset_id, creation_time):
        self.id_ = id_
        self.asset_id = asset_id
        self.creation_time = creation_time

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'zhiwang:loans_digest:{0}'.format(self.id_)

    @property
    def loans(self):
        return ZhiwangLoan.get_multi_by_loans_digest_id(self.id_)

    @classmethod
    def create(cls, asset, loans_digest_info):
        assert isinstance(asset, ZhiwangAsset)
        assert isinstance(loans_digest_info, AssetInvestInfoResponse)

        sql = 'insert into {.table_name} (asset_id, creation_time) values (%s, %s)'.format(cls)
        params = (asset.id_, datetime.datetime.now())

        id_ = db.execute(sql, params)
        db.commit()
        instance = cls.get(id_)

        instance._update_digest_info(loans_digest_info)

        # 创建借贷人记录
        loans = loans_digest_info.loans
        try:
            for loan in (loans or []):
                ZhiwangLoan.create(instance, loan, _commit=False)
        except:
            db.rollback()
            raise
        else:
            db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_asset_id(asset.id_)
        return instance

    @classmethod
    def update(cls, loans_digest, loans_digest_info):
        assert isinstance(loans_digest_info, AssetInvestInfoResponse)
        assert isinstance(loans_digest, ZhiwangLoansDigest)

        if loans_digest.contract_no == loans_digest_info.contract_no:
            loans_digest._update_digest_info(loans_digest_info)

            loans = loans_digest_info.loans
            if loans and len(loans) > len(loans_digest.loans):
                loan_receipt_no_list = [loan.loan_receipt_no for loan in loans_digest.loans]
                try:
                    for loan in loans:
                        if loan.loan_receipt_no not in loan_receipt_no_list:
                            ZhiwangLoan.create(loans_digest, loan, _commit=False)
                except:
                    db.rollback()
                    raise
                else:
                    db.commit()
        return loans_digest

    @classmethod
    def create_or_update(cls, asset, loans_digest_info):
        loans_digest = cls.get_by_asset_id(asset.id_)
        if loans_digest:
            return cls.update(loans_digest, loans_digest_info)
        else:
            return cls.create(asset, loans_digest_info)

    def _update_digest_info(self, loans_digest_info):
        self.update_props_items({
            'contract_no': loans_digest_info.contract_no,
            'reinvest': loans_digest_info.reinvest,
            'plan_invest_amount': str(loans_digest_info.plan_invest_amount),
            'principle_amount': str(loans_digest_info.principle_amount),
            'surplus_amount': str(loans_digest_info.surplus_amount),
            'total_count': loans_digest_info.total_count,
            'invest_start_date': str(loans_digest_info.invest_start_date)
        })

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = 'select id, asset_id, creation_time from {.table_name} where id=%s'.format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_key_by_asset_id)
    def get_id_by_asset_id(cls, asset_id):
        sql = 'select id from {.table_name} where asset_id=%s'.format(cls)
        params = (asset_id,)
        rs = db.execute(sql, params)
        if rs:
            return str(rs[0][0])

    @classmethod
    def get_by_asset_id(cls, asset_id):
        return cls.get(cls.get_id_by_asset_id(asset_id))

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_asset_id(cls, asset_id):
        mc.delete(cls.cache_key_by_asset_id.format(asset_id=asset_id))


class ZhiwangLoan(PropsMixin):
    table_name = 'hoard_zhiwang_loan'
    cache_key = 'hoard:zhiwang:loan:id:{id_}:v1'
    cache_key_by_loans_digest_id = 'hoard:zhiwang:loan:loans_digest_id:{loans_digest_id}'

    # 借款协议编号
    loan_receipt_no = PropsItem('loan_receipt_no', '', unicode_type)

    # 投资编号
    invest_id = PropsItem('invest_id', 0, int)

    # 借款人姓名
    debtor_name = PropsItem('debtor_name', '', unicode_type)

    # 借款人身份证号
    debtor_ricn = PropsItem('debtor_ricn', '', unicode_type)

    # 借款人身份
    debtor_type = PropsItem('debtor_type', '', unicode_type)

    # 借款用途
    debt_purpose = PropsItem('debt_purpose', '', unicode_type)

    # 借款金额
    lending_amount = PropsItem('lending_amount', 0, Decimal)

    # 借款人开始还款的日期
    start_date = PropsItem('start_date', None, date_type)

    def __init__(self, id_, loans_digest_id, creation_time):
        self.id_ = id_
        self.loans_digest_id = loans_digest_id
        self.creation_time = creation_time

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'zhiwang:loan:{0}'.format(self.id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, loans_digest_id, creation_time from {.table_name}'
               ' where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_key_by_loans_digest_id)
    def get_ids_by_loans_digest_id(cls, loans_digest_id):
        sql = 'select id from {.table_name} where loans_digest_id=%s'.format(cls)
        params = (loans_digest_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_multi_by_loans_digest_id(cls, loans_digest_id):
        return cls.get_multi(cls.get_ids_by_loans_digest_id(loans_digest_id))

    @classmethod
    def create(cls, loans_digest, loan, _commit=True):
        assert isinstance(loans_digest, ZhiwangLoansDigest)
        sql = 'insert into {.table_name} (loans_digest_id, creation_time) values(%s, %s)'.format(
            cls)
        params = (loans_digest.id_, datetime.datetime.now())
        id_ = db.execute(sql, params)

        if _commit:
            db.commit()
        instance = cls.get(id_)

        cls.clear_cache(id_)
        cls.clear_cache_by_loans_digest_id(loans_digest.id_)

        instance.update_props_items({
            'loan_receipt_no': loan.loan_receipt_no,
            'invest_id': loan.invest_id,
            'debtor_name': loan.debtor_name.encode('utf-8'),
            'debtor_ricn': loan.debtor_ricn.encode('utf-8'),
            'debtor_type': loan.debtor_type.encode('utf-8'),
            'debt_purpose': loan.debt_purpose.encode('utf-8'),
            'lending_amount': str(loan.lending_amount),
            'start_date': loan.start_date.isoformat()
        })
        return instance

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_loans_digest_id(cls, loans_digest_id):
        mc.delete(cls.cache_key_by_loans_digest_id.format(loans_digest_id=loans_digest_id))
