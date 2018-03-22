#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
获取每天转出资产并更新
"""

from datetime import date, timedelta

from jupiter.app import create_app
from libs.db.store import db
from core.models.hoard.zhiwang import ZhiwangAsset, ZhiwangProfile


app = create_app()


def get_redeeming_assets_by_period(check_end):
    sql = ('select asset_no from hoard_zhiwang_asset where '
           'status!=%s and date(expect_payback_date) <= %s ')
    params = (ZhiwangAsset.Status.redeemed.value, check_end)
    rs = db.execute(sql, params)

    for r in rs:
        yield ZhiwangAsset.get_by_asset_no(r[0])


def main():
    # 获取所有到期日在明天之前的资产
    tomorrow = date.today() + timedelta(days=1)

    with app.app_context():
        for index, asset in enumerate(get_redeeming_assets_by_period(tomorrow)):
            profile = ZhiwangProfile.add(asset.user_id)
            profile.synchronize_asset(asset.asset_no)


if __name__ == '__main__':
    main()
