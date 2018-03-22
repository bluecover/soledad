# -*- coding:utf-8 -*-

from .framework import BaseTestCase
from core.models.insurance.insurance import Insurance
# from core.models.insurance.packages import Package
from core.models.insurance.order import Order


class InsuranceTest(BaseTestCase):

    def test_insurance_oder_age_property(self):
        insurance_order = Order(1, 2, 3, 1)
        self.assertEqual(insurance_order.age, None)
        insurance_order.age = '2014-03-01'
        self.assertEqual(insurance_order.age.birth[0], 2)

    def test_insurance_oder_coverage_property(self):
        insurance_order = Order(1, 2, 3, 1)
        self.assertEqual(insurance_order.coverage, 10)
        insurance_order.coverage = 20
        self.assertEqual(insurance_order.coverage, 20)

    def test_insurance_oder_insurace_property(self):
        item = [
            {'start_age': '60D', 'end_age': '6Y',  'fee': 480}
            ]
        comprehensive_insurance_obj = Insurance.get(1)
        comprehensive_insurance_obj.ins_property.feerate = item

        insurance_order = Order(1, 2, 3, 1)
        fee = insurance_order.insurance.get_fee(1, birthday='2013-03-01')
        self.assertEqual(fee, 480)

        self.assertEqual(item == insurance_order.insurance.ins_property.feerate,
                         True)

    def test_insurance_oder_rate_property(self):
        item = [
            {'start_age': '60D', 'end_age': '6Y',  'fee': 480}
            ]
        comprehensive_insurance_obj = Insurance.get(1)
        comprehensive_insurance_obj.ins_property.feerate = item

        insurance_order = Order(1, 2, 3, 1)
        insurance_order.rate(birthday='2013-03-01')
        self.assertEqual(insurance_order.rate(birthday='2013-03-01'), 480)

    def test_get_comprehensive_insurance_feedrate(self):
        item = [
            {'start_age': '60D', 'end_age': '6Y',  'fee': 480}
            ]
        comprehensive_insurance_obj = Insurance.get(1)
        comprehensive_insurance_obj.ins_property.feerate = item
        fee = comprehensive_insurance_obj.ins_property.get(1, birthday='2013-03-01')
        self.assertEqual(fee, 480)

    def test_get_critical_insurance_feedrate(self):
        item = [
            {'ill': 1, 'age': '0Y', 'gender': 'M', 'fee': 480},
            {'ill': 1, 'age': '0Y', 'gender': 'F', 'fee': 320},
            {'ill': 0, 'age': '0Y', 'gender': 'M', 'fee': 200},
            {'ill': 0, 'age': '0Y', 'gender': 'F', 'fee': 160},
            ]
        critical_insurance_obj = Insurance.get(8)
        critical_insurance_obj.ins_property.feerate = item
        fee = critical_insurance_obj.ins_property.get(
            1, ill=1, gender='1', birthday='2016-03-01', coverage=10)
        self.assertEqual(fee, 480)

    def test_get_critical_insurance_feedrate_20w(self):
        item = [
            {'ill': 1, 'age': '2Y', 'gender': 'M', 'fee': 480},
            {'ill': 1, 'age': '2Y', 'gender': 'F', 'fee': 320},
            {'ill': 0, 'age': '2Y', 'gender': 'M', 'fee': 200},
            {'ill': 0, 'age': '2Y', 'gender': 'F', 'fee': 160},
            ]
        critical_insurance_obj = Insurance.get(8)
        critical_insurance_obj.ins_property.feerate = item
        fee = critical_insurance_obj.ins_property.get(
            2, ill=0, gender='0', birthday='2014-03-01')
        self.assertEqual(fee, 320)

    def test_get_education_insurance_feedrate_20w(self):
        item = [
            {'age': '2Y', 'coverage': 'low', 'fee': 3393},
            {'age': '2Y', 'coverage': 'medium', 'fee': 9390},
            {'age': '2Y', 'coverage': 'high', 'fee': 21525},
            {'age': '3Y', 'coverage': 'low', 'fee': 6553},
            {'age': '3Y', 'coverage': 'medium', 'fee': 18140},
            {'age': '3Y', 'coverage': 'high', 'fee': '41575'}
            ]
        education_insurance_obj = Insurance.get(10)
        education_insurance_obj.ins_property.feerate = item
        fee = education_insurance_obj.ins_property.get(
            1, birthday='2014-03-01', coverage='a1')
        self.assertEqual(fee, 3393)
