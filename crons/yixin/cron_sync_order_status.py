#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
宜定盈订单状态同步
"""

from collections import Counter

from jupiter.app import create_app
from jupiter.ext import sentry
from jupiter.workers.hoard_yrd import (
    hoard_yrd_payment_tracking, hoard_yrd_confirming,
    hoard_yrd_exiting_checker)
from libs.logger.rsyslog import rsyslog


app = create_app()
MAX_RETRY = 5


def main():
    tasks = [hoard_yrd_payment_tracking, hoard_yrd_confirming,
             hoard_yrd_exiting_checker]

    for task in tasks:
        mq = task.get_broker()
        counter = Counter()
        while True:
            job = mq.peek_buried()
            if not job:
                break

            info = {'body':  job.body, 'task':  task}
            if counter[job.body] >= MAX_RETRY:
                log = 'Job of tube is deleted'
                rsyslog.send('%s: %r' % (log, info), tag='cron_yixin_sync_kick_ruined')
                sentry.captureMessage(log, extra=info)
                job.delete()
                continue
            mq.kick()
            rsyslog.send(
                'Kicking job %(body)s of tube %(task)s' % info, tag='cron_yixin_sync_kick_history')
            counter[job.body] += 1


if __name__ == '__main__':
    main()
