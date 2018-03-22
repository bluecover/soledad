# coding:utf-8

import datetime
from decimal import Decimal

from xmlib.wrappers import CreditorRights

from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.hoard.xinmi import XMAsset
from core.models.utils.types import unicode_type, date_type


class XMLoansDigest(PropsMixin):
    table_name = 'hoard_xm_loans_digest'
    cache_key = 'hoard:xm:loans_digest:id:{id_}:v1'
    cache_key_by_asset_id = 'hoard:xm:loans_digest:asset_id:{asset_id}:v1'

    # 出借咨询与服务协议
    contract_no = PropsItem('contract_no', '', unicode_type)

    # 资金出借/回收方式
    reinvest = PropsItem('reinvest', '', unicode_type)

    # 实际出借金额
    principle_amount = PropsItem('principle_amount', 0, Decimal)

    # 协议与债权占比（持有比例）
    receipt_hold_scale = PropsItem('receipt_hold_scale', 0, Decimal)

    # 初始出借日期
    invest_start_date = PropsItem('invest_start_date', '', date_type)

    def __init__(self, id_, asset_id, creation_time):
        self.id_ = id_
        self.asset_id = asset_id
        self.creation_time = creation_time

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'xm:loans_digest:{0}'.format(self.id_)

    @property
    def loans(self):
        return XMLoan.get_multi_by_loans_digest_id(self.id_)

    @classmethod
    def create(cls, asset, loans_digest_info):
        assert isinstance(asset, XMAsset)
        assert isinstance(loans_digest_info, CreditorRights)

        sql = 'insert into {.table_name} (asset_id, creation_time) values (%s, %s)'.format(cls)
        params = (asset.id_, datetime.datetime.now())

        id_ = db.execute(sql, params)
        db.commit()
        instance = cls.get(id_)

        instance.update_props_items({
            'contract_no': loans_digest_info['loan_receipt_no'],
            'reinvest': loans_digest_info['invest_lending_type'],
            'principle_amount': str(loans_digest_info['loan_receipt_amt']),
            'receipt_hold_scale': loans_digest_info['receipt_hold_scale'],
            'invest_start_date': loans_digest_info.start_date.isoformat()
        })

        # 创建借贷人记录
        loans = loans_digest_info
        try:
            XMLoan.create(instance, loans, _commit=False)
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
        assert isinstance(loans_digest_info, CreditorRights)
        assert isinstance(loans_digest, XMLoansDigest)

        loans = loans_digest_info.loans
        if len(loans) > len(loans_digest.loans):
            loan_receipt_no_list = [loan.loan_receipt_no for loan in loans_digest.loans]
            try:
                for loan in loans:
                    if loan.loan_receipt_no not in loan_receipt_no_list:
                        XMLoan.create(loans_digest, loan, _commit=False)
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


class XMLoan(PropsMixin):
    table_name = 'hoard_xm_loan'
    cache_key = 'hoard:xm:loan:id:{id_}:v1'
    cache_key_by_loans_digest_id = 'hoard:xm:loan:loans_digest_id:{loans_digest_id}'

    # 借款协议编号
    loan_receipt_no = PropsItem('loan_receipt_no', '', unicode_type)

    # 投资编号
    invest_id = PropsItem('invest_id', '', int)

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
    start_date = PropsItem('start_date', '', date_type)

    def __init__(self, id_, loans_digest_id, creation_time):
        self.id_ = id_
        self.loans_digest_id = loans_digest_id
        self.creation_time = creation_time

    def get_db(self):
        return 'hoard'

    def get_uuid(self):
        return 'xm:loan:{0}'.format(self.id_)

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
    def create(cls, loans_digest, loans, _commit=True):
        assert isinstance(loans_digest, XMLoansDigest)
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
            'loan_receipt_no': loans.loan_receipt_no,
            'invest_id': loans.order_id,
            'debtor_name': loans.bc_name,
            'debtor_ricn': loans.debtor_identity_no,
            'debtor_type': loans.debtor_type,
            'debt_purpose': loans.debt_desc,
            'lending_amount': str(loans.loan_receipt_amt),
            'start_date': loans.start_date.isoformat()
        })
        return instance

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_loans_digest_id(cls, loans_digest_id):
        mc.delete(cls.cache_key_by_loans_digest_id.format(loans_digest_id=loans_digest_id))
