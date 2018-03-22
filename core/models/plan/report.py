# -*- coding: utf-8 -*-

import os
from operator import attrgetter
from warnings import warn
from datetime import datetime

from MySQLdb import IntegrityError
from envcfg.json.solar import DEBUG

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models import errors
from core.models.mixin.props import SecretPropsMixin
from core.models.utils import randbytes2, datetime_2_str
from .plan import Plan
from .consts import REPORT_STATUS, FORMULA_VER, FORMULA_DIR, REPORT_DIR
from .calculator import Calculator, InvalidFormulaKeyError
from .property import RAW_DATA


_REPORT_CACHE_PREFIX = 'report:'

REPORT_CACHE_KEY = _REPORT_CACHE_PREFIX + '%s'
REPORT_BY_NAME_CACHE_KEY = _REPORT_CACHE_PREFIX + 'name:%s'
REPORT_PLAN_IDS_CACHE_KEY = _REPORT_CACHE_PREFIX + 'plan:ids:%s'


class Report(SecretPropsMixin):

    def __init__(self, id, confuse_name, plan_id, rev, formula_ver, status,
                 create_time, update_time):
        self.id = str(id)
        self.confuse_name = confuse_name
        self.plan_id = str(plan_id)
        self.rev = rev
        self.formula_ver = formula_ver
        self.status = str(status)
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Report id=%s, plan_id=%s, rev=%s>' % (
            self.id, self.plan_id, self.rev)

    def get_uuid(self):
        return 'report:secret:data:%s' % self.id

    def get_db(self):
        return 'report_data'

    @property
    def plan(self):
        return Plan.get(self.plan_id) if self.plan_id else None

    @property
    def raw_data(self):
        return self.plan.data.get_by_rev(self.rev) if self.plan else {}

    def get_inter_data(self):
        return self.data.intermeidate_data or {}

    def set_inter_data(self, dat):
        self.data.update(intermeidate_data=dat)

    inter_data = property(get_inter_data, set_inter_data)

    @classmethod
    def add(cls, plan_id, rev):
        if not plan_id or not rev:
            return False

        name = randbytes2(8)
        try:
            params = (name, plan_id, rev, FORMULA_VER, REPORT_STATUS.new,
                      datetime.now())
            id = db.execute('insert into user_report '
                            '(confuse_name, plan_id, rev, formula_ver, status,'
                            ' create_time) '
                            'values(%s, %s, %s, %s, %s, %s)',
                            params)
            if id:
                db.commit()
                mc.delete(REPORT_PLAN_IDS_CACHE_KEY % plan_id)
                return cls.get(id)
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert account failed')

    @classmethod
    @cache(REPORT_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, confuse_name, plan_id, rev, '
                        'formula_ver, status, create_time, update_time '
                        'from user_report where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(REPORT_BY_NAME_CACHE_KEY % '{confuse_name}')
    def get_by_name(cls, confuse_name):
        rs = db.execute('select id, confuse_name, plan_id, rev, '
                        'formula_ver, status, create_time, update_time '
                        'from user_report where confuse_name=%s',
                        (confuse_name,))
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(REPORT_PLAN_IDS_CACHE_KEY % '{plan_id}')
    def get_ids_by_plan(cls, plan_id):
        rs = db.execute('select id from user_report where plan_id=%s',
                        (plan_id,))
        return [str(id) for (id,) in rs] if rs else []

    @classmethod
    def gets_by_plan_id(cls, plan_id):
        ids = cls.get_ids_by_plan(plan_id)
        if ids:
            reports = [cls.get(id) for id in ids]
            return sorted(reports, key=attrgetter('create_time'), reverse=True)

    @classmethod
    def get_latest_by_plan_id(cls, plan_id):
        reports = cls.gets_by_plan_id(plan_id)
        if reports:
            return reports[0]

    @classmethod
    def gets_by_user_id(cls, user_id):
        plan = Plan.get_by_user_id(user_id)
        if plan:
            return cls.gets_by_plan_id(plan.id)

    def clear_cache(self):
        mc.delete(REPORT_CACHE_KEY % self.id)
        mc.delete(REPORT_BY_NAME_CACHE_KEY % self.confuse_name)
        mc.delete(REPORT_PLAN_IDS_CACHE_KEY % self.plan_id)

    def update_status(self, status):
        # TODO add log
        if status not in REPORT_STATUS.values():
            return False
        try:
            db.execute('update user_report set status=%s '
                       'where id=%s', (status, self.id))
            db.commit()
            self.clear_cache()
            self.status = status
            return Report.get(self.id)
        except:
            db.rollback()
            return False

    def update_formula_ver(self, formula_ver):
        if int(formula_ver) <= int(self.formula_ver):
            return False
        try:
            db.execute('update user_report set formula_ver=%s '
                       'where id=%s', (formula_ver, self.id))
            db.commit()
            self.clear_cache()
            self.formula_ver = formula_ver
            return Report.get(self.id)
        except:
            db.rollback()
            return False

    def _path(self):
        year = self.create_time.year
        month = self.create_time.month
        day = self.create_time.day
        return REPORT_DIR + '%s/%s/%s/' % (year, month, day)

    @property
    def html_path(self):
        path = self._path() + 'html/'
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def pdf_path(self):
        path = self._path() + 'pdf/'
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def abs_html_name(self):
        return self.html_path + self.confuse_name + '.html'

    @property
    def abs_pdf_name(self):
        return self.pdf_path + self.confuse_name + '.pdf'


def _log(report, msg):
    rsyslog.send(report.id + '\t' + msg, tag='report_generator')


def cal_intermediate_data(report, force=False, log=_log):
    '''
    生成规划书中间数据
    存储在inter_data中
    '''
    if not (report.rev and report.raw_data):
        # assert report.rev
        # assert report.raw_data
        log(report, 'error\tmissing raw data error')
        report.update_status(REPORT_STATUS.fail)
        return errors.err_inter_data_generate_error

    if report.inter_data and not DEBUG and not force:
        return report.inter_data

    plan_data = report.raw_data
    cal = Calculator.get_by_plan_data(plan_data)

    try:
        data = cal.execute(data_property=RAW_DATA, formula=FORMULA_DIR)
    except InvalidFormulaKeyError as e:
        log(report, 'error\t%s' % e)
        report.update_status(REPORT_STATUS.fail)
        raise

    # gen date
    gen_date = datetime.now()
    data['gen_date'] = datetime_2_str(gen_date)

    report.inter_data = data
    return errors.err_ok


def generate_report(report, force=False):
    """生成规划书"""

    _log(report, 'start')
    if not force and report.status != REPORT_STATUS.new:
        _log(report, 'error\treport status error')
        report.update_status(REPORT_STATUS.fail)
        return errors.err_report_status_error

    _log(report, 'inter_data generating')
    error = cal_intermediate_data(report, force=force)
    if error != errors.err_ok:
        return error

    report = report.update_status(REPORT_STATUS.interdata)
    _log(report, 'inter_data generated')

    incr_user_count()

    return errors.err_ok


USER_COUNT_MC_KEY = '__user_count_total__'


def get_user_count():
    def _get_count():
        try:
            r = mc.get(USER_COUNT_MC_KEY)
            if r:
                r = int(r)
                return r
        except:
            return 0
    count = _get_count()
    return count if count else 25038


def incr_user_count():
    mc.set(USER_COUNT_MC_KEY, get_user_count()+1)
