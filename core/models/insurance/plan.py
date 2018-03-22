# -*- coding: utf-8 -*-
from datetime import datetime

from libs.db.store import db
from core.models.mixin.props import SecretPropsMixin


_PLAN_CACHE_PREFIX = 'ins:plan:'
PLAN_CACHE_KEY = _PLAN_CACHE_PREFIX + '%s'
PLAN_USER_CACHE_KEY = _PLAN_CACHE_PREFIX + 'user:%s'


class Plan(SecretPropsMixin):

    def __init__(self, id, user_id, create_time, update_time):
        self.id = str(id)
        self.user_id = str(user_id)
        self.create_time = create_time
        self.update_time = update_time

    def __repr__(self):
        return '<Plan id=%s, user_id=%s>' % (self.id, self.user_id)

    def get_uuid(self):
        return 'ins:plan:secret:data:%s' % self.id

    def get_db(self):
        return 'ins_plan_data'

    @classmethod
    def get(cls, plan_id):
        rs = db.execute('select id, user_id, '
                        'create_time, update_time '
                        'from insurance_plan where id=%s', (plan_id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def get_by_user_id(cls, user_id):
        rs = db.execute('select id, user_id, '
                        'create_time, update_time '
                        'from insurance_plan where user_id=%s', (user_id,))
        return [cls(*r) for r in rs] if rs else None

    @classmethod
    def add(cls, user_id):
        id_ = db.execute('insert into insurance_plan '
                         '(user_id, create_time) '
                         'values (%s, %s)',
                         (user_id, datetime.now()))
        if id_:
            db.commit()
            return cls.get(id_)
        else:
            db.rollback()

    def remove(self):
        db.execute('delete from insurance_plan where id=%s', (self.id,))
        db.commit()
        if self._secret_db.couchdb.get(self._props_db_key, self._props_name):
            self._secret_db.couchdb.delete(self._props_db_key, self._props_name)

    def update_plan(self, data, href):
        plan_keys = data.keys()
        non_int_keys = ['gender', 'marriage', 'owner', 'resident', 'has_social_security',
                        'has_complementary_medicine', 'family_duty', 'older_duty', 'spouse_duty',
                        'child_duty', 'loan_duty', 'annual_premium']
        int_keys = ['age', 'annual_revenue_family', 'annual_revenue_personal',
                    'asset', 'accident_coverage', 'ci_coverage',
                    'ci_coverage_with_social_security', 'ci_period', 'ins_premium_least',
                    'ins_premium_up', 'life_coverage', 'life_period']
        update_dict = {'id': self.id}
        for key in plan_keys:
            if key in non_int_keys:
                update_dict[key] = data.get(key, '')
            if key in int_keys:
                update_dict[key] = int_or_none(data.get(key))
        if 'is_completed' in plan_keys:
            update_dict['is_completed'] = True
            update_dict['href'] = href
        self.data.update(**update_dict)

    @classmethod
    def get_user_plan_dict(cls, user_id):
        planners = cls.get_by_user_id(user_id)
        if planners:
            return sorted([to_unicode(p.data.data) for p in planners],
                          key=plan_key_fun, reverse=True)
        else:
            return {}

    @classmethod
    def get_user_plan_by_id(cls, plan_id):
        plan = Plan.get(plan_id)
        return to_unicode(plan.data.data)

    @classmethod
    def belong_to_user(cls, plan_id, user_id):
        plan_dict = cls.get_user_plan_dict(user_id)
        if not plan_dict:
            return False
        plan_ids = [p['id'] for p in plan_dict]
        if plan_id not in plan_ids:
            return False
        return True


def int_or_none(x):
    return int(x) if x else ''


def to_unicode(data):
    r = {}
    for x in data.keys():
        if data[x] and isinstance(data[x], str):
            r[x] = data[x].decode('utf-8')
        else:
            r[x] = data[x]
    return r


def plan_key_fun(plan):
    score = 0
    if plan.get('is_completed'):
        score += 100
    if plan.get('owner') and plan.get('owner') == u'自己':
        score += 10
    else:
        score += 5
    return score
