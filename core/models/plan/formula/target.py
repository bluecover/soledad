# -*- coding: utf-8 -*-

import copy

#  w    预期收益率
#  i    收入年增长率
#  m    月结余率（也视为年结余率）


def multi_targets(target, earning, income_year, w, i, m):
    '''
    目标计算
        target: 目标
        earning: 可投资资产
        income_year: 年收入
    '''
    data = []
    start_money = earning
    start_year = 0  # 剩余的年限
    for index, tar in enumerate(target):
        t = copy.deepcopy(tar)
        year = int(t.get('year'))-start_year
        t_money = int(t.get('money'))

        p = 0
        for y in range(year+1):
            # 第一年当年剩余资产，否则用年收入
            start_money = start_money if y == 0 else income_year
            m = 1 if y == 0 else m
            p += (start_money*(i+1)**y)*m*(1+w)**(year-y)

        x = round(float(p)/t_money, 4)
        t['p'] = p
        t['x'] = x
        t['rate'] = min(x, 1)
        data.append(t)

        # 不以100%完成为首要任务
        start_money = p - t_money if x >= 1 else 0

        # 目标按年限排序，当前计算的年为当前目标的年限
        start_year = int(t.get('year'))

    return data


def advance_targets(target, earning, income_year, revenue, income, balance):
    '''
    进阶目标计算方案
    '''

    def _get_rank(w, i, m):
        '''
        取值rank
        '''
        value = (round(float(w-revenue[0])/revenue[0], 2) +
                 round(float(i-income[0])/income[0], 2) +
                 round(float(m-balance[0])/balance[0], 2))
        return value

    achievement = {}
    for w in revenue:
        for i in income:
            for m in balance:
                data = multi_targets(target, earning, income_year, w, i, m)
                achievement[(w, i, m)] = data

    # 最优解
    answer = [[] for i in range(len(target)+1)]
    for k, v in achievement.iteritems():
        value = _get_rank(*k)
        finished = filter(lambda i: 'x' in i and i.get('x') > 1, v)
        if len(finished) == len(target):
            rs_key = 0
            rs_value = [value, k]+v
        else:
            rs_key = len(finished)
            rs_value = [value, k]+v
        data = answer[rs_key]
        data.append(rs_value)
        answer[rs_key] = data

    # print answer
    rs_data = None
    if answer[0]:
        # 所有目标都可以实现
        data = sorted(answer[0], key=lambda i: i[0])  # 按rank从小到大排序
        t_rank = data[0][0]
        # rank最小的取出来，可能为多个最小的
        data = filter(lambda d: d[0] == t_rank, data)
        if len(data) > 1:
            w_ratio, i_ratio, m_ratio = 1, 1, 1
            for d in data:
                (_, (w, i, m), _) = d
                w_r = float(w-revenue[0])/revenue[0]
                i_r = float(i-income[0])/income[0]
                m_r = float(m-balance[0])/balance[0]
                if w_r < w_ratio or (w_r == w_ratio and m_r < m_ratio):
                    rs_data = d
                    w_ratio, i_ratio, m_ratio = w_r, i_r, m_r  # noqa
        else:
            rs_data = data[0]
        return rs_data[1], rs_data[2:]
    else:
        '''
        没有可以完全实现的数据
        各个参数全部取最大值
        '''
        (w, i, m) = (revenue[-1], income[-1], balance[-1])
        data = multi_targets(target, earning, income_year, w, i, m)
        return (w, i, m), data
