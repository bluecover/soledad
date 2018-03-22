# -*- coding: utf-8 -*-

"""
批量取消未支付新米订单工具
"""

from jupiter.workers import hoard_xm
from libs.db.store import db


def cancel_unpaid_orders():
    sql = 'SELECT order_code FROM hoard_xm_order WHERE status=%s;'
    rs = db.execute(sql, ('U',))
    for r in rs:
        hoard_xm.xm_cancel_order_prepare.produce(str(r[0]))


if __name__ == '__main__':
    cancel_unpaid_orders()
