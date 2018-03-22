#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指旺订单导出
"""

import sys
import getopt
import csv

from libs.db.store import db
from core.models.hoard.zhiwang import ZhiwangOrder, ZhiwangAsset


def genernate_report(filename, time_str):
    csv_file = open(filename, 'wb')
    writer = csv.writer(csv_file, delimiter=',')
    header = ['订单编号', '资产编号', '订单金额', '支付金额', '基础利率', '实际利率', '下单时间']
    writer.writerow(header)
    year, month = time_str.split('-')

    sql = ('select id from hoard_zhiwang_order where status=%s'
           'and year(creation_time)=%s and month(creation_time)=%s')
    params = (ZhiwangOrder.Status.success.value, year, month)
    rs = db.execute(sql, params)
    orders = [ZhiwangOrder.get(r[0]) for r in rs]

    for order in orders:
        line = [0] * len(header)
        asset = ZhiwangAsset.get_by_order_code(order.order_code)
        if not asset:
            # asset not found for specific order code
            line[0] = order.order_code
            line[1] = '[故障单]'
            writer.writerow(line)
            continue
        line = [
            order.order_code,
            asset.asset_no,
            '%.2f' % order.amount,
            '%.2f' % (order.pay_amount or order.amount),  # compatible
            '%.2f' % asset.annual_rate,
            '%.2f' % asset.actual_annual_rate,
            order.creation_time
        ]
        writer.writerow([str(o) for o in line])
    csv_file.close()

USAGE = 'Usage Example: -f /var/tmp/report.csv -d 2015-02'

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:d:')
    except getopt.GetoptError as e:
        print(USAGE)
        sys.exit(2)
    filename = ''
    date = ''
    for o, a in opts:
        if o == '-f':
            filename = a
        elif o == '-d':
            date = a
        else:
            print(USAGE)
    if filename and date:
        genernate_report(filename, date)
        print 'Done!'
    else:
        print(USAGE)
