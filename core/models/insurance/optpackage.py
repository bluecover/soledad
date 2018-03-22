# coding: utf-8

import itertools

from libs.db.store import db
from libs.cache import mc
from core.models import errors
from core.models.insurance.program import Program
from core.models.mixin.props import PropsMixin
from core.models.insurance.packages import Package
from core.models.insurance.order import Order
from .consts import BALANCE, MEDICAL, DISEASE, ACCIDENT
from .consts import RECOMMEND, BACKUP
from .consts import MEDICAL_WITH_SOCIAL_INSURANCE
from .consts import (PACKAGE_NO, PACKAGE_BASIC, PACKAGE_MEDICAL,
                     PACKAGE_ACCIDENT, PACKAGE_DISEASE,
                     PACKAGE_UPGRADE_1, PACKAGE_UPGRADE_2)
from .consts import HAS_SOCIAL_INSURANCE, HAS_SUPPLEMENT


MC_TOTAL_INSURANCE_USER_COUNT = 'insurance:user:amount:v2'


class OptPackage(PropsMixin):

    will_package_map = {
        BALANCE: {RECOMMEND: PACKAGE_BASIC,
                  BACKUP: [PACKAGE_UPGRADE_1, PACKAGE_UPGRADE_2]},
        MEDICAL_WITH_SOCIAL_INSURANCE: {RECOMMEND: PACKAGE_ACCIDENT,
                                        BACKUP: [PACKAGE_NO]},
        MEDICAL: {RECOMMEND: PACKAGE_MEDICAL, BACKUP: [PACKAGE_BASIC]},
        DISEASE: {RECOMMEND: PACKAGE_DISEASE, BACKUP: [PACKAGE_BASIC]},
        ACCIDENT: {RECOMMEND: PACKAGE_ACCIDENT,
                   BACKUP: [PACKAGE_UPGRADE_1, PACKAGE_UPGRADE_2]}
    }

    def get_uuid(self):
        return 'insurance:secret:child:data:%s' % self.id

    def get_db(self):
        return 'insurance_child_data'

    def __init__(self, id, user_id, status, create_time, update_time):
        self.id = str(id)
        self.user_id = str(user_id)
        self.status = status
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<ChildInsurancePlan id=%s, user_id=%s>' % (self.id,
                                                           self.user_id)

    @property
    def user(self):
        from core.models.user.account import Account
        return Account.get(self.user_id)

    @classmethod
    def get_total_ins_children_count(cls):
        sql = ('select count(account_id) '
               'from insurance_profile ')
        rs = db.execute(sql)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_plan_data(cls, user_id, will_id,
                         birthday, ill, gender, coverage, socical_insurance,
                         supplement, edu):

        if will_id == MEDICAL_WITH_SOCIAL_INSURANCE:
            if (socical_insurance != HAS_SOCIAL_INSURANCE or
                    supplement != HAS_SUPPLEMENT):
                will_id = MEDICAL

        recommend_package_id = cls.will_package_map[will_id][RECOMMEND]
        backup_package_ids = cls.will_package_map[will_id][BACKUP]
        packages = {RECOMMEND: Package.get(recommend_package_id),
                    BACKUP: [Package.get(backup_package_id)
                             for backup_package_id in backup_package_ids]}
        recommend_packages = packages[RECOMMEND]
        backup_packages = packages[BACKUP]
        program = Program()
        quota = program.quota[str(will_id)]
        order_id = 'order_id'
        recommend_insurances = []

        for recommend_package in recommend_packages:
            insurance_order = Order(
                user_id, order_id, recommend_package.id,
                recommend_package.insurance_id)

            insurance_order.age = birthday
            ability = recommend_package.cat_ability(insurance_order.age)
            rate = insurance_order.rate(
                birthday=birthday, ill=ill,
                gender=gender, coverage=coverage,
                socical_insurance=socical_insurance,
                supplement=supplement,
                edu=edu)

            ins_sub_title = insurance_order.ins_sub_title()
            if rate is not None:
                ins = insurance_order.insurance
                recommend_insurances.append(
                    {'insurance_id': ins.id,
                     'quota': quota,
                     'insurance_name': ins.name,
                     'rec_reason': ins.ins_property.rec_reason,
                     'buy_url': ins.ins_property.buy_url,
                     'ins_title': ins.ins_property.ins_title,
                     'ins_sub_title': ins_sub_title,
                     'rate': rate,
                     'package_id': recommend_package.id,
                     'ability': ability,
                     'rec_rank': recommend_package.rec_rank_in_package})
        backup_insurances = []
        for backup_package in backup_packages:
            for backup in backup_package:
                insurance_order = Order(
                    user_id, order_id, backup.id,
                    backup.insurance_id)

                insurance_order.age = birthday
                rate = insurance_order.rate(
                    birthday=birthday, ill=ill,
                    gender=gender, coverage=coverage,
                    socical_insurance=socical_insurance,
                    supplement=supplement,
                    edu=edu)

                ins_sub_title = insurance_order.ins_sub_title()

                ability = backup.cat_ability(insurance_order.age)
                if rate is not None:
                    ins = insurance_order.insurance
                    backup_insurances.append(
                        {'insurance_id': ins.id,
                         'insurance_name': ins.name,
                         'rec_reason': ins.ins_property.rec_reason,
                         'buy_url': ins.ins_property.buy_url,
                         'ins_title': ins.ins_property.ins_title,
                         'ins_sub_title': ins_sub_title,
                         'rate': rate,
                         'package_id': backup.id,
                         'ability': ability,
                         'rec_rank': backup.rec_rank_in_package})
        return packages, recommend_insurances, backup_insurances


class InvalidFormulaKeyError(Exception):
    pass


class Calculator():

    def __init__(self, data, user_id, will_id):
        self.data = data
        self.user_id = user_id
        self.will_id = will_id

    @classmethod
    def get_by_plan_data(cls, data, user_id, will_id):
        if data and isinstance(data, dict):
            return cls(data, user_id, int(will_id))

    def execute(self):
        data = self.data['children']
        birthday = data.get('birthdate')
        ill = data.get('child_genetic')
        gender = data.get('gender')
        coverage = None
        socical_insurance = data.get('child_medicare')
        supplement = data.get('childins_supplement')
        edu = data.get('child_edu')
        if edu == '1':
            coverage = data.get('project')

        return OptPackage.get_by_plan_data(self.user_id,
                                           self.will_id, birthday,
                                           ill, gender, coverage,
                                           socical_insurance,
                                           supplement,
                                           edu)


def gen_result(profile, force=True):
    if not profile.result_data:
        return errors.err_none_plan_data

    result_data = profile.result_data
    if ((result_data.get('recommend') or result_data.get('backup')) and not force):
        return errors.err_ok
    calculator = Calculator.get_by_plan_data(
        {'children': result_data.get('children')},
        profile.user_id, result_data.get('will'))
    _, recommend_ins, backup_ins = calculator.execute()

    if recommend_ins is None:
        recommend_ins = {}
    result_data['recommend'] = recommend_ins
    if backup_ins is None:
        backup_ins = {}
    result_data['backup'] = backup_ins
    profile.result_data = result_data
    return errors.err_ok


def find_second_minum(insurances, key):
    ins_sorted = sorted(insurances, key=lambda x: x['rec_rank'])
    minum = ins_sorted[0][key]

    if minum != 0:
        return [0, minum]

    second = minum
    for ins in ins_sorted:
        if ins[key] > minum:
            second = ins[key]
            break
    return [minum, second]


def get_result(profile):
    recommend_ins = profile.result_data.get('recommend')
    backup_insurance = profile.result_data.get('backup')

    rec_selected = find_second_minum(recommend_ins, 'rec_rank')
    rec_ins = [insurance for insurance in recommend_ins
               if insurance['rec_rank'] in rec_selected]

    backup_ins = []
    rec_ins_group = (dict([(g, list(k)) for g, k in itertools.groupby(
        backup_insurance, lambda x:x['package_id'])]))
    for backup_ins_key in rec_ins_group:
        backup = rec_ins_group[backup_ins_key]
        backup_selected = find_second_minum(backup,
                                            'rec_rank')
        backup_ins_sub = [insurance for insurance in backup
                          if insurance['rec_rank'] in backup_selected]
        backup_ins.extend(backup_ins_sub)
    backups = sorted(backup_ins, key=lambda x: x['package_id'])
    return rec_ins, backups


def set_total_ins_children_count():
    """set total user count who buy children insurance"""
    mc.set(MC_TOTAL_INSURANCE_USER_COUNT, get_total_ins_children_count()+1)


def get_total_ins_children_count():
    """get total user count who buy children insurance"""
    return mc.get(MC_TOTAL_INSURANCE_USER_COUNT) or 1
