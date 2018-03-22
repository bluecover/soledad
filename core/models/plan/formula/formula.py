# -*- coding: utf-8 -*-

import copy
import bisect

from libs.linker import make_url

from core.models.utils import hundred_rounding, ten_thou_rounding, ten_rounding, dec_2_pct

from core.models.plan.formula.data import (average_income, net_assets_data_ratio,
                                           net_assets_data_individual, net_assets_data_family,
                                           expend_month_data_ratio, expend_month_data_individual,
                                           expend_month_data_family, assets_allocation_data,
                                           average_earning_data)
from core.models.plan.formula.target import multi_targets


# pylint: disable=E0601,E0602

#pre data
paid_job = ['1','2','3','4'] #有收入的职业: 公务员, 国企、事业单位职工, 私企、外企职工, 私营业主、自由职业者
age = int(age)
spouse_age = int(spouse_age) if spouse else 0

#家庭
children = filter(lambda child: int(child.get('age'))<18, children) #只取18以下的子女作为算法依据
children_number = len(children) # 子女个数
relation_number = children_number+(1 if spouse else 0)
family_member_number = 1+ relation_number #家庭成员个数
is_family_doc = '家庭' if relation_number else ''


##############资产现状##############
non_invest = [deposit_current, deposit_fixed] # 非投资品资产
invest = [funds_money, funds_hybrid, funds_bond, funds_stock, funds_other, invest_bank, invest_stock, invest_national_debt, invest_p2p, invest_insure, invest_metal, invest_other] #投资品资产 TODO D

raw_physical_assets = [('房产', real_estate_value*10000),
                       ('汽车', car_value*10000),
                       ('收藏品', real_collection_value*10000),
                       ('其他', real_other_value*10000)]

raw_deposit_assets = [('现金及活期存款', deposit_current),
                      ('定期存款', deposit_fixed)]

raw_funds_assets = [('货币基金/余额宝', funds_money),
                    ('债券型基金', funds_bond),
                    ('混合型基金', funds_hybrid),
                    ('指数型基金', funds_index),
                    ('股票型基金', funds_stock),
                    ('其他基金', funds_other)]

raw_other_assets = [('银行理财产品', invest_bank),
                    ('国债', invest_national_debt),
                    ('储蓄型保险', invest_insure),
                    ('P2P网贷', invest_p2p),
                    ('股票', invest_stock),
                    ('贵金属', invest_metal),
                    ('其他', invest_other)]


physical_assets_l = copy.copy(raw_physical_assets)
deposit_assets_l = copy.copy(raw_deposit_assets)
funds_assets_l = copy.copy(raw_funds_assets)
other_assets_l = copy.copy(raw_other_assets)
for (k, v) in raw_physical_assets:
    if v == 0:
        physical_assets_l.remove((k,v))
for (k, v) in raw_deposit_assets:
    if v == 0:
        deposit_assets_l.remove((k,v))
for (k, v) in raw_funds_assets:
    if v == 0:
        funds_assets_l.remove((k,v))
for (k, v) in raw_other_assets:
    if v == 0:
        other_assets_l.remove((k,v))

fin_assets_l = deposit_assets_l + funds_assets_l + other_assets_l

funds_assets = sum([funds_money, funds_bond, funds_hybrid, funds_index, funds_stock, funds_other])
deposit_assets = sum(non_invest)

physical_assets = sum([v for (k,v) in physical_assets_l]) #实物资产
fin_assets = sum([v for (k,v) in fin_assets_l]) #金融资产
total_assets = physical_assets+fin_assets #资产总值
total_debt = consumer_loans+real_estate_loan*10000 #总负债
net_assets = total_assets-total_debt #净资产
debt_ratio = round(float(total_debt)/total_assets, 4) if total_assets!=0 else 0.0 #资产负债率

net_assets_data = net_assets_data_family if relation_number else net_assets_data_individual
net_assets_ratio = 0.0
if net_assets<net_assets_data[0]:
    net_assets_ratio = net_assets_data_ratio[0]
else:
    net_assets_ratio = net_assets_data_ratio[bisect.bisect(net_assets_data, net_assets)-1]#净资产评价

assets_eval_con = ''
net_assets_ratio_con = '高于'
assets_eval_doc = ''
if net_assets_ratio>=0.75:
    assets_eval_con = '高于'
    assets_eval_doc = '您已经有了很好的财富积累。从较高的起点出发，如果善加投资，财富成长速度会越来越快。'
elif 0.5 <= net_assets_ratio < 0.75:
    assets_eval_con = '略高于'
    assets_eval_doc = '您已经有了不错的财富积累。但这只是一个起点，如果善加投资，财富成长速度会越来越快。'
elif 0.3 <= net_assets_ratio < 0.5:
    assets_eval_con = '略低于'
    assets_eval_doc = '您已经有了一定的财富积累。但是接下来仍需做好收支规划，并善加投资，获得更快的财富成长速度。'
elif net_assets_ratio < 0.3:
    assets_eval_con = '低于'
    net_assets_ratio_con = '低于'
    net_assets_ratio = 1-net_assets_ratio
    assets_eval_doc = '从您的财富积累情况来看，理财起点较低。但是如果接下来做好收支规划，并善加投资，财务状况会得到有效改善。'

debt_con = ''
debt_doc = ''
gh_suggest_assets_act = []

if real_estate_loan:
    if debt_ratio<0.3:
        debt_con = '较低'
        debt_doc = '您的资产负债率较低，债务负担较轻，并且负债主要来自于房贷这种利率较低的长期贷款。只要您保持健康的收支状况、按时还贷，即可有效控制财务风险。'
    elif 0.3<=debt_ratio<0.6:
        debt_con = '适中'
        debt_doc = '您的资产负债率适中，债务负担可以承受，并且负债主要来自于房贷这种利率较低的长期贷款。只要您保持健康的收支状况、按时还贷，可以有效控制财务风险。'
    elif debt_ratio>=0.6:
        debt_con = '较高'
        debt_doc = '您的资产负债率较高。虽然您的负债主要来自于房贷这种利率较低的长期贷款，但是较重的债务负担还是可能使您在财务方面捉襟见肘。您需要通过良好的收支规划和稳健投资来增加金融资产，<span class="text-blue">将资产负债率降低到60%以下</span>，从而有效控制财务风险。'
        gh_suggest_assets_act.append('将您的资产负债率降低至<span class="text-orange">60%</span>')
else:
    if debt_ratio==0 or debt_ratio==0.0:
        debt_con = '较低'
        debt_doc = '您的资产负债率为0，没有债务负担。请您继续保持健康的收支状况、稳健投资，不断提升抵御财务风险的能力。'
    elif 0<debt_ratio<0.25:
        debt_con = '较低'
        debt_doc = '您的资产负债率较低，债务负担较轻。只要您保持健康的收支状况、稳健投资，即可有效控制财务风险。'
    elif 0.25<=debt_ratio<0.5:
        debt_con = '适中'
        debt_doc = '您的资产负债率适中，债务负担可以承受。但您需要保持健康的收支状况、稳健投资，并根据债务的利率和期限情况制定优先级、及时偿还负债，从而有效控制财务风险。'
    else:
        debt_con = '较高'
        debt_doc = '您的资产负债率较高，债务负担较重，及时偿还负债应作为重要理财目标、以高优先级来完成。您需要持续优化收支、提高结余，并稳健投资增加金融资产，<span class="text-blue">将资产负债率降低到50%以下</span>，从而有效控制财务风险。'
        gh_suggest_assets_act.append('将您的资产负债率降低至<span class="text-orange">50%</span>')

gh_suggest_assets_doc = '您的财富'+assets_eval_con+'大多数'+('家庭' if relation_number else '人')+'，结合资产负债率来看，财务风险'+debt_con+'。'

##############收支分析##############
mine_income_month = income_month_salary+income_month_extra #我的月收入
spouse_income_month = (spouse_income_month_salary+spouse_income_month_extra) if spouse else 0 #配偶月收入
income_month = mine_income_month+spouse_income_month #月收入

expend_month = expend_month_ent+expend_month_trans+expend_month_shopping+expend_month_house+expend_month_extra #月支出
balance_month = income_month-expend_month #月结余
balance_month_ratio = round(float(balance_month)/income_month, 2) if income_month else 0.0 #月结余率

mine_income_year = mine_income_month*12+income_year_bonus+income_year_extra #我的年收入
spouse_income_year = (spouse_income_month*12+spouse_income_year_bonus+spouse_income_year_extra) if spouse else 0 #配偶年收入
income_year = mine_income_year+spouse_income_year #年收入

expend_year = expend_month*12+expend_year_extra #年支出
balance_year = income_year-expend_year #年结余
balance_year_ratio = round(float(balance_year)/income_year, 2) if income_year else 0.0 #结余率

income_resource_count = (1 if career in paid_job else 0)+(1 if spouse and spouse_career in paid_job else 0) #收入来源个数
income_loc = '%s0000'%city[:2] if city[:2] in ('11','12','31','50') else city
income_loc_cn, income_loc_person, income_loc_family = average_income.get(income_loc, ('其他城市','1240','2480'))

local_income = int(income_loc_family if family_member_number>1 else income_loc_person)

target_balance_month_ratio = 0.0 #目标月结余率
#见目标结余率表格
if relation_number:
    if income_month>12000:
        if expend_month_house:
            target_balance_month_ratio = 0.3
        else:
            target_balance_month_ratio = 0.35
    else:
        if expend_month_house:
            target_balance_month_ratio = 0.25
        else:
            target_balance_month_ratio = 0.3
else:
    if income_month>8000:
        if expend_month_house:
            target_balance_month_ratio = 0.3
        else:
            target_balance_month_ratio = 0.35
    else:
        if expend_month_house:
            target_balance_month_ratio = 0.25
        else:
            target_balance_month_ratio = 0.3
if 0.245<=balance_month_ratio<0.295:
    target_balance_month_ratio = 0.3 if target_balance_month_ratio<balance_month_ratio else target_balance_month_ratio
if 0.295<=balance_month_ratio<0.355:
    target_balance_month_ratio = 0.35

target_balance_month_ratio = balance_month_ratio if balance_month_ratio>0.35 else target_balance_month_ratio
target_balance_month_name = '提高到' if balance_month_ratio<0.35 else '维持在'
target_balance_month = balance_month if balance_month_ratio>0.35 else int(income_month*target_balance_month_ratio)


expend_month_data = expend_month_data_family if relation_number else expend_month_data_individual
expend_month_ratio = 0.0
if expend_month<expend_month_data[0]:
    expend_month_ratio = expend_month_data_ratio[0]
else:
    expend_month_ratio = expend_month_data_ratio[bisect.bisect(expend_month_data, expend_month)-1]#月支出评价

expend_month_house_ratio = round(float(expend_month_house)/income_month, 4) if income_month else 0.0

# 收支评价
balance_month_title = '建议提高到' if balance_month_ratio<=0.35 else '建议维持在'
balance_month_ratio_con = ''
balance_month_ratio_doc = ''
if balance_month_ratio<0.15 and expend_month_house:
    balance_month_ratio_con = '过低'
    balance_month_ratio_doc = '您当前的月结余率过低，提升空间很大。逐步提高月结余应该是您理财的首要目标。考虑到房租房贷压力，<span class="text-blue">建议您先争取将月结余率由'+dec_2_pct(balance_month_ratio)+'提高到'+dec_2_pct(target_balance_month_ratio)+'，即平均每月结余'+format(target_balance_month, ',')+'元</span>，这样才能逐步实现财富积累。'
elif balance_month_ratio<0.15 and not expend_month_house:
    balance_month_ratio_con = '过低'
    balance_month_ratio_doc = '您当前的月结余率过低。而且您并没有房租房贷支出，提升空间很大。逐步提高月结余应该是您理财的首要目标。<span class="text-blue">建议您先争取将月结余率由'+dec_2_pct(balance_month_ratio)+'提高到'+dec_2_pct(target_balance_month_ratio)+'，即平均每月结余'+format(target_balance_month, ',')+'元</span>，这样才能逐步实现财富积累。'
elif balance_month_ratio>=0.15 and balance_month_ratio<0.25 and expend_month_house:
    balance_month_ratio_con = '偏低'
    balance_month_ratio_doc = '您当前的月结余率偏低，有待进一步提高。考虑到房租房贷压力，<span class="text-blue">建议您争取将月结余率由'+dec_2_pct(balance_month_ratio)+'提高到'+dec_2_pct(target_balance_month_ratio)+'，即平均每月结余'+format(target_balance_month, ',')+'元</span>，这将帮助您更快进行财富积累。'
elif balance_month_ratio>=0.15 and balance_month_ratio<0.25 and not expend_month_house:
    balance_month_ratio_con = '偏低'
    balance_month_ratio_doc = '您当前的月结余率偏低。您并没有房租房贷支出，结余率有待进一步提高。根据您的个人情况，<span class="text-blue">建议您争取将月结余率由'+dec_2_pct(balance_month_ratio)+'提高到'+dec_2_pct(target_balance_month_ratio)+'，即平均每月结余'+format(target_balance_month, ',')+'元</span>，这将帮助您更快进行财富积累。'
elif balance_month_ratio>=0.25 and balance_month_ratio<0.35 and expend_month_house:
    balance_month_ratio_con = '稍低'
    balance_month_ratio_doc = '您当前的月结余率稍低于理想水平。考虑到房租房贷压力，<span class="text-blue">建议您将月结余率由'+dec_2_pct(balance_month_ratio)+'提高到'+dec_2_pct(target_balance_month_ratio)+'，即平均每月结余'+format(target_balance_month, ',')+'元</span>。这将帮助您更快进行财富积累。'
elif balance_month_ratio>=0.25 and balance_month_ratio<0.35 and not expend_month_house:
    balance_month_ratio_con = '稍低'
    balance_month_ratio_doc = '您当前的月结余率稍低于理想水平。考虑到您并无房租房贷支出，<span class="text-blue">建议将月结余率由'+dec_2_pct(balance_month_ratio)+'提高到'+dec_2_pct(target_balance_month_ratio)+'，即平均每月结余'+format(target_balance_month, ',')+'元</span>。这将帮助您更快进行财富积累。'
elif balance_month_ratio>0.35:
    balance_month_ratio_con = '健康'
    balance_month_ratio_doc = '您当前的月结余状况较为健康，请保持。不过，如果继续挖掘开源节流的潜力，会帮助您更快进行财富积累。'

gh_suggest_balance_doc = '您'+is_family_doc+'的月结余率'+balance_month_ratio_con+'，请将月结余率'+target_balance_month_name+dec_2_pct(target_balance_month_ratio)+'（'+format(target_balance_month, ',')+'元）。'
gh_suggest_balance_act = ['养成记帐习惯，明确了解收支状况，以便分析和改进（推荐使用 <a href="'+make_url('http://timi.talicai.com/')+'" target="_blank">TIMI时光记帐</a>）',
                          '在月初制定预算，在月末分析实际支出并对照改进',
                          '将月结余率'+target_balance_month_name+dec_2_pct(target_balance_month_ratio)+'（'+ format(target_balance_month, ',')+'元 )']

##############备用金##############
target_deposit_current_ceiling = 1000 #目标活期存款上限
target_deposit_current_floor = 500 #目标活期存款下限
target_funds_money_ceiling = 2000 #目标货币基金上限
target_funds_money_floor = 1000 #目标货币基金下限

target_reserve_fund = 0 #目标备用金金额

if expend_month>15000:
    target_deposit_current_ceiling = 30000
    target_deposit_current_floor = 15000
    target_funds_money_ceiling = 60000
    target_funds_money_floor = 30000
elif expend_month>500 and expend_month<=15000:
    target_deposit_current_ceiling = hundred_rounding(expend_month*2)
    target_deposit_current_floor = hundred_rounding(expend_month)
    target_funds_money_ceiling = hundred_rounding(expend_month*4)
    target_funds_money_floor = hundred_rounding(expend_month*2)

deposit_current_r = hundred_rounding(deposit_current)
funds_money_r = hundred_rounding(funds_money)
dep_evl, dep_act, fun_evl, fun_act = '', '', '', ''

gh_suggest_reserve_act = ['', '']

#资产抵扣 用于 投资规划
dep_des = deposit_current_r #投资抵扣活期存款
fun_des = funds_money_r #投资抵扣货币基金

if target_deposit_current_floor <= deposit_current_r <= target_deposit_current_ceiling:
    #活期合理
    dep_evl, dep_act = '合理', '保持现状'
    gh_suggest_reserve_act[0] = '保持现金及活期存款'+format(deposit_current_r,',')+'元不变'
    if target_funds_money_floor <= funds_money_r <= target_funds_money_ceiling:
        fun_evl, fun_act = '合理', '保持现状'
        gh_suggest_reserve_act[1] = '保持货币基金'+format(funds_money_r,',')+'元不变'
        target_reserve_fund = deposit_current_r+funds_money_r
        dep_des = deposit_current_r
        fun_des = funds_money_r
    elif funds_money_r < target_funds_money_floor:
        fun_evl, fun_act = '不足', '使用未来月结余，增持货币基金%s元'%format(target_funds_money_floor-funds_money_r,',')
        gh_suggest_reserve_act[1] = '增持货币基金'+format(target_funds_money_floor-funds_money_r,',')+'元'
        target_reserve_fund = deposit_current_r+target_funds_money_floor
        dep_des = deposit_current_r
        fun_des = funds_money_r
    elif funds_money_r > target_funds_money_ceiling:
        fun_evl, fun_act = '过高', '超额%s元，处理建议将在后续的投资规划中给出'%format(funds_money_r-target_funds_money_ceiling,',')
        gh_suggest_reserve_act[1] = '减持货币基金'+format(funds_money_r-target_funds_money_ceiling,',')+'元'
        target_reserve_fund = deposit_current_r+target_funds_money_ceiling
        dep_des = deposit_current_r
        fun_des = target_funds_money_ceiling

elif deposit_current_r < target_deposit_current_floor:
    #活期不足
    dep_evl, dep_act = '不足', '使用未来月结余，补充活期存款%s元'%format(target_deposit_current_floor-deposit_current_r,',')
    gh_suggest_reserve_act[0] = '增持现金及活期存款'+format(target_deposit_current_floor-deposit_current_r,',')+'元'
    if target_funds_money_floor <= funds_money_r <= target_funds_money_ceiling:
        fun_evl, fun_act = '合理', '保持现状'
        gh_suggest_reserve_act[1] = '保持货币基金'+format(funds_money_r,',')+'元不变'
        target_reserve_fund = target_deposit_current_floor+funds_money_r
        dep_des = deposit_current_r
        fun_des = funds_money_r
    elif funds_money_r < target_funds_money_floor:
        fun_evl, fun_act = '不足', '使用未来月结余，增持货币基金%s元'%format(target_funds_money_floor-funds_money_r,',')
        gh_suggest_reserve_act[1] = '增持货币基金'+format(target_funds_money_floor-funds_money_r,',')+'元'
        target_reserve_fund = target_deposit_current_floor+target_funds_money_floor
        dep_des = deposit_current_r
        fun_des = funds_money_r
    elif funds_money_r > target_funds_money_ceiling:
        fun_evl, fun_act = '过高', '超额%s元，处理建议将在后续的投资规划中给出'%format(funds_money_r-target_funds_money_ceiling,',')
        gh_suggest_reserve_act[1] = '减持货币基金'+format(funds_money_r-target_funds_money_ceiling,',')+'元'
        target_reserve_fund = target_deposit_current_floor+target_funds_money_ceiling
        dep_des = deposit_current_r
        fun_des = target_funds_money_ceiling

elif deposit_current_r > target_deposit_current_ceiling:
    #活期过高
    dep_evl = '过高'
    if target_funds_money_floor <= funds_money_r <= target_funds_money_ceiling:
        fun_evl, fun_act = '合理', '保持现状'
        dep_act = '将活期存款中%s元用于投资计划'%format(deposit_current_r-target_deposit_current_ceiling,',')
        gh_suggest_reserve_act[0] = '减持现金及活期存款'+format(deposit_current_r-target_deposit_current_ceiling,',')+'元'
        gh_suggest_reserve_act[1] = '保持货币基金'+format(funds_money_r,',')+'元不变'
        target_reserve_fund = target_deposit_current_ceiling+funds_money_r
        dep_des = target_deposit_current_ceiling
        fun_des = funds_money_r
    elif funds_money_r < target_funds_money_floor:
        fun_evl, fun_act = '不足', '使用未来月结余，增持货币基金%s元'%format(target_funds_money_floor-funds_money_r,',')
        dep_act_floor_more = deposit_current_r-target_deposit_current_floor
        dep_act_ceiling_more = deposit_current_r-target_deposit_current_ceiling
        fun_act_less = target_funds_money_floor-funds_money_r
        #判断活期的结余是否可以填满货币基金的不足
        if dep_act_floor_more<fun_act_less:
            dep_act = '将活期存款中%s元用于增持货币基金'%format(dep_act_floor_more,',')
            gh_suggest_reserve_act[0] = '减持现金及活期存款'+format(dep_act_floor_more,',')+'元'
            fun_act = '使用现有活期存款和未来结余，增持货币基金%s元'%format(fun_act_less,',')
            target_reserve_fund = target_deposit_current_floor+target_funds_money_floor
            dep_des = target_deposit_current_floor
            fun_des = target_funds_money_floor
        elif dep_act_ceiling_more>fun_act_less:
            # case9
            dep_act = '将活期存款中%s元转作其他安排'%format(dep_act_ceiling_more,',')
            gh_suggest_reserve_act[0] = '减持现金及活期存款'+format(dep_act_ceiling_more,',')+'元'
            fun_act = '使用现有活期存款，增持货币基金%s元'%format(fun_act_less,',')
            target_reserve_fund = target_deposit_current_ceiling+target_funds_money_floor
            dep_des = target_deposit_current_ceiling+target_funds_money_floor-funds_money_r
            fun_des = funds_money_r
        else:
            dep_act = '将活期存款中%s元用于增持货币基金'%format(fun_act_less,',')
            gh_suggest_reserve_act[0] = '减持现金及活期存款'+format(fun_act_less,',')+'元'
            fun_act = '使用现有活期存款，增持货币基金%s元'%format(fun_act_less,',')
            target_reserve_fund = deposit_current_r+funds_money_r
            dep_des = deposit_current_r
            fun_des = funds_money_r
        gh_suggest_reserve_act[1] = '增持货币基金'+format(fun_act_less,',')+'元'
    elif funds_money_r > target_funds_money_ceiling:
        fun_evl, fun_act = '过高', '超额%s元，处理建议将在后续的投资规划中给出'%format(funds_money_r-target_funds_money_ceiling,',')
        gh_suggest_reserve_act[1] = '减持货币基金'+format(funds_money_r-target_funds_money_ceiling,',')+'元'
        dep_act = '将活期存款中%s元用于投资计划'%format(deposit_current_r-target_deposit_current_ceiling,',')
        gh_suggest_reserve_act[0] = '减持现金及活期存款'+format(deposit_current_r-target_deposit_current_ceiling,',')+'元'
        target_reserve_fund = target_deposit_current_ceiling+target_funds_money_ceiling
        dep_des = target_deposit_current_ceiling
        fun_des = target_funds_money_ceiling

gh_suggest_reserve_doc = '请以活期存款和货币基金形式，储备'+format(target_reserve_fund,',')+'元紧急备用金，以防不时之需。'

##############风险承受##############
#风险承受 rt = risk tolerrance
#能力
age_rt = 30 if age<=25 else (0 if age>55 else 55-age)

career_cors = {'1':15,'2':15,'3':12,'4':8,'5':5,'6':0,'7':5}
career_rt = career_cors[career] #
#family_rt = 10 if not spouse and not children else ,

family_rt = 0
if spouse:
    if children:
        if income_resource_count>=2:
            family_rt = 5 #已婚，双薪, 有子女
        elif income_resource_count == 1:
            family_rt = 3 #已婚，单薪, 有子女
        else:
            family_rt = 0 #已婚，无薪, 有子女
    else:
        family_rt = 8 #已婚，无子女
elif children:
    family_rt = 0 #未婚 有子女
else:
    family_rt = 10 #未婚 无子女

income_rt = 0
if income_year>=300000:
    income_rt = 20
elif income_year<300000 and income_year>=150000:
    income_rt = 18
elif income_year<150000 and income_year>=120000:
    income_rt = 15
elif income_year<120000 and income_year>=90000:
    income_rt = 10
elif income_year<90000 and income_year>=60000:
    income_rt = 8
elif income_year<60000 and income_year>=35000:
    income_rt = 4

balance_rt = 0
if balance_year_ratio>=0.5:
    balance_rt = 15
elif balance_year_ratio<0.5 and balance_year_ratio>=0.35:
    balance_rt = 13
elif balance_year_ratio<0.35 and balance_year_ratio>=0.25:
    balance_rt = 11
elif balance_year_ratio<0.25 and balance_year_ratio>=0.15:
    balance_rt = 8
elif balance_year_ratio<0.15 and balance_year_ratio>=0.05:
    balance_rt = 4

insure_rt = 0
total_insure_count = (1 if mine_society_insure!='0' else 0) + \
                     (1 if spouse and spouse_society_insure!='0' else 0) + \
                     sum([1 if c.get('child_society_insure')!='0' else 0 for c in children])
total_biz_count = len(mine_biz_insure)+(len(spouse_biz_insure) if spouse else 0)+sum([len(c.get('biz_insure')) for c in children])
if total_insure_count==family_member_number and total_biz_count*1.0/family_member_number>=1.5:
    insure_rt = 10
if total_insure_count==family_member_number and total_biz_count*1.0/family_member_number<1.5:
    insure_rt = 7
if total_insure_count<family_member_number and total_biz_count*1.0/family_member_number>=1.5:
    insure_rt = 4
if total_insure_count<family_member_number and total_biz_count*1.0/family_member_number<1.5:
    insure_rt = 0

fin_assets_rt = 0
if fin_assets>=500000:
    income_rt = 20
elif fin_assets<500000 and fin_assets>=300000:
    income_rt = 18
elif fin_assets<300000 and fin_assets>=150000:
    income_rt = 15
elif fin_assets<150000 and fin_assets>=100000:
    income_rt = 12
elif fin_assets<100000 and fin_assets>=70000:
    income_rt = 9
elif fin_assets<70000 and fin_assets>=40000:
    income_rt = 5

estate_rt = 0
if real_estate_value:
    if real_estate_loan:
        load_ratio = round(float(real_estate_loan)/real_estate_value, 4)
        if load_ratio<=0.5:
            estate_rt = 10
        else:
            estate_rt = 5
    else:
        if real_estate_value*10000>=income_year*50:
            estate_rt = 20 #房产总值>=年收入x50，无房贷
        elif real_estate_value*10000<income_year*50 and real_estate_value*10000>=income_year*30:
            estate_rt = 18 #年收入x30<=房产总值<年收入x50，无房贷
        else:
            estate_rt = 15 #房产总值<年收入x30，无房贷
else:
    estate_rt = 0

debt_rt = 0
debt_ratio_rt = round(float(consumer_loans)/fin_assets, 4) if fin_assets!=0 else 0
if debt_ratio_rt>=0.9:
    debt_rt = 0
elif debt_ratio_rt<0.9 and debt_ratio_rt>=0.5:
    balance_rt = 5
elif debt_ratio_rt<0.5 and debt_ratio_rt>=0.2:
    balance_rt = 10
elif debt_ratio_rt<0.2 and debt_ratio_rt>=0.05:
    balance_rt = 15
else:
    balance_rt = 20

invest_exp_rt = 0
if invest_exp == '1': #5年以上
    invest_exp_rt = 10
elif invest_exp == '2': #3-5年
    invest_exp_rt = 8
elif invest_exp == '3': #1-3年
    invest_exp_rt = 5
elif invest_exp == '4': #1年以内
    invest_exp_rt = 2
elif invest_exp == '5': #无经验
    invest_exp_rt = 0

target_rt = 0
target_money = sum([t.get('money') if t.get('year')<=3 else 0 for t in target])
target_ratio = round(float(target_money)/fin_assets, 4) if fin_assets!=0 else 0
if target_ratio>=0.9:
    target_rt = 0
elif target_ratio<0.9 and target_ratio>=0.7:
    target_rt = 3
elif target_ratio<0.7 and target_ratio>=0.5:
    target_rt = 7
elif target_ratio<0.5 and target_ratio>=0.2:
    target_rt = 12
elif target_ratio<0.2 and target_ratio>0:
    target_rt = 17
else:
    target_rt = 20

rtc = sum([age_rt, career_rt, family_rt, income_rt, balance_rt, insure_rt, fin_assets_rt, estate_rt, debt_rt, invest_exp_rt, target_rt])


#意愿 风险偏好
invest_concern_rt = 0
if invest_concern == '1': #收益最大化
    invest_concern_rt = 10
elif invest_concern == '2': #本金安全性
    invest_concern_rt = 0
elif invest_concern == '3': #二者平衡
    invest_concern_rt = 5

invest_increase_rt = 0
if invest_increase == '1': #马上追加投资
    invest_increase_rt = 10
elif invest_increase == '2': #继续持有
    invest_increase_rt = 7
elif invest_increase == '3': #部分卖出
    invest_increase_rt = 4
elif invest_increase == '4': #赶紧止盈脱手
    invest_increase_rt = 0

invest_handle_rt = 0
if invest_handle == '1': #全部卖出
    invest_handle_rt = 0
elif invest_handle == '2': #部分卖出
    invest_handle_rt = 3
elif invest_handle == '3': #观望等待
    invest_handle_rt = 6
elif invest_handle == '4': #越跌越买
    invest_handle_rt = 10

invest_sit_rt = 0
invest_cur_sit_ratio = round(float(sum(non_invest+[funds_money]))/fin_assets, 4) if fin_assets!=0 else 0
if invest_cur_sit_ratio>=0.9:
    target_rt = 0
elif invest_cur_sit_ratio<0.9 and invest_cur_sit_ratio>=0.7:
    target_rt = 3
elif invest_cur_sit_ratio<0.7 and invest_cur_sit_ratio>=0.5:
    target_rt = 6
elif invest_cur_sit_ratio<0.5 and invest_cur_sit_ratio>=0.3:
    target_rt = 8
else:
    target_rt = 10

rtw = sum([invest_concern_rt, invest_increase_rt, invest_handle_rt, invest_sit_rt])

rtc_rank = 1
if rtc>=161:
    rtc_rank = 5
    rtc_rank_doc = '很强'
elif rtc<161 and rtc>=121:
    rtc_rank = 4
    rtc_rank_doc = '较强'
elif rtc<121 and rtc>=81:
    rtc_rank = 3
    rtc_rank_doc = '中等'
elif rtc<81 and rtc>=51:
    rtc_rank = 2
    rtc_rank_doc = '较弱'
elif rtc<51 and rtc>=0:
    rtc_rank = 1
    rtc_rank_doc = '很弱'

rtw_rank = 1
if rtw>=35:
    rtw_rank = 5
    rtw_rank_doc = '激进型'
elif rtw<35 and rtw>=27:
    rtw_rank = 4
    rtw_rank_doc = '进取型'
elif rtw<27 and rtw>=19:
    rtw_rank = 3
    rtw_rank_doc = '平衡型'
elif rtw<19 and rtw>=11:
    rtw_rank = 2
    rtw_rank_doc = '稳健型'
elif rtw<11 and rtw>=0:
    rtw_rank = 1
    rtw_rank_doc = '保守型'

risk_rank = rtc_rank if rtc_rank <= rtw_rank else rtw_rank

rt_rank_ratio = {'1':'0%', '2':'-5%', '3':'-10%', '4':'-15%', '5':'-20%'}
rtc_rank_ratio = rt_rank_ratio[str(rtc_rank)]
rtw_rank_ratio = rt_rank_ratio[str(rtw_rank)]
risk_rank_ratio = rt_rank_ratio[str(risk_rank)]

gh_suggest_risk_doc = '您的风险承受能力'+rtc_rank_doc+'，风险偏好属于'+rtw_rank_doc+'，请将投资风险控制在'+risk_rank_ratio+'以内。'

##############投资规划##############
# 资产配置环节所有计算均需四舍五入至百位
fin_assets_r = hundred_rounding(fin_assets)
deposit_fixed_r = hundred_rounding(deposit_fixed)
invest_bank_r = hundred_rounding(invest_bank)
invest_national_debt_r = hundred_rounding(invest_national_debt)
invest_insure_r = hundred_rounding(invest_insure)
funds_bond_r = hundred_rounding(funds_bond)
invest_p2p_r = hundred_rounding(invest_p2p)
funds_index_r = hundred_rounding(funds_index)
funds_hybrid_r = hundred_rounding(funds_hybrid)
funds_stock_r = hundred_rounding(funds_stock)
funds_other_r = hundred_rounding(funds_other)
invest_stock_r = hundred_rounding(invest_stock)
invest_metal_r = hundred_rounding(invest_metal)
invest_other_r = hundred_rounding(invest_other)

investable_assets = fin_assets_r-dep_des-fun_des
invest_assets = investable_assets if investable_assets>=2000 else 2000 #投资规划可计算最小金额


(low_risk_ratio, medium_risk_ratio, high_risk_ratio, expect_ave_return, _, _, _, _, his_ave_return, total_return) = assets_allocation = assets_allocation_data[str(risk_rank)]

raw_low_assets = [('现金及活期存款', deposit_current_r-dep_des),
                  ('货币基金', funds_money_r-fun_des),
                  ('定期存款', deposit_fixed_r),
                  ('银行理财产品', invest_bank_r),
                  ('国债', invest_national_debt_r),
                  ('储蓄型保险', invest_insure_r)]
raw_medium_assets = [('债券型基金', funds_bond_r),
                     ('P2P网贷', invest_p2p_r)]
raw_high_assets = [('指数型基金', funds_index_r),
                   ('混合型基金', funds_hybrid_r),
                   ('股票型基金', funds_stock_r),
                   ('其他基金', funds_other_r),
                   ('股票', invest_stock_r),
                   ('贵金属', invest_metal_r),
                   ('其他投资', invest_other_r)]

raw_low_assets_d = dict(raw_low_assets)
raw_medium_assets_d = dict(raw_medium_assets)
raw_high_assets_d = dict(raw_high_assets)

cur_low_assets = sum(raw_low_assets_d.values())
cur_medium_assets = sum(raw_medium_assets_d.values())
cur_high_assets = sum(raw_high_assets_d.values())

low_risk_assets = int(invest_assets*low_risk_ratio)
medium_risk_assets = int(invest_assets*medium_risk_ratio)
high_risk_assets = int(invest_assets*high_risk_ratio)

deduction_low = ['现金及活期存款','货币基金','定期存款','银行理财产品','国债', '储蓄型保险']
deduction_medium = ['P2P网贷','债券型基金']
deduction_high = ['其他投资','贵金属','股票','其他基金','混合型基金','股票型基金','指数型基金']

change_low_amount = 0
change_medium_amount = 0
change_high_amount = 0

increase_low_product = ''
increase_medium_product = ''
increase_high_product = ''

low_evl, low_act, deduction_low_plan = '','', []
medium_evl, medium_act, deduction_medium_plan = '','', []
high_evl, high_act, deduction_high_plan = '','', []

if low_risk_assets*0.95 <= cur_low_assets <= low_risk_assets*1.05:
    low_evl, low_act = '合理', '不变'
elif cur_low_assets < low_risk_assets*0.95:
    low_evl, low_act = '不足', '增持'
    change_low_amount = low_risk_assets-cur_low_assets
    if invest_bank_r:
        if change_low_amount<10000:
            increase_low_product = '国债、货币基金'
        else:
            increase_low_product = '银行理财产品、国债、货币基金'
    else:
        if change_low_amount<50000:
            increase_low_product = '国债、货币基金'
        else:
            increase_low_product = '银行理财产品、国债、货币基金'
else:
    low_evl, low_act = '过高', '减持'
    change_low_amount = cur_low_assets-low_risk_assets
    for p in deduction_low:
        if p == '储蓄型保险':
            deduction_low_plan.append((p, '不变'))
            break

        if int(change_low_amount) == 0:
            break
        p_amount = raw_low_assets_d[p]
        if int(p_amount) == 0:
            continue
        if p_amount <= change_low_amount:
            deduction_low_plan.append((p, p_amount))
            change_low_amount -= p_amount
        else:
            deduction_low_plan.append((p, change_low_amount))
            break
    change_low_amount = cur_low_assets-low_risk_assets

if medium_risk_assets*0.95 <= cur_medium_assets <= medium_risk_assets*1.05:
    medium_evl, medium_act = '合理', '不变'
elif cur_medium_assets < medium_risk_assets*0.95:
    medium_evl, medium_act = '不足', '增持'
    increase_medium_product = '二级债券型基金、P2P网贷'
    change_medium_amount = medium_risk_assets-cur_medium_assets
else:
    medium_evl, medium_act = '过高', '减持'
    change_medium_amount = cur_medium_assets-medium_risk_assets
    for p in deduction_medium:
        p_amount = raw_medium_assets_d[p]
        if int(change_medium_amount) == 0:
            break
        if int(p_amount) == 0:
            continue
        if p_amount <= change_medium_amount:
            deduction_medium_plan.append((p, p_amount))
            change_medium_amount -= p_amount
        else:
            deduction_medium_plan.append((p, change_medium_amount))
            break
    change_medium_amount = cur_medium_assets-medium_risk_assets

if high_risk_assets*0.95 <= cur_high_assets <= high_risk_assets*1.05:
    high_evl, high_act = '合理', '不变'
elif cur_high_assets < high_risk_assets*0.95:
    high_evl, high_act = '不足', '增持'
    increase_high_product = '股票型基金、指数型基金'
    change_high_amount = high_risk_assets-cur_high_assets
else:
    high_evl, high_act = '过高', '减持'
    change_high_amount = cur_high_assets-high_risk_assets
    for p in deduction_high:
        p_amount = raw_high_assets_d[p]
        if int(change_high_amount) == 0:
            break
        if int(p_amount) == 0:
            continue
        if p_amount <= change_high_amount:
            deduction_high_plan.append((p, p_amount))
            change_high_amount -= p_amount
        else:
            deduction_high_plan.append((p, change_high_amount))
            break
    change_high_amount = cur_high_assets-high_risk_assets

# 规划书波动图
fluctuation_risk_data = [{'name':'好规划推荐方案', 'data': [str(i*100) for i in average_earning_data.get(str(risk_rank))[:-1]]},
                         {'name':'激进投资方案', 'data': [str(i*100) for i in average_earning_data.get('6')[:-1]]}]

fluctuation_risk_data_gh = '|'.join(fluctuation_risk_data[0].get('data'))
fluctuation_risk_data_jj = '|'.join(fluctuation_risk_data[1].get('data'))

#fluctuation_risk_name = ['好规划推荐方案', '激进投资方案']
#fluctuation_risk_data = [[i*100 for i in average_earning_data.get(str(risk_rank))[:-1]], [i*100 for i in average_earning_data.get('6')[:-1]]]

# 预备变量
target_balance_year = income_year*target_balance_month_ratio if income_year*target_balance_month_ratio>balance_year else balance_year

est_balance = [target_balance_month_ratio*income_year*1.1**n for n in range(5)] #五年收支结余预估
est_balance[0] = target_balance_year

est_ave = [0]*5 #投资收益
est_assets_growth = [0]*5 #可投资资产增长值
est_assets = [0]*5 #可投资资产总值

for y in range(5):
    if y ==0:
        est_ave[y] = invest_assets*expect_ave_return
        est_assets_growth[y] = est_balance[y]+est_ave[y]
        est_assets[y] = invest_assets+est_assets_growth[y]
    else:
        est_ave[y] = est_assets[y-1]*expect_ave_return
        est_assets_growth[y] = est_balance[y]+est_ave[y]
        est_assets[y] = est_assets[y-1]+est_assets_growth[y]

est_assets = [invest_assets]+est_assets

value_predict_data = [{'name': '收支结余','data': [str(hundred_rounding(i)) for i in est_balance], 'color': '#FFB56E'},
                      {'name': '投资收益','data': [str(hundred_rounding(i)) for i in est_ave], 'color': '#70C862'},
                      {'name': '可投资资产总值','data': [str(hundred_rounding(i)) for i in est_assets[:-1]], 'color': '#727BC6'}]

value_predict_data_balance = '|'.join(value_predict_data[0].get('data'))
value_predict_data_invest = '|'.join(value_predict_data[1].get('data'))
value_predict_data_assets = '|'.join(value_predict_data[2].get('data'))

gh_suggest_invest_doc = '您现有可投资资产'+format(investable_assets,',')+'元，建议按照'+dec_2_pct(low_risk_ratio)+'：'+dec_2_pct(medium_risk_ratio)+'：'+dec_2_pct(high_risk_ratio)+'的比例，分别配置低风险、中等风险和高风险资产，实现约'+dec_2_pct(expect_ave_return, place=2)+'的预期年化收益率。'

gh_suggest_invest_low_act = ''
gh_suggest_invest_medium_act = ''
gh_suggest_invest_high_act = ''

if low_act == '不变':
    gh_suggest_invest_low_act = '保持共'+format(cur_low_assets,',')+'元不变，并持续优化产品选择。'
elif deduction_low_plan:
    gh_suggest_invest_low_act = '减持'
    temp_suggest_invest = []
    for (name, p) in deduction_low_plan:
        if p !='不变':
            temp_suggest_invest.append(name+format(p,',')+'元')
    gh_suggest_invest_low_act += '、'.join(temp_suggest_invest)
elif increase_low_product:
    gh_suggest_invest_low_act = '增持'+increase_low_product+'共'+format(change_low_amount,',')+'元'
    increase_low_product = '推荐品种：'+increase_low_product
gh_suggest_invest_low_act = '低风险资产：'+gh_suggest_invest_low_act

if medium_act == '不变':
    gh_suggest_invest_medium_act = '保持共'+format(cur_medium_assets,',')+'元不变，并持续优化产品选择。'
elif deduction_medium_plan:
    gh_suggest_invest_medium_act = '减持'
    temp_suggest_invest = []
    for (name, p) in deduction_medium_plan:
        temp_suggest_invest.append(name+format(p,',')+'元')
    gh_suggest_invest_medium_act += '、'.join(temp_suggest_invest)
elif increase_medium_product:
    gh_suggest_invest_medium_act = '增持'+increase_medium_product+'共'+format(change_medium_amount,',')+'元'
    increase_medium_product = '推荐品种：'+increase_medium_product
gh_suggest_invest_medium_act = '中风险资产：'+gh_suggest_invest_medium_act

if high_act == '不变':
    gh_suggest_invest_high_act = '保持共'+format(cur_high_assets,',')+'元不变，并持续优化产品选择。'
elif deduction_high_plan:
    gh_suggest_invest_high_act = '减持'
    temp_suggest_invest = []
    for (name, p) in deduction_high_plan:
        temp_suggest_invest.append(name+format(p,',')+'元')
    gh_suggest_invest_high_act += '、'.join(temp_suggest_invest)
elif increase_high_product:
    gh_suggest_invest_high_act = '增持'+increase_high_product+'共'+format(change_high_amount,',')+'元'
    increase_high_product = '推荐品种：'+increase_high_product
gh_suggest_invest_high_act = '高风险资产：'+gh_suggest_invest_high_act

##############保险计划##############
social_insure_dict = {'0':'无社保',
                      '1':'五险（标准）',
                      '2':'四险（少生育险）',
                      '3':'三险（少生育、工伤险）',
                      '4':'六险（多大额补充医保）',
                      '5':'个人缴纳社保',
                      '6':'新农合、农村养老险',
                      '7':'公务员社保（免缴）',
                      '8':'少儿医保、学生医保'}

biz_insure_dict = {'0':'无',
                   '1':'重疾险',
                   '2':'综合意外险',
                   '3':'定期寿险',
                   '4':'医疗险',
                   '5':'儿童综合险',
                   '6':'养老险',
                   '7':'教育年金险',
                   '8':'其他险种'}

insure_plan = ['社保','2','1','3'] #社保、意外、重疾、寿险
spouse_insure_plan = ['社保','2','1','3']

sum_insured_1 = 0 # 重疾
sum_insured_2 = 0 # 意外
sum_insured_3 = 0 # 寿险

cur_insure_stat_doc = ''

balance_year_inc_ratio = 1.1

#本人计划
if spouse:
    #有配偶
    if int(age)<35:
        # A21
        cur_insure_stat_doc = '目前，您有一定的家庭负担；较年轻、健康风险较小；同时收入、结余、资产规模在未来仍有较大上升空间。'
        #寿险
        if income_year:
            temp_spouse = 0
            for y in range(10):
                sum_insured_3 += (expend_year*balance_year_inc_ratio**y-expend_month_house*12)*0.75/(1+expect_ave_return)**y
                temp_spouse += (spouse_income_year*balance_year_inc_ratio**y)/(1+expect_ave_return)**y
            sum_insured_3 = sum_insured_3+(float(mine_income_year)/income_year*total_debt)-investable_assets-temp_spouse
        if sum_insured_3<100000:
            sum_insured_3 = 0
            for y in range(10):
                sum_insured_3+=(mine_income_year-expend_year*0.35)*balance_year_inc_ratio**y/(1+expect_ave_return)**y
            sum_insured_3 = max(sum_insured_3, 100000)
        #意外
        sum_insured_2 = sum_insured_3*1.5
        #重疾
        sum_insured_1 = 100000+expend_year*2
    else:
        cur_insure_stat_doc = '目前，您家庭负担较重；且年龄渐长，需开始预防健康问题；同时已有一定资产积累。'
        m = 0 # 计算对方实际年限
        l = 0 # 计算实际年限
        if gender=='male':
            # A22m
            m = min(15, 55-spouse_age)
            l = min(15, 60-age)
        else:
            # A22f
            m = min(15, 60-spouse_age)
            l = min(15, 55-age)
        #寿险
        if income_year:
            for y in range(15):
                sum_insured_3 += (expend_year*balance_year_inc_ratio**y-expend_month_house*12)*0.75/(1+expect_ave_return)**y
            temp_spouse = 0
            for y in range(m):
                temp_spouse+=(spouse_income_year*balance_year_inc_ratio**y)/(1+expect_ave_return)**y
            sum_insured_3 = sum_insured_3+(float(mine_income_year)/income_year*total_debt)-investable_assets-temp_spouse
        if sum_insured_3<100000:
            sum_insured_3 = 0
            for y in range(l):
                sum_insured_3+=(mine_income_year-expend_year*0.35)*balance_year_inc_ratio**y/(1+expect_ave_return)**y
            sum_insured_3 = max(sum_insured_3, 100000)
        #意外
        sum_insured_2 = sum_insured_3*1.5
        #重疾
        sum_insured_1 = 150000+expend_year*2
else:
    #无配偶
    if children:
        cur_insure_stat_doc = '目前，您独自抚养子女，家庭负担较重，尤其应注意健康和意外风险，同时应保证收入来源的稳定。'
        # A13
        #寿险
        for y in range((18-int(children[0].get('age')))):# TODO 考虑某个孩子
            sum_insured_3 += (expend_year*balance_year_inc_ratio**y-expend_month_house*12)/(1+expect_ave_return)**y
        sum_insured_3 = sum_insured_3+total_debt-investable_assets
        sum_insured_3 = max(sum_insured_3, 100000)
        #意外
        sum_insured_2 = sum_insured_3*1.5
        #重疾
        sum_insured_1 = 150000+expend_year*2
    else:
        if age<30:
            cur_insure_stat_doc = '目前，您未婚单身、家庭负担很小；年轻、自身的健康风险也较小；同时收入、结余、个人资产规模都处在成长期。'
            # A11
            insure_plan = ['社保','2','1'] #社保、意外、重疾
            #意外
            for y in range(20):
                sum_insured_2+=target_balance_year*balance_year_inc_ratio**y/(1+expect_ave_return)**y
            sum_insured_2 = max(sum_insured_2, 100000)
            #重疾
            sum_insured_1 = 100000+expend_year*2
        else:
            cur_insure_stat_doc = '目前，您未婚单身、家庭负担很小；年龄渐长，需开始预防健康问题；收入、结余、资产规模应处于稳定增长期。'
            # A12
            m = 0 # 计算本人实际年限
            if gender=='male':
                # A12m
                m = min(20, 60-age)
            else:
                # A12f
                m = min(20, 55-age)
            #寿险
            for y in range(m):
                sum_insured_3+=target_balance_year*balance_year_inc_ratio**y/(1+expect_ave_return)**y
            sum_insured_3 = max(sum_insured_3, 100000)
            #意外
            sum_insured_2 = sum_insured_3*1.5
            #重疾
            sum_insured_1 = 150000+expend_year*2
insure_plan[1] = (insure_plan[1], sum_insured_2)
insure_plan[2] = (insure_plan[2], sum_insured_1)
if len(insure_plan) == 4:
    insure_plan[3] = (insure_plan[3], sum_insured_3)

sum_insured_1 = 0 # 重疾
sum_insured_2 = 0 # 意外
sum_insured_3 = 0 # 寿险
#配偶计划
if spouse:
    if spouse_age<35:
        # B21
        #寿险
        temp_mine = 0
        if income_year:
            for y in range(10):
                sum_insured_3 += (expend_year*balance_year_inc_ratio**y-expend_month_house*12)*0.75/(1+expect_ave_return)**y
                temp_mine+=(mine_income_year*balance_year_inc_ratio**y)/(1+expect_ave_return)**y
            sum_insured_3 = sum_insured_3+(float(spouse_income_year)/income_year*total_debt)-investable_assets-temp_mine
        if sum_insured_3<100000:
            sum_insured_3 = 0
            for y in range(10):
                sum_insured_3+=(spouse_income_year-expend_year*0.35)*balance_year_inc_ratio**y/(1+expect_ave_return)**y
            sum_insured_3 = max(sum_insured_3, 100000)
        #意外
        sum_insured_2 = sum_insured_3*1.5
        #重疾
        sum_insured_1 = 100000+expend_year*2
    else:
        m = 0 # 计算对方实际年限
        l = 0 # 计算实际年限
        if gender=='female':
            # B22m 配偶性别
            m = min(15, 55-age)
            l = min(15, 60-spouse_age)
        else:
            # B22f
            m = min(15, 60-age)
            l = min(15, 55-spouse_age)
        #寿险
        if income_year:
            for y in range(15):
                sum_insured_3 += (expend_year*balance_year_inc_ratio**y-expend_month_house*12)*0.75/(1+expect_ave_return)**y
            temp_mine = 0
            for y in range(m):
                temp_mine+=(mine_income_year*balance_year_inc_ratio**y)/(1+expect_ave_return)**y
            sum_insured_3 = sum_insured_3+(float(spouse_income_year)/income_year*total_debt)-investable_assets-temp_mine
        if sum_insured_3<100000:
            sum_insured_3 = 0
            for y in range(l):
                sum_insured_3+=(spouse_income_year-expend_year*0.35)*balance_year_inc_ratio**y/(1+expect_ave_return)**y
            sum_insured_3 = max(sum_insured_3, 100000)
        #意外
        sum_insured_2 = sum_insured_3*1.5
        #重疾
        sum_insured_1 = 150000+expend_year*2

spouse_insure_plan[1] = (spouse_insure_plan[1], sum_insured_2)
spouse_insure_plan[2] = (spouse_insure_plan[2], sum_insured_1)
spouse_insure_plan[3] = (spouse_insure_plan[3], sum_insured_3)

cur_mine_insure = {'社保':social_insure_dict.get(mine_society_insure)}
for insure in mine_biz_insure:
    cur_mine_insure[insure['insure_type']] = {'insure_quota':insure['insure_quota'],'insure_year_fee':insure['insure_year_fee']}

target_mine_insure = []
target_mine_insure_d = []
for insure in insure_plan:
    if insure=='社保':
        if cur_mine_insure[insure] == social_insure_dict['0']:
            # 无社保
            target_mine_insure.append(insure)
            target_mine_insure_d.append(insure)
        else:
            continue
    else:
        (insure_plan_type, sum_insured) = insure
        if insure_plan_type in cur_mine_insure:
            continue
        else:
            target_mine_insure.append(insure)
            target_mine_insure_d.append(biz_insure_dict[insure_plan_type])

cur_spouse_insure = {}
target_spouse_insure = []
target_spouse_insure_d = []
if spouse:
    cur_spouse_insure = {'社保':social_insure_dict.get(spouse_society_insure)}
    for insure in spouse_biz_insure:
        cur_spouse_insure[insure['insure_type']] = {'insure_quota':insure['insure_quota'],'insure_year_fee':insure['insure_year_fee']}
    for insure in spouse_insure_plan:
        if insure=='社保':
            if cur_spouse_insure[insure] == social_insure_dict['0']:
                # 无社保
                target_spouse_insure.append(insure)
                target_spouse_insure_d.append(insure)
            else:
                continue
        else:
            (insure_plan_type, sum_insured) = insure
            if insure_plan_type in cur_spouse_insure:
                continue
            else:
                target_spouse_insure.append(insure)
                target_spouse_insure_d.append(biz_insure_dict[insure_plan_type])

cur_children_insure = []
target_children_insure = []
target_children_insure_d = []
for child in children:
    child_society_insure = child.get('child_society_insure')
    child_biz_insure = child.get('biz_insure')

    cur_child_insure = {}
    target_child_insure = []
    target_child_insure_d = []
    cur_child_insure = {'社保':social_insure_dict.get(child_society_insure)}
    for insure in child_biz_insure:
        cur_child_insure[insure['insure_type']] = {'insure_quota':insure['insure_quota'],'insure_year_fee':insure['insure_year_fee']}
    if cur_child_insure['社保'] != social_insure_dict['8']:
        # 无社保
        target_child_insure.append('社保')
        target_child_insure_d.append('社保')
    if '5' not in cur_child_insure:
        # 无少儿综合险
        target_child_insure.append(('5', 100000))
        target_child_insure_d.append(biz_insure_dict['5'])
    cur_children_insure.append(cur_child_insure)
    target_children_insure.append(target_child_insure)
    target_children_insure_d.append(target_child_insure_d)

is_full_insured = False if target_mine_insure or target_spouse_insure or (target_children_insure and reduce(lambda x,y:x or y, target_children_insure)) else True

insure_suggest_doc = ''
if is_full_insured:
    insure_suggest_doc = '持续优化保险规划。'
else:
    insure_suggest_doc_d = []
    insure_suggest_doc_d.append(('本人' if relation_number else '')+'补充'+('、'.join(target_mine_insure_d[:-1])+'和'+target_mine_insure_d[-1] if len(target_mine_insure_d)>1 else target_mine_insure_d[0]) if target_mine_insure_d else '')
    if spouse:
        insure_suggest_doc_d.append('配偶补充'+('、'.join(target_spouse_insure_d[:-1])+'和'+target_spouse_insure_d[-1] if len(target_spouse_insure_d)>1 else target_spouse_insure_d[0]) if target_spouse_insure_d else '')
    for index, ci in enumerate(target_children_insure_d):
        if ci:
            insure_suggest_doc_d.append('子女'+str(index+1)+'（'+children[index].get('age')+'岁）补充'+(ci[0]+'和'+ci[1] if len(ci)==2 else ci[0]))
    insure_suggest_doc = '；'.join(insure_suggest_doc_d)

target_insure_plan = []
target_insure_explain_key = []
for p in target_mine_insure:
    insured_man = '本人'
    insured_type = '参投社保' if p=='社保' else '购买'+biz_insure_dict.get(p[0])
    insured_sum = '-' if p=='社保' else format(ten_thou_rounding(int(p[1]))/10000,',')+'万元'
    insured_fee = ''
    if p=='社保':
        insured_fee = '月工资 5% - 10%'
        p_name = p
    else:
        if p[0] == '1':
            #重疾险
            insured_fee = format(ten_rounding(int(p[1])/100000.0*800),',')
            p_name = '重疾险'
        elif p[0] == '2':
            #意外险
            insured_fee = format(ten_rounding(int(p[1])/100000.0*80),',')
            p_name = '意外险'
        elif p[0] == '3':
            #寿险
            insured_fee = format(ten_rounding(int(p[1])/100000.0*100),',')
            p_name = '寿险'
    insured_fee = insured_fee+'元/年'
    target_insure_plan.append((insured_man, insured_type, insured_sum, insured_fee))
    if p_name not in target_insure_explain_key:
        target_insure_explain_key.append(p_name)

for p in target_spouse_insure:
    insured_man = '配偶'
    insured_type = '参投社保' if p=='社保' else '购买'+biz_insure_dict.get(p[0])
    insured_sum = '-' if p=='社保' else format(ten_thou_rounding(int(p[1]))/10000,',')+'万元'
    insured_fee = ''
    if p=='社保':
        insured_fee = '月工资 5% - 10%'
        p_name = p
    else:
        if p[0] == '1':
            #重疾险
            insured_fee = format(ten_rounding(int(p[1])/100000.0*800),',')
            p_name = '重疾险'
        elif p[0] == '2':
            #意外险
            insured_fee = format(ten_rounding(int(p[1])/100000.0*80),',')
            p_name = '意外险'
        elif p[0] == '3':
            #寿险
            insured_fee = format(ten_rounding(int(p[1])/100000.0*100),',')
            p_name = '寿险'
    insured_fee = insured_fee+'元/年'
    target_insure_plan.append((insured_man, insured_type, insured_sum, insured_fee))
    if p_name not in target_insure_explain_key:
        target_insure_explain_key.append(p_name)
for index, child_p in enumerate(target_children_insure):
    for p in child_p:
        insured_man = '子女%s（%s岁）'%(index+1, children[index].get('age'))
        insured_type = '参投少儿医保' if p=='社保' else '购买儿童综合险'
        insured_sum = '-' if p=='社保' else '10万元'
        insured_fee = '50-250元/年' if p=='社保' else '200-500元/年'
        target_insure_plan.append((insured_man, insured_type, insured_sum, insured_fee))
        if p=='社保':
            p_name = '少儿医保'
        else:
            p_name = '儿童险'
        if p_name not in target_insure_explain_key:
            target_insure_explain_key.append(p_name)

target_insure_plan_d = {}
for p in target_insure_plan:
    data = target_insure_plan_d.get(p[0], [])
    data.append([p[1][6:], p[2], p[3]]) # 去掉 “购买”“参投”二字
    target_insure_plan_d[p[0]] = data

gh_suggest_insure_doc = ''
if not is_full_insured:
    gh_suggest_insure_doc = ('为家庭' if relation_number else '')+'建立必要且基本的保障，'+insure_suggest_doc+'。'
else:
    gh_suggest_insure_doc = '您'+('与家人' if relation_number else '')+'已经具备基础保障，请持续优化保险规划。'

gh_suggest_insure_act = []
for p in target_insure_plan:
    act_insured_sum = '' if p[2] == '-' else '保额%s，'%p[2]
    suggest_insure_act = '为%s%s，%s保费约为%s'%(p[0],p[1],act_insured_sum,p[3])
    suggest_insure_type =  p[1][6:] if p[2] != '-' else '' #p[1][2:]将险种前面的行为动词去掉'参保'，'购买'
    gh_suggest_insure_act.append((suggest_insure_act,suggest_insure_type))


##############理财目标##############
expect_income_ratio = 0.1 #预期收入增长率

target = sorted(target, key=lambda x:int(x.get('year')))

general_target = multi_targets(target, investable_assets, income_year, expect_ave_return, expect_income_ratio, target_balance_month_ratio)

general_target_status = len(filter(lambda i:'x' in i and i.get('x')>1, general_target))

gh_suggest_target_doc = '以'+dec_2_pct(target_balance_month_ratio)+'的结余率、'+dec_2_pct(expect_income_ratio)+'的年收入增长率、'+dec_2_pct(expect_ave_return)+'的投资收益率，逐渐达成理财目标。'

# pylint: enable=E0601,E0602
