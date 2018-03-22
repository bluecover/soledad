# -*- coding: utf-8 -*-

import copy
from datetime import datetime

from core.models.utils import calculate_age

# pylint: disable=E0601,E0602

# health 0, 1, 2 # 极少 偶尔 经常
# society 0, 1 # 无 有
# other 0, 1 # 无 有报销途径
# family_income 0, 1, 2 # 低于 相当 高于

children_insurance = []

for c in children:
    child = copy.copy(c)

    name = child.get('name')
    birthdate = child.get('birthdate')
    health = int(child.get('health'))
    society = int(child.get('society'))
    family_income = int(child.get('family_income'))

    com_in = False #comprehensive insurance
    ill_in = False #illness insurance
    edu_in = False #education insurance

    doc = """现阶段，%(name)s的自我保护意识薄弱，身体抵抗力较弱，容易意外受伤、生病，尤其一些重大疾病的患病率高于成年人。这就需要您为孩子做好应对普通医疗、重大疾病的准备。<br/>

此外，%(name)s的教育将是您的一项重要投资，应及早规划。尤其需要防范家庭变故、无力负担教育金的情况，保证%(name)s在每个阶段都能享有专用教育金。<br/>"""

    if society == 0:
        pass
        if family_income == 0:
            # case 5
            com_in = True
            doc += """目前，%(name)s未参投社保，需要购买儿童综合险、重疾险补充对普通医疗、重大疾病的保障；也需针对教育风险购买教育险。"""
        else:# family_income = 1,2
            # case 6
            com_in = True
            ill_in = True
            doc += """目前，%(name)s未参投社保，需要购买儿童综合险补充对普通医疗、重大疾病的保障；也需针对教育风险购买教育险。"""
    else:#society == 1
        other = int(child.get('other'))
        if other == 0:
            if health == 2:
                if family_income == 0:
                    # case 3
                    com_in = True
                    doc += """目前，%(name)s虽参投社保，但身体较弱，还应购买儿童综合险补充对普通医疗、重大疾病的保障；也需针对教育风险购买教育险。"""
                else: # family_income = 1, 2
                    # case 4
                    com_in = True
                    ill_in = True
                    doc += """目前，%(name)s虽参投社保，但身体较弱，还应购买儿童综合险、重疾险补充对普通医疗、重大疾病的保障；也需针对教育风险购买教育险。"""
            else:# health = 0, 1
                # case 2
                ill_in = True
                doc += """目前，%(name)s参投社保，普通医疗保障充足；还需针对重大疾病、教育风险购买重疾险、教育险。"""
        else: # other = 1
            # case 1
            ill_in = True
            doc += """目前，%(name)s参投社保、享有补充医疗报销，普通医疗保障充足；还需针对重大疾病、教育风险购买重疾险、教育险。"""
    child['insure'] = {'0':com_in, '1':ill_in, '2':edu_in}
    child['doc'] = doc % {'name':name}

    birth = datetime.strptime(birthdate, '%Y-%m-%d')
    child['age'] = calculate_age(birth.date())
    children_insurance.append(child)
