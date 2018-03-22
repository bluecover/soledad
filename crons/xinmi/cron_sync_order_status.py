#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
指旺订单状态同步及资产补录
"""

from collections import Counter

from jupiter.app import create_app
from jupiter.ext import sentry
from jupiter.workers.hoard_xm import xm_payment_tracking
from libs.logger.rsyslog import rsyslog


app = create_app()
MAX_RETRY = 5


def main():
    tasks = [xm_payment_tracking]

    for task in tasks:
        mq = task.get_broker()
        counter = Counter()
        while True:
            job = mq.peek_buried()
            if not job:
                break

            info = {'body': job.body, 'task': task}
            if counter[job.body] >= MAX_RETRY:
                log = 'Job of tube is deleted'
                rsyslog.send(
                    '%s: %r' % (log, info), tag='cron_xm_sync_kick_ruined')
                sentry.captureMessage(log, extra=info)
                job.delete()
                continue
            mq.kick()
            rsyslog.send(
                'Kicking job %(body)s of tube %(task)s' % info,
                tag='cron_xm_sync_kick_history')
            counter[job.body] += 1

if __name__ == '__main__':
    main()
