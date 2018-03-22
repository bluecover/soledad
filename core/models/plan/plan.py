# -*- coding: utf-8 -*-

from datetime import datetime

from warnings import warn

from MySQLdb import IntegrityError

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from .data import PlanSecretDataMixin

_PLAN_CACHE_PREFIX = 'plan:'

PLAN_CACHE_KEY = _PLAN_CACHE_PREFIX + '%s'
PLAN_USER_CACHE_KEY = _PLAN_CACHE_PREFIX + 'user:%s'


class Plan(PlanSecretDataMixin):
    """
    用户的填写规划书的数据
    """

    def __init__(self, id, user_id, step, create_time, update_time):
        self.id = str(id)
        self.user_id = str(user_id)
        self.step = step
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Plan id=%s, user_id=%s>' % (self.id, self.user_id)

    @classmethod
    @cache(PLAN_CACHE_KEY % '{plan_id}')
    def get(cls, plan_id):
        rs = db.execute('select id, user_id, step, '
                        'create_time, update_time '
                        'from user_plan where id=%s', (plan_id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(PLAN_USER_CACHE_KEY % '{user_id}')
    def get_by_user_id(cls, user_id):
        rs = db.execute('select id, user_id, step, '
                        'create_time, update_time '
                        'from user_plan where user_id=%s', (user_id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def add(cls, user_id):
        try:
            id = db.execute('insert into user_plan '
                            '(user_id, create_time) '
                            'values (%s, %s)',
                            (user_id, datetime.now()))
            if id:
                db.commit()
                return cls.get(id)
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert user_plan failed')

    @property
    def user(self):
        from core.models.user.account import Account
        return Account.get(self.user_id)

    def update_step(self, step, force=False):
        if not isinstance(step, int):
            try:
                step = int(step)
            except:
                return False
        if step not in range(1, 6):
            return False
        if step > self.step or force:
            db.execute('update user_plan set step=%s where id=%s',
                       (step, self.id))
            db.commit()
            self.clear_cache()
            self.step = step

    def clear_cache(self):
        mc.delete(PLAN_CACHE_KEY % self.id)
        mc.delete(PLAN_USER_CACHE_KEY % self.user_id)

    def send_for_report(self):
        '''
        after all forms are post, report can be generate
        '''
        if self.step < 5:
            return False
        from .report import Report, generate_report
        rev = self.data.rev
        if not rev:
            return False
        report = Report.add(self.id, rev)
        if not report:
            return False

        generate_report(report)


def _log(report_id, msg):
    rsyslog.send(report_id + '\t' + msg, tag='report_buried_reborn')
