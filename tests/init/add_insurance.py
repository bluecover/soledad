# -*- coding: utf-8 -*-

'''
初始化保险条目信息
'''

from libs.utils.log import bcolors
from core.models.insurance.insurance import Insurance
from core.models.insurance.packages import Package
from core.models.insurance.program import Program


enter = '\r\n\r\n'


def add_insurance_props():
    item = [
        {'age': '0Y', 'coverage': 'low', 'fee': 3234},
        {'age': '0Y', 'coverage': 'medium', 'fee': 8940},
        {'age': '0Y', 'coverage': 'high', 'fee': 20490},
        {'age': '1Y', 'coverage': 'low', 'fee': 3320},
        {'age': '1Y', 'coverage': 'medium', 'fee': 9170},
        {'age': '1Y', 'coverage': 'high', 'fee': 21015},
        {'age': '2Y', 'coverage': 'low', 'fee': 3393},
        {'age': '2Y', 'coverage': 'medium', 'fee': 9390},
        {'age': '2Y', 'coverage': 'high', 'fee': 21525},
        {'age': '3Y', 'coverage': 'low', 'fee': 6553},
        {'age': '3Y', 'coverage': 'medium', 'fee': 18140},
        {'age': '3Y', 'coverage': 'high', 'fee': 41575},
        {'age': '4Y', 'coverage': 'low', 'fee': 6725},
        {'age': '4Y', 'coverage': 'medium', 'fee': 18600},
        {'age': '4Y', 'coverage': 'high', 'fee': 41575},
        {'age': '5Y', 'coverage': 'low', 'fee': 6889},
        {'age': '5Y', 'coverage': 'medium', 'fee': 19060},
        {'age': '5Y', 'coverage': 'high', 'fee': 43680},
        {'age': '6Y', 'coverage': 'low', 'fee': 7065},
        {'age': '6Y', 'coverage': 'medium', 'fee': 19540},
        {'age': '6Y', 'coverage': 'high', 'fee': 44780},
        {'age': '7Y', 'coverage': 'low', 'fee': 6026},
        {'age': '7Y', 'coverage': 'medium', 'fee': 13970},
        {'age': '7Y', 'coverage': 'high', 'fee': 30755},
        {'age': '8Y', 'coverage': 'low', 'fee': 6183},
        {'age': '8Y', 'coverage': 'medium', 'fee': 14340},
        {'age': '8Y', 'coverage': 'high', 'fee': 31575},
        {'age': '9Y', 'coverage': 'low', 'fee': 6343},
        {'age': '9Y', 'coverage': 'medium', 'fee': 14710},
        {'age': '9Y', 'coverage': 'high', 'fee': 32390},
        {'age': '10Y', 'coverage': 'low', 'fee': 5285},
        {'age': '10Y', 'coverage': 'medium', 'fee': 8990},
        {'age': '10Y', 'coverage': 'high', 'fee': 17980},
        {'age': '11Y', 'coverage': 'low', 'fee': 5420},
        {'age': '11Y', 'coverage': 'medium', 'fee': 9220},
        {'age': '11Y', 'coverage': 'high', 'fee': 18400},
        {'age': '12Y', 'coverage': 'low', 'fee': 5555},
        {'age': '12Y', 'coverage': 'medium', 'fee': 9460},
        {'age': '12Y', 'coverage': 'high', 'fee': 18900},
        {'age': '13Y', 'coverage': 'low', 'fee': 5690},
        {'age': '13Y', 'coverage': 'medium', 'fee': 9680},
        {'age': '13Y', 'coverage': 'high', 'fee': 19360}
    ]
    education_insurance_obj = Insurance.get(10)
    feerate = item
    rec_reason = u'① 保障范围广（意外身故、意'
    buy_url = 'http://www.hzins.com/product/detail-727.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现直到大学的教育金保障'
    education_insurance_obj.add_insurance_props(

        feerate, rec_reason, buy_url, ins_title, ins_sub_title)
    item1 = [
        {'start_age': '60D', 'end_age': '6Y', 'fee': 480},
    ]
    comprehensive_insurance_obj = Insurance.get(1)
    feerate = item1
#    rec_reason = (u'① 保障范围广（意外身故、意外医疗、住院医疗、重大疾病、',
#                  u'医疗运送等',
#                  enter,
#                  u'② 性价比高，尤其含重疾保额10万元')
    rec_reason = u'① 含保费豁免条款'
    buy_url = 'http://www.hzins.com/product/detail-857.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现综合、全面的保障'
    comprehensive_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item2 = [
        {'start_age': '7Y', 'end_age': '17Y', 'fee': 400}
    ]
    comprehensive_insurance_obj = Insurance.get(2)
    feerate = item2
#    rec_reason = (u'① 保障范围广（意外身故、意外医疗、住院医疗、重大疾病、',
#                  u'医疗运送等）',
#                  enter,
#                  u'② 性价比高，尤其含重疾保额10万元')
    rec_reason = u'① 保障范围广（意外身故、意外医疗、住院医疗、重大疾病、医'
    buy_url = 'http://www.hzins.com/product/detail-858.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现综合、全面的保障'
    comprehensive_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item3 = [
        {'start_age': '3Y', 'end_age': '17Y', 'fee': 190}
    ]
    comprehensive_insurance_obj = Insurance.get(3)
    feerate = item3
    rec_reason = u'① 保障侧重医疗和重疾，含住院医疗8万，重疾2万'
    buy_url = 'http://www.hzins.com/product/detail-932.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现医疗为重的综合保障'
    comprehensive_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item4 = [
        {'start_age': '30D', 'end_age': '17Y', 'fee': 260}
    ]
    comprehensive_insurance_obj = Insurance.get(4)
    feerate = item4
    rec_reason = u'① 保费低、保障全'
    ins_title = 'ins_title'
    ins_sub_title = u'实现医疗为重的综合保障'
    buy_url = 'http://www.hzins.com/product/detail-933.html'
    ins_sub_title = u'实现综合、全面的保障'
    comprehensive_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item5 = [
        {'start_age': '30D', 'end_age': '2Y', 'fee': 480}
    ]
    comprehensive_insurance_obj = Insurance.get(5)
    feerate = item5
    rec_reason = u'① 保障较全面，'
    buy_url = 'http://www.hzins.com/product/detail-1107.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现医疗为重的综合保障'
    comprehensive_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item6 = [
        {'start_age': '2Y', 'end_age': '6Y', 'fee': 300}
    ]
    comprehensive_insurance_obj = Insurance.get(6)
    feerate = item6
    rec_reason = u'① 住院医疗（10万）'
    buy_url = 'http://www.hzins.com/product/detail-924.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现医疗为重的综合保障'
    comprehensive_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item7 = [
        {'start_age': '7Y', 'end_age': '17Y', 'fee': 300}
    ]
    comprehensive_insurance_obj = Insurance.get(7)
    feerate = item7
    rec_reason = u'① 性价比高，含住院医疗10万、重疾8万等'
    buy_url = 'http://www.hzins.com/product/detail-926.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现医疗为重的综合保障'
    comprehensive_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item8 = [
        {'ill': 0, 'gender': 'M', 'age': '0Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '0Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '1Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '1Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '2Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '2Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '3Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '3Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '4Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '4Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '5Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '5Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '6Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '6Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '7Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '7Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '8Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '8Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '9Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '9Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '10Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '10Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '11Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '11Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '12Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '12Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '13Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '13Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '14Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '14Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '15Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '15Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '16Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '16Y', 'fee': 200},
        {'ill': 0, 'gender': 'F', 'age': '17Y', 'fee': 200},
        {'ill': 0, 'gender': 'M', 'age': '17Y', 'fee': 200}
    ]

    critical_insurance_obj = Insurance.get(8)
    feerate = item8
    rec_reason = u'① 针对18种少儿高发重大疾病，剔除成人易患的重疾'
    buy_url = 'http://www.hzins.com/product/detail-725.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现最高%s万元的重疾保障'
    critical_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    item9 = [
        {'ill': 1, 'gender': 'M', 'age': '0Y', 'fee': 160},
        {'ill': 1, 'gender': 'F', 'age': '0Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '1Y', 'fee': 150},
        {'ill': 1, 'gender': 'F', 'age': '1Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '2Y', 'fee': 150},
        {'ill': 1, 'gender': 'F', 'age': '2Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '3Y', 'fee': 150},
        {'ill': 1, 'gender': 'F', 'age': '3Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '4Y', 'fee': 160},
        {'ill': 1, 'gender': 'F', 'age': '4Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '5Y', 'fee': 160},
        {'ill': 1, 'gender': 'F', 'age': '5Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '6Y', 'fee': 170},
        {'ill': 1, 'gender': 'F', 'age': '6Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '7Y', 'fee': 170},
        {'ill': 1, 'gender': 'F', 'age': '7Y', 'fee': 130},
        {'ill': 1, 'gender': 'M', 'age': '8Y', 'fee': 180},
        {'ill': 1, 'gender': 'F', 'age': '8Y', 'fee': 140},
        {'ill': 1, 'gender': 'M', 'age': '9Y', 'fee': 180},
        {'ill': 1, 'gender': 'F', 'age': '9Y', 'fee': 140},
        {'ill': 1, 'gender': 'M', 'age': '10Y', 'fee': 190},
        {'ill': 1, 'gender': 'F', 'age': '10Y', 'fee': 140},
        {'ill': 1, 'gender': 'M', 'age': '11Y', 'fee': 200},
        {'ill': 1, 'gender': 'F', 'age': '11Y', 'fee': 150},
        {'ill': 1, 'gender': 'M', 'age': '12Y', 'fee': 200},
        {'ill': 1, 'gender': 'F', 'age': '12Y', 'fee': 160},
        {'ill': 1, 'gender': 'F', 'age': '13Y', 'fee': 210},
        {'ill': 1, 'gender': 'M', 'age': '13Y', 'fee': 160},
        {'ill': 1, 'gender': 'F', 'age': '14Y', 'fee': 220},
        {'ill': 1, 'gender': 'M', 'age': '14Y', 'fee': 170},
        {'ill': 1, 'gender': 'M', 'age': '15Y', 'fee': 230},
        {'ill': 1, 'gender': 'F', 'age': '15Y', 'fee': 180},
        {'ill': 1, 'gender': 'F', 'age': '16Y', 'fee': 250},
        {'ill': 1, 'gender': 'M', 'age': '16Y', 'fee': 190},
        {'ill': 1, 'gender': 'F', 'age': '17Y', 'fee': 260},
        {'ill': 1, 'gender': 'M', 'age': '17Y', 'fee': 200}
    ]

    critical_insurance_obj = Insurance.get(9)
    feerate = item9
    rec_reason = u'① 长期消费型保险，适合有家族遗传病史，'
    buy_url = 'http://www.hzins.com/product/health/detal-146.html'
    ins_title = 'ins_title'
    ins_sub_title = u'实现%s万元的长期重疾保障'
    critical_insurance_obj.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    package_obj_1 = Package.get(1)
    package_obj_1[0].insurance_ability = u'本套餐合理覆盖医疗、重疾、'
    package_obj_1[0].name = u'基础套餐'
    package_obj_1[0].title = u'均衡、全面的保障规划'
    package_obj_1[0].sub_title = u'以超高性价比实现均衡的基础保障'
    package_obj_1[0].quota = u''
    package_obj_1[0].quota_b = u''
    package_obj_1[0].radar = 'radar1.png'

    package_obj_2 = Package.get(2)
    package_obj_2[0].insurance_ability = u'本套餐着重于医疗保障，'
    package_obj_2[0].name = u'医疗套餐'
    package_obj_2[0].title = u'医疗保障为主的规划'
    package_obj_2[0].sub_title = u'充足的医疗保障与合理的整体配置'
    package_obj_2[0].quota = u''
    package_obj_2[0].quota_b = u''
    package_obj_2[0].radar = 'radar2.png'

    package_obj_3 = Package.get(3)
    package_obj_3[0].insurance_ability = u'本套餐着重于重疾保障，兼顾适当的'
    package_obj_3[0].name = u'重疾套餐'
    package_obj_3[0].title = u'医疗保障为主的规划'
    package_obj_3[0].sub_title = u'充足的重疾保障与合理的整体配置'
    package_obj_3[0].quota = u''
    package_obj_3[0].quota_b = u''
    package_obj_3[0].radar = 'radar3.png'

    package_obj_4 = Package.get(4)
    package_obj_4[0].insurance_ability = u'本套餐着重于意外保障，精心组合'
    package_obj_4[0].name = u'意外套餐'
    package_obj_4[0].title = u'重疾保障为主的规划'
    package_obj_4[0].sub_title = u'充足的意外保障与高性价比的整体配置'
    package_obj_4[0].quota = u''
    package_obj_4[0].quota_b = u''
    package_obj_4[0].radar = 'radar4.png'

    package_obj_5 = Package.get(5)
    package_obj_5[0].insurance_ability = u'本套餐均衡应对各种风险，科学组合'
    package_obj_5[0].name = u'升级套餐'
    package_obj_5[0].title = u'意外保障为主的规划'
    package_obj_5[0].sub_title = u'以高性价比实现全面、完善的保障'
    package_obj_5[0].quota = u''
    package_obj_5[0].quota_b = u''
    package_obj_5[0].radar = 'radar5.png'

    program = Program()
    balance_quota = u'理财师根据儿童现状，挑选最高性价比儿童保险，'

    medical_with_socical_insurance = u'由于您的孩子已有医保与补充医疗保险，'
    medical_quota = 'medical_quota'

    disease_quota = u'有家族遗传病史的儿童需要尽早完善重疾保障，适合长期重疾险'
    accident_quota = u'孩子们还没学会保护自己，同时充满好奇心、活泼好动，'

    program.quota = {'1': balance_quota,
                     '2': medical_with_socical_insurance,
                     '3': medical_quota,
                     '4': disease_quota,
                     '5': accident_quota}


def add_insurance(kind, insurance_id, name, status, rec_rank):
    Insurance.add(kind, insurance_id, name, status, rec_rank)
    bcolors.run(
        u'insurance_id=%s,kind=%s,name=%s' %
        (insurance_id, kind, name), key='insurance')


def add_package():
    pkg_map = {'1': u'基础套餐', '2': u'医疗套餐', '3': u'重疾套餐',
               '4': u'意外套餐', '5': u'升级套餐第一推荐',
               '6': u'升级套餐第二推荐'}
    ins_map = {'1': u'乐享人生-安联个人保障计划（幼儿版） 计划二',
               '2': u'乐享人生-安联个人保障计划（少儿版） 计划二',
               '3': u'慧择少儿学生安康保障计划（国寿版） 计划A',
               '4': u'慧择少儿学生安康保障计划（国寿版） 计划B',
               '5': u'平安宝贝少儿综合医疗保险 A款',
               '6': u'阳光乐童卡综合保障计划 儿童版',
               '7': u'阳光乐童卡综合保障计划 青少年版',
               '8': u'泰康e顺少儿重大疾病保险',
               '9': u'合众定期重大疾病保险',
               '10': u'阳光旅程教育金保障计划（分红型）'}
    pkg_id = '1'
    ins_id = '1'
    status = '1'
    rank_in_pkg = '2'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)
    pkg_id = '1'
    ins_id = '2'
    status = '1'
    rank_in_pkg = '1'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '1'
    ins_id = '4'
    status = '1'
    rank_in_pkg = '3'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '1'
    ins_id = '8'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '1'
    ins_id = '9'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '1'
    ins_id = '10'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '2'
    ins_id = '3'
    status = '1'
    rank_in_pkg = '1'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '2'
    ins_id = '5'
    status = '1'
    rank_in_pkg = '2'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '2'
    ins_id = '8'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '2'
    ins_id = '9'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '2'
    ins_id = '10'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '3'
    ins_id = '4'
    status = '1'
    rank_in_pkg = '3'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '3'
    ins_id = '6'
    status = '1'
    rank_in_pkg = '2'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '3'
    ins_id = '7'
    status = '1'
    rank_in_pkg = '1'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '3'
    ins_id = '8'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '3'
    ins_id = '9'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '3'
    ins_id = '10'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '4'
    ins_id = '4'
    status = '1'
    rank_in_pkg = '1'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '4'
    ins_id = '8'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)
    pkg_id = '4'
    ins_id = '9'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '4'
    ins_id = '10'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '5'
    ins_id = '5'
    status = '1'
    rank_in_pkg = '3'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '5'
    ins_id = '6'
    status = '1'
    rank_in_pkg = '2'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '5'
    ins_id = '7'
    status = '1'
    rank_in_pkg = '1'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '5'
    ins_id = '8'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '5'
    ins_id = '9'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '5'
    ins_id = '10'
    status = '1'
    rank_in_pkg = '0'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '6'
    ins_id = '1'
    status = '1'
    rank_in_pkg = '2'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

    pkg_id = '6'
    ins_id = '2'
    status = '1'
    rank_in_pkg = '1'
    rec_rank = '1'
    Package.add(pkg_id, pkg_map[pkg_id], ins_id, ins_map[ins_id],
                status, rank_in_pkg, rec_rank)

if __name__ == '__main__':
    bcolors.run('add_insurance insurance.')
    add_insurance(0, 1, u'ins1', 1, 1)
    add_insurance(0, 2, u'ins2', 1, 1)
    add_insurance(0, 3, u'ins3', 1, 1)
    add_insurance(0, 4, u'ins4', 1, 1)
    add_insurance(0, 5, u'ins5', 1, 1)
    add_insurance(0, 6, u'ins6', 1, 1)
    add_insurance(0, 7, u'ins7', 1, 1)
    add_insurance(1, 8, u'ins8', 1, 1)
    add_insurance(1, 9, u'ins9', 1, 1)
    add_insurance(2, 10, u'ins10', 1, 1)

    add_package()
    add_insurance_props()
