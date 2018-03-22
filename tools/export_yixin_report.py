#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
宜人贷订单导出
"""

import sys
import getopt
import csv

from libs.db.store import db
from core.models.hoard.order import HoardOrder, OrderStatus
from core.models.hoard.profile import HoardProfile
from core.models.hoard.account import YixinAccount


def genernate_report(filename, date):

    csv_file = open(filename, 'wb')
    writer = csv.writer(csv_file, delimiter=',')
    header = ['理财单号', '订单号', '宜人贷账号', '宜定盈名称',
              '订单状态', '订单金额', '创建时间']
    writer.writerow(header)
    year, month = date.split('-')

    sql = 'select id from hoard_order where status="C" \
            and year(creation_time)=%s and month(creation_time)=%s'
    params = (year, month)
    rs = db.execute(sql, params)
    orders = [HoardOrder.get(r[0]) for r in rs]

    if orders is not None:
        for order in orders:
            if order.order_id is None:
                continue
            profile = HoardProfile.get(order.user_id)
            yixin_account = YixinAccount.get_by_local(
                profile.account_id) if profile else ''
            p2p_account = yixin_account.p2p_account if yixin_account else ''
            p2p_service_name = (order.service.p2pservice_name
                                if order.service else '')

            if order.status == OrderStatus.paid:
                order_status = '已支付'
            elif order.status == OrderStatus.unpaid:
                order_status = '未支付'
            elif order.status == OrderStatus.confirmed:
                order_status = '已确认'
            elif order.status == OrderStatus.failure:
                order_status = '失败'
            else:
                order_status = '未知'

            line = [
                str(order.fin_order_id),
                str(order.order_id),
                str(p2p_account),
                str(p2p_service_name),
                order_status,
                int(order.order_amount),
                order.creation_time.strftime('%Y-%m-%d %H:%M')]

            writer.writerow(line)

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
