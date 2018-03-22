# coding: utf-8

"""
导出规划书中的信息供用户画像
"""

import json
import datetime
import logging

import gb2260
from babel.dates import format_timedelta

from jupiter.app import create_app
from jupiter.integration.bearychat import BearyChat
from core.models.decorators import coerce_type
from core.models.plan.plan import Plan
from core.models.plan.report import Report
from libs.db.store import db
from libs.fs.fs import QiniuFS


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

bearychat = BearyChat('data')
fs = QiniuFS('guihua-internal', 'http://7xnqtg.dl1.z0.glb.clouddn.com')
fs_expires = datetime.timedelta(minutes=30)

CAREERS = {
    '1': '公务员',
    '2': '国企、事业单位职工',
    '3': '私企、外企职工',
    '4': '私营业主、自由职业者',
    '5': '学生',
    '6': '待业',
    '7': '其他',
}


def export_by_user(user_id):
    plan = Plan.get_by_user_id(user_id)
    report = Report.get_latest_by_plan_id(plan.id)

    if not plan or not report:
        return

    career = plan.data.get('career')
    city = gb2260.search(plan.data.get('city'))
    has_spouse = bool(int(plan.data.get('spouse') or '0'))
    has_children = bool(plan.data.get('children') or [])
    monthly_salary = plan.data.get('income_month_salary')
    rtc_rank_ratio = report.inter_data['rtc_rank_ratio']

    if city is None:
        logger.warning('ignore invalid city: %s' % plan.data.get('city'))
        return

    return {
        'career': career, 'province': city.province.name,
        'prefecture': city.prefecture.name, 'has_spouse': has_spouse,
        'has_children': has_children, 'monthly_salary': monthly_salary,
        'rtc_rank_ratio': rtc_rank_ratio, 'user_id': user_id}


@coerce_type(list)
def export_by_multi_users(user_ids):
    for user_id in user_ids:
        item = export_by_user(user_id)
        if item is not None:
            yield item


def get_all_user_ids():
    rs = db.execute('select distinct user_id from user_plan')
    ids = [r[0] for r in rs]
    ids.sort()
    return ids


def main():
    if not bearychat.configured:
        logger.error('bearychat is not configured')
        return

    logger.info('collecting users')
    user_ids = get_all_user_ids()

    logger.info('collecting profiles')
    user_profiles = export_by_multi_users(user_ids)

    logger.info('processing data')
    upload_files = {
        'profiles.json': json.dumps(user_profiles),
        'careers.json': json.dumps(CAREERS)}
    upload_folder = 'plan-profile/%s' % datetime.datetime.utcnow().isoformat()
    upload_links = []

    for name, content in upload_files.iteritems():
        logger.info('uploading %s' % name)
        upload_key = '%s/%s' % (upload_folder, name)
        fs.upload(content, 'application/json', upload_key)
        url = fs.get_url(upload_key, is_private=True, expires=fs_expires)
        upload_links.append(u'[%s](%s)' % (name, url))

    logger.info('sending notification')
    message = u'规划书用户信息已导出(共%s条), 链接%s内有效: %s' % (
        len(user_profiles), format_timedelta(fs_expires, locale='zh_CN'),
        u' '.join(upload_links))
    bearychat.say(message, skip_duplication=False)


if __name__ == '__main__':
    with create_app().app_context():
        main()
