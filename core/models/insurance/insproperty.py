# coding: utf-8

from core.models.mixin.props import PropsMixin, PropsItem
from .consts import (PACKAGE_BASIC, PACKAGE_ACCIDENT)
from .consts import (INS_SUB_TITLE_NUMBER_10, INS_SUB_TITLE_NUMBER_20)
from .consts import (MALE, FEMALE)
from .age import Age


class InsProperty(PropsMixin):
    feerate = PropsItem('feerate', {})
    rec_reason = PropsItem('rec_reason', '')
    buy_url = PropsItem('buy_url')
    ins_title = PropsItem('ins_title')
    ins_sub_title = PropsItem('ins_sub_title', 'ins_sub_title')

    def __init__(self, insurance_id, kind):
        self.id = insurance_id
        self.kind = kind
        self._age = None

    def get_db(self):
        return 'insure_fee_rate'

    def get_uuid(self):
        return 'insure_fee_rate:insure:%s' % self.id

    def get_ins_sub_title(self, package_id, insurance_id):
        return self.ins_sub_title

    def add_props(self, feerate, rec_reason, buy_url, ins_title, ins_sub_title):
        self.feerate = feerate
        self.rec_reason = rec_reason
        self.buy_url = buy_url
        self.ins_title = ins_title
        self.ins_sub_title = ins_sub_title

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, ageobj):
        self._age = ageobj


class PropertyComprenhensiveInsurance(InsProperty):
    def get(self, package_id, **kwargs):
        birthday = kwargs['birthday'] if 'birthday' in kwargs else None

        if birthday is None:
            return

        if self.feerate is None:
            return

        self.age = Age(birthday)
        year, days = self.age.birth

        for fee in self.feerate:
            if int(year) == 0:
                if (
                    int(days) >= int(fee['start_age'][0:-1]) and
                    fee['start_age'][-1] == 'D'
                ):
                    return fee['fee'] if fee['fee'] else None
                else:
                    return
            else:
                if (
                    int(year) <= int(fee['end_age'][0:-1]) and
                    (fee['start_age'][-1] == 'D' or
                     int(year) >= int(fee['start_age'][0:-1]))
                ):
                    return fee['fee'] if fee['fee'] else None
        return


class PropertyCriticalInsurance(InsProperty):

    def get_ins_sub_title(self, package_id, insurance_id):
        if package_id in [PACKAGE_BASIC, PACKAGE_ACCIDENT]:
            return self.ins_sub_title % (INS_SUB_TITLE_NUMBER_10)
        return self.ins_sub_title % (INS_SUB_TITLE_NUMBER_20)

    def get(self, package_id, **kwargs):
        ill = kwargs['ill'] if 'ill' in kwargs else None
        gender = kwargs['gender'] if 'gender' in kwargs else None
        birthday = kwargs['birthday'] if 'birthday' in kwargs else None

        if (ill is None or gender is None or
                birthday is None):
            return

        gender = MALE if gender == '1' else FEMALE
        disease = int(ill)

        coverage = 1
        if package_id not in [PACKAGE_BASIC, PACKAGE_ACCIDENT]:
            coverage = 2
        if self.feerate is None:
            return
        self.age = Age(birthday)
        year, days = self.age.birth
        for rate in self.feerate:
            if (
                rate['gender'] == gender and
                int(rate['age'][0:-1]) == int(year) and
                rate['ill'] == disease
            ):
                return (int(rate['fee']) * coverage if rate['fee'] else None)
        return


class PropertyEducationInsurance(InsProperty):
    def get(self, package_id, **kwargs):
        birthday = kwargs['birthday'] if 'birthday' in kwargs else None
        coverage = kwargs['coverage'] if 'coverage' in kwargs else None

        if coverage is None or birthday is None:
            return

        if coverage in ['a1', 'b1', 'c1']:
            coverage = 'low'
        elif coverage in ['a2', 'b2', 'c2']:
            coverage = 'medium'
        elif coverage in ['a3', 'b3', 'c3']:
            coverage = 'high'
        else:
            return

        if self.feerate is None:
            return
        self.age = Age(birthday)
        year, days = self.age.birth
        for fee in self.feerate:
            if (
                int(fee['age'][0:-1]) == int(year) and
                fee['coverage'] == coverage
            ):
                return fee['fee'] if fee['fee'] else None
        return
