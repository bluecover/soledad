# -*- coding: utf-8 -*-

"""
礼券全民群发
"""

from datetime import datetime
from more_itertools import chunked

from libs.db.store import db
from core.models.user.consts import ACCOUNT_STATUS
from core.models.welfare import Coupon, Package
from core.models.welfare.package.kind import (
    migration_compensation_package as distribution_package)


def get_package_by_user(user_id, package_kind_id):
    sql = 'select id from coupon_package where user_id=%s and kind_id=%s'
    rs = db.execute(sql, (user_id, package_kind_id))
    return [r[0] for r in rs]


def get_all_users():
    sql = 'select id from account where status=%s'
    rs = db.execute(sql, ACCOUNT_STATUS.NORMAL)
    return [r[0] for r in rs]


def create_package(user_id, package_kind_id):
    # if get_package_by_user(user_id, package_kind_id):
    #     print 'already created package for %s' % user_id
    #     return

    sql = ('insert into coupon_package (user_id, kind_id, status, unpacked_time, '
           'creation_time) values (%s, %s, %s, %s, %s)')
    params = (user_id, package_kind_id, Package.Status.in_pocket.value,
              datetime.now(), datetime.now())
    p_id = db.execute(sql, params)
    Package.clear_cache(p_id)
    Package.clear_cache_by_user(user_id)
    return p_id


def create_package_distribution_record(user_id, package_id):
    sql = ('insert into coupon_package_sunny_world (user_id, package_id, '
           'creation_time) values (%s, %s, %s)')
    params = (user_id, package_id, datetime.now())
    db.execute(sql, params)


def create_coupon(name, user_id, kind_id, package_id, platforms,
                  product_matcher_kind_id, expire_time):
    sql = ('insert into coupon (name, user_id, kind_id, package_id, status, '
           'platforms, product_matcher_kind_id, creation_time, expire_time) '
           'values (%s, %s, %s, %s, %s, %s, %s, %s, %s)')
    params = (name, user_id, kind_id, package_id, Coupon.Status.in_wallet.value,
              ','.join([p.value for p in platforms]), product_matcher_kind_id,
              datetime.now(), expire_time)
    id_ = db.execute(sql, params)
    Coupon.clear_cache(id_)
    Coupon.clear_user_coupon_ids_cache(user_id)
    Coupon.clear_package_coupon_ids_cache(package_id)


def distribute_coupon_to_user(user_id):
    if not user_id:
        print 'User %s not found' % user_id
        return

    try:
        package_id = create_package(user_id, distribution_package.id_)
        if package_id is None:
            print 'creating package for %s failed' % user_id
            return
        create_package_distribution_record(user_id, package_id)
        for wrapper in distribution_package.coupon_wrappers:
            for _ in xrange(wrapper.amount):
                create_coupon(
                    wrapper.name, user_id, wrapper.kind.id_, package_id,
                    wrapper.platforms, wrapper.product_matcher_kind.id_,
                    wrapper.expire_time)
    except Exception as e:
        print '****Distribute coupon error for %s:%s' % (user_id, e)
        return


def run():
    all_user_ids = get_all_users()
    for seq, user_ids in enumerate(chunked(all_user_ids, 100)):
        print '*发放第%d批次(每批次100人)' % (seq + 1)
        for uid in user_ids:
            distribute_coupon_to_user(uid)
        db.commit()

if __name__ == '__main__':
    run()
