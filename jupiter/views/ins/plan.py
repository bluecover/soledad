# -*- coding: utf-8 -*-
import json
import uuid
import math


from flask import Blueprint, request, g, redirect, jsonify, session, url_for, abort
from flask_mako import render_template

from core.models.insurance.plan import Plan
from libs.logger.rsyslog import rsyslog

RESIDENT_INS_COVERAGE = {
  u'北上深': 30,
  u'一二线城市': 20,
  u'其他地级市': 10,
  u'县市、城镇': 10
}

DUTY_MAP = {
    'a': 10,
    'b': 30,
    'c': 70,
    'd': 100,
    'null': 0
}

bp = Blueprint('ins.plan', __name__)


@bp.route('/ins/plan/')
def index():
    if not g.user:
        if not session.get('uuid'):
            session['uuid'] = str(uuid.uuid4())
        if not session.get('ins_plan_index_log'):
            rsyslog.send(session['uuid']+'\t'+request.remote_addr, tag='ins_plan_index')
            session['ins_plan_index_log'] = 'logged'
        return render_template('ins/plan.html')
    else:
        user_id = g.user.id
        if session.get('ins_plan'):
            register_log = format_plan(session['ins_plan'], is_regiester='yes', user_id=user_id)
            register_log = session['uuid'] + '\t' + register_log
            rsyslog.send(register_log, tag='ins_plan')
            update_session_to_plan(user_id, session.get('ins_plan'))
        if Plan.get_user_plan_dict(user_id):
            planners_dict = Plan.get_user_plan_dict(user_id)
            return render_template('ins/plan_management.html', planners=planners_dict)
        return render_template('ins/plan.html')


@bp.route('/ins/plan/planning/<plan_id>')
def planning(plan_id):
    if g.user:
        if Plan.belong_to_user(plan_id, g.user.id):
            return render_template('ins/plan_planning.html', **Plan.get_user_plan_by_id(plan_id))
        else:
            return redirect(url_for('ins.plan.index'))


@bp.route('/ins/plan/consulting/', methods=['GET'])
def consulting():
    if not g.user:
        if not session.get('uuid'):
            session['uuid'] = str(uuid.uuid4())
        if not session.get('ins_plan_consulting_log'):
            rsyslog.send(session['uuid']+'\t'+request.remote_addr, tag='ins_plan_consulting')
            session['ins_plan_consulting_log'] = 'logged'
        session_dict = {}
        if session.get('ins_plan'):
            session_dict = json.loads(session.get('ins_plan'))
        session_dict['is_login'] = False
        return render_template('ins/plan_consulting.html',
                               plan=json.dumps(session_dict))
    else:
        user_id = g.user.id
        plan_id = request.args.get('plan_id')
        if not plan_id and not Plan.get_user_plan_dict(user_id):
            return render_template('ins/plan_consulting.html', plan=session.get('ins_plan', '{}'))
        if plan_id and Plan.belong_to_user(plan_id, g.user.id):
            plan_dict = Plan.get(plan_id).data.data
            plan_json_str = session.get('login_ins_plan'+str(plan_id))
            if plan_json_str:
                session_plan = json.loads(plan_json_str)
                plan_dict.update(session_plan)
            plan_dict['is_login'] = True
            plan_json = json.dumps(plan_dict)
            session['plan_id'] = plan_id
            return render_template('ins/plan_consulting.html', plan=plan_json)
        return redirect(url_for('ins.plan.index'))


@bp.route('/j/ins/plan/add_planning', methods=['POST'])
def add_plan():
    request_dict = request.form.to_dict()
    stage = None
    if request_dict.get('stage', None):
        stage = int(request_dict.get('stage', None))
    request_dict.pop('stage', None)

    if not g.user:
        if not session.get('uuid'):
            session['uuid'] = str(uuid.uuid4())
        if not session.get('ins_plan'):
            session['ins_plan'] = json.dumps(request_dict)
            return_dict = {}
        else:
            origin_plan = json.loads(session.get('ins_plan'))
            updated_plan, return_dict = update_plan_with_stage(request_dict, stage, origin_plan)
            origin_plan.update(updated_plan)
            session['ins_plan'] = json.dumps(origin_plan)
        rsyslog.send(session['uuid']+'\t'+format_plan(session['ins_plan']), tag='ins_plan')
        return jsonify(**return_dict), 200

    else:
        user_id = g.user.id
        plan_id = session.get('plan_id')
        if len(Plan.get_user_plan_dict(user_id)) > 2:
            abort(401)
        if request_dict.keys() == ['owner']:
            if len(Plan.get_user_plan_dict(user_id)) == 1:
                return add_mate_plan(user_id, request_dict.get('owner'))
            else:
                abort(401)
        if plan_id:
            return update_login_plan(user_id, request_dict, plan_id, stage)
        else:
            if not Plan.get_user_plan_dict(user_id):
                plan = add_login_plan(user_id, request_dict)
                session['plan_id'] = plan.id
                return jsonify(islogin=True), 200
            else:
                abort(401)


@bp.route('/j/ins/plan/delete_planning', methods=['POST'])
def delete_plan():
    if not g.user:
        return jsonify(is_login=False, error='not login'), 400
    plan = Plan.get(request.form.get('id'))
    if plan and Plan.belong_to_user(plan.id, g.user.id):
        plan.remove()
        session.pop('login_ins_plan'+str(plan.id), None)
        return jsonify(is_login=True), 200
    else:
        abort(401)


def update_plan_with_stage(form_dict, stage, origin_plan):
    updated_plan = {}
    return_dict = {}
    if stage == 0:
        owner = form_dict.get('owner', None)
        gender = form_dict.get('gender', None)
        marriage = form_dict.get('marriage', None)
        updated_plan['gender'] = gender
        if owner:
            updated_plan['owner'] = owner
        if marriage:
            updated_plan['marriage'] = marriage

    elif stage == 1:
        age = int(form_dict.get('age'))
        updated_plan['age'] = age
        return_dict['ci_period'] = updated_plan['ci_period'] = 20 if age > 35 else 30

    elif stage == 2:
        annual_revenue_personal = form_dict.get('annual_revenue_personal')
        annual_revenue_family = form_dict.get('annual_revenue_family', None)
        annual_revenue_personal = int(annual_revenue_personal)
        if annual_revenue_family:
            annual_revenue_family = int(annual_revenue_family)
        resident = form_dict.get('resident')
        accident_coverage = RESIDENT_INS_COVERAGE.get(resident, 10)
        updated_plan['annual_revenue_personal'] = annual_revenue_personal
        updated_plan['annual_revenue_family'] = annual_revenue_family
        updated_plan['resident'] = resident
        updated_plan['accident_coverage'] = accident_coverage
        return_dict['accident_coverage'] = accident_coverage

    elif stage == 3:
        has_social_security = form_dict.get('has_social_security')
        has_complementary_medicine = form_dict.get('has_complementary_medicine')
        annual_revenue_personal = origin_plan.get('annual_revenue_personal')
        age = origin_plan.get('age')
        ci_period = 20 if age > 35 else 30
        ci_coverage = compute_ci_coverage(has_social_security, has_complementary_medicine,
                                          annual_revenue_personal)
        ci_coverage_with_social_security = compute_ci_coverage(annual_revenue_personal, u'有',
                                                               has_complementary_medicine)
        updated_plan['has_social_security'] = has_social_security
        updated_plan['has_complementary_medicine'] = has_complementary_medicine
        updated_plan['ci_period'] = ci_period
        updated_plan['ci_coverage'] = ci_coverage
        updated_plan['ci_coverage_with_social_security'] = ci_coverage_with_social_security
        return_dict['ci_period'] = ci_period
        return_dict['ci_coverage'] = ci_coverage
        return_dict['ci_coverage_with_social_security'] = ci_coverage_with_social_security

    elif stage == 4:
        updated_plan['family_duty'] = json.loads(form_dict['family_duty'])
        marriage = origin_plan.get('marriage')
        annual_revenue_personal = origin_plan.get('annual_revenue_personal')
        annual_revenue_family = origin_plan.get('annual_revenue_family', None)
        revenue = annual_revenue_family if marriage == u'已婚' else annual_revenue_personal
        least_ratio = 0.05
        up_ratio = 0.07
        ins_premium_least = int(math.floor(revenue * least_ratio * 10000))
        ins_premium_up = int(math.floor(revenue * up_ratio * 10000))
        updated_plan['ins_premium_least'] = ins_premium_least
        updated_plan['ins_premium_up'] = ins_premium_up
        return_dict['ins_premium_least'] = ins_premium_least
        return_dict['ins_premium_up'] = ins_premium_up

    elif stage == 5:
        older_duty = form_dict.get('older_duty', 'null')
        spouse_duty = form_dict.get('spouse_duty', 'null')
        child_duty = form_dict.get('child_duty', 'null')
        loan_duty = form_dict.get('loan_duty', 'null')
        asset = int(form_dict.get('asset', 0))
        duty_total = sum([DUTY_MAP[x] for x in [older_duty, spouse_duty, child_duty, loan_duty]])
        life_coverage = duty_total - asset
        life_period = 60 - origin_plan.get('age')
        life_period = life_period/10 * 10
        life_period = 30 if life_period >= 25 else life_period
        if older_duty != 'null':
            updated_plan['older_duty'] = older_duty
        if spouse_duty != 'null':
            updated_plan['spouse_duty'] = spouse_duty
        if child_duty != 'null':
            updated_plan['child_duty'] = child_duty
        if loan_duty != 'null':
            updated_plan['loan_duty'] = loan_duty
        updated_plan['asset'] = asset
        updated_plan['life_coverage'] = life_coverage
        updated_plan['life_period'] = life_period
        return_dict['life_coverage'] = life_coverage
        return_dict['life_period'] = life_period

    elif stage == 6:
        if origin_plan.get('life_coverage', None) is None:
            updated_plan['life_coverage'] = ''
        annual_premium = form_dict.get('annual_premium')
        updated_plan['annual_premium'] = annual_premium
        updated_plan['is_completed'] = True

    return updated_plan, return_dict


def add_myself(user_id, mate_gender):
    p = Plan.add(user_id)
    my_gender = u'男性' if mate_gender == u'女性' else u'女性'
    p.data.update(
        owner=u'自己',
        marrige=u'已婚',
        gender=my_gender,
        href=url_for('ins.plan.consulting', plan_id=p.id),
        is_completed=False,
        accident_coverage='',
        id=p.id
    )


def update_login_plan(user_id, request_dict, plan_id, stage):
    if Plan.belong_to_user(plan_id, user_id):
        plan = Plan.get(plan_id)
        session_plan_key = 'login_ins_plan'+str(plan_id)
        if not session.get(session_plan_key):
            session[session_plan_key] = json.dumps(request_dict)
            plan.data.update(**request_dict)
            return_dict = {}
        else:
            origin_plan = Plan.get_user_plan_by_id(plan_id)
            updated_plan, return_dict = update_plan_with_stage(request_dict, stage, origin_plan)
            origin_plan.update(updated_plan)
            session[session_plan_key] = json.dumps(origin_plan)
            plan.data.update(**updated_plan)
            if stage == 6:
                plan.data.update(is_completed=True)
                plan.data.update(href=url_for('ins.plan.planning', plan_id=plan.id))
                session.pop(session_plan_key, None)
                session.pop('plan_id', None)
        return jsonify(**return_dict), 200
    return abort(401)


def update_session(session_str, request_dict):
    session_dict = json.loads(session_str)
    session_dict.update(request_dict)
    return json.dumps(session_dict)


def add_login_plan(user_id, request_dict):
    plan = Plan.add(user_id)
    plan.data.update(
        href=url_for('ins.plan.consulting', plan_id=plan.id),
        is_completed=False
    )
    plan.update_plan(request_dict, url_for('ins.plan.planning', plan_id=plan.id))
    session['plan_id'] = plan.id
    if len(Plan.get_user_plan_dict(g.user.id)) == 1 and \
            plan.data.owner.decode('utf-8') == u'配偶':
        add_myself(g.user.id, plan.data.gender.decode('utf-8'))
    return plan


def update_session_to_plan(user_id, session_str):
    if Plan.get_user_plan_dict(user_id):
        session.pop('ins_plan', None)
        # session.pop('uuid', None)
        return
    session_dict = json.loads(session_str)
    plan = Plan.add(user_id)
    plan.data.update(
        is_completed=False,
        href=url_for('ins.plan.consulting', plan_id=plan.id)
    )
    plan.update_plan(session_dict, url_for('ins.plan.planning', plan_id=plan.id))
    session.pop('ins_plan', None)
    # session.pop('uuid', None)
    if session_dict.get('owner') and session_dict.get('owner') == u'配偶':
        add_myself(user_id, session_dict.get('gender'))


def add_mate_plan(user_id, owner):
    plan_dict = Plan.get_user_plan_dict(user_id)
    plan = Plan.add(g.user.id)
    plan.data.update(
        is_completed=False,
        href=url_for('ins.plan.consulting', plan_id=plan.id),
        id=plan.id,
        marriage=u'已婚',
        gender=u'男性' if plan_dict[0]['gender'] == u'女性' else u'女性',
        owner=owner,
    )
    return jsonify(is_login=True, id=plan.id, href=plan.data.href,
                   is_completed=plan.data.is_completed,
                   gender=plan.data.gender), 200


def compute_ci_coverage(has_social_security, has_complementary_medicine, annual_revenue_personal):

    if annual_revenue_personal <= 4:
        ci_coverage = 20 if has_social_security == u'无' else 10
    elif annual_revenue_personal < 20:
        if has_social_security == u'无':
            ci_coverage = 30
        elif has_complementary_medicine == u'无':
            ci_coverage = 20
        else:
            ci_coverage = 10
    else:
        if has_social_security == u'无':
            ci_coverage = 40
        else:
            ci_coverage = 30 if has_complementary_medicine == u'无' else 20
    return ci_coverage


def get_bye_str(_item, _h):
    if _h == 'family_duty' and _item.get(_h, None):
        return ';'.join(str(x) for x in _item.get(_h))
    try:
        return str(_item.get(_h, ''))
    except UnicodeEncodeError:
        return _item.get(_h, '').encode('utf-8')
    finally:
        pass


def format_plan(json_str, is_regiester='no', user_id='no'):
    json_dict = json.loads(json_str)
    json_dict['is_register'] = is_regiester
    json_dict['user_id'] = user_id
    keys = ['gender', 'marriage', 'owner', 'age', 'annual_revenue_personal',
            'annual_revenue_family', 'resident', 'has_social_security',
            'has_complementary_medicine', 'family_duty', 'older_duty',
            'spouse_duty', 'child_duty', 'loan_duty', 'asset', 'annual_premium',
            'is_register', 'user_id']
    return ','.join([key + ': ' + get_bye_str(json_dict, key) for key in keys])
