# -*- coding: utf-8 -*-

from datetime import datetime
from itertools import chain
from base64 import b64encode, b64decode
from flask import g, redirect, request, jsonify, url_for, session
from flask_mako import render_template
from flask_wtf import Form
from wtforms import StringField
from libs.logger.rsyslog import rsyslog
from wtforms.validators import DataRequired, ValidationError, AnyOf
from core.models.insurance.optpackage import (
    gen_result, get_result,
    get_total_ins_children_count,
    set_total_ins_children_count)
from core.models.insurance.profile import Profile
from core.models.insurance.activity61 import Activity61
from core.models.insurance.packages import Package
from ._blueprint import create_blueprint

bp = create_blueprint('children', __name__)


def redirect_login():
    return redirect(url_for('accounts.login.login', next=request.path))


def shared_url(account_id):
    return b64encode(g.user.id)


@bp.route('/share')
def share():
    cur_path = 'child_ins'

    if not g.user:
        return redirect_login()

    share_url = url_for('.index',
                        share_id=shared_url(g.user.id), _external=True)
    activity61 = Activity61.add(g.user.id) if g.user else ''
    count = len(activity61.recommend) if activity61 else 0

    return render_template('childins/activity61.html', **locals())


def shared(share_id):
    if not share_id:
        return None
    try:
        share = b64decode(share_id)
    except:
        share = None
    if share:
        tokens = session.setdefault('ins_child_61_tokens', {})
        tokens['shared_url'] = share_id
        session.modified = True
    return share


@bp.route('/', methods=['GET', 'POST'])
def index():
    cur_path = 'child_ins'

    count = get_total_ins_children_count()

    if request.method == 'POST':
        will_id = request.form.get('children')

        form = InsuranceWillForm()
        if not form.validate():
            return jsonify(
                r=False, errors=form.errors,
                error=u''.join(chain(*form.errors.values())))
        profile = Profile.add(g.user.id) if g.user else ''
        profile.user_will = will_id
        return redirect('/ins/children/info/1')

    profile = Profile.get(g.user.id) if g.user else None
    if profile and profile.result_data:
        return redirect('/ins/children/plan')
    share_id = shared(request.args.get('share_id', None))
    return render_template('childins/index.html', **locals())


@bp.route('/info/1', methods=['GET', 'POST'])
def program():
    cur_path = 'child_ins'

    profile = Profile.add(g.user.id) if g.user else ''
    if request.method == 'POST':
        will_id = request.form.get('childins_program')

        form = InsuranceWillForm()
        if not form.validate():
            return jsonify(
                r=False, errors=form.errors,
                error=u''.join(chain(*form.errors.values())))

        profile.user_will = will_id
        return redirect('/ins/children/info/2')

    if g.user:
        return render_template('childins/program.html', **locals())
    return redirect_login()


@bp.route('/info/2', methods=['GET', 'POST'])
def child():
    cur_path = 'child_ins'
    if not g.user:
        return redirect_login()

    profile = Profile.add(g.user.id)
    if profile.user_will == 0:
        return redirect('/ins/children/info/1')
    if request.method == 'POST':
        set_total_ins_children_count()
        form = InsuranceForm()
        if not form.validate():
            return jsonify(
                r=False, errors=form.errors,
                error=u''.join(chain(*form.errors.values())))

        profile.baby_birthday = datetime.strptime(form.birthdate.data, '%Y-%m-%d')
        profile.baby_gender = form.gender.data
        profile.child_medicare = form.child_medicare.data
        profile.childins_supplement = form.childins_supplement.data
        profile.child_genetic = form.child_genetic.data
        profile.child_edu = form.child_edu.data
        profile.project = form.project.data
        profile.result_data = {
            'children': form.data,
            'will': profile.user_will
        }

        gen_result(profile, force=True)

        # log
        msg = [g.user.id, str(profile.create_time), str(datetime.now())]
        rsyslog.send('\t'.join(msg), tag='children_insurance_plan_result')
        return redirect('/ins/children/plan')
    return render_template('childins/info.html', **locals())


def inc_recommend_number():
    tokens = session.get('ins_child_61_tokens', None)
    if not tokens:
        return
    shared_url = tokens.get('shared_url', None)

    share_id = None
    if shared_url:
        try:
            share_id = b64decode(shared_url)
        except:
            share_id = None

    if not share_id:
        return

    activity61 = Activity61.add(share_id)
    recommend = activity61.recommend
    if share_id and g.user.id != share_id and g.user.id not in recommend:
        recommend.append(g.user.id)

    activity61.recommend = recommend
    tokens['shared_url'] = None


@bp.route('/plan')
def result():
    if not g.user:
        return redirect_login()
    profile = Profile.add(g.user.id)
    if profile.user_will == 0:
        return redirect('/ins/children/info/1')
    cur_path = 'child_ins'
    if not profile.result_data:
        return redirect('/ins/children/info/1')

    inc_recommend_number()

    recommend_ins, backup_ins = get_result(profile)
    quota = recommend_ins[0].get('quota', 'quota') if recommend_ins else ''

    baby_birthday = profile.baby_birthday.strftime('%Y年%m月%d日')

    gender = u'男' if profile.baby_gender == '1' else u'女'

    rec_ability = (
        recommend_ins[0]['ability'] if recommend_ins is not None else ''
    )
    rec_total = sum([rec_ins['rate'] for rec_ins in recommend_ins])
    rec_package = Package.get(recommend_ins[0]['package_id'])
    rec_pack = rec_package[0]

    if backup_ins:
        backup_ability = (
            backup_ins[0]['ability'] if backup_ins else ''
        )
        backup_total = sum([backup['rate'] for backup in backup_ins])
        backup_package = Package.get(backup_ins[0]['package_id'])
        backup_pack = backup_package[0]

    # is_six_shown = profile.is_six
    # share_url = url_for('.index',
    #                     share_id=shared_url(g.user.id), _external=True)
    if not profile.is_six:
        profile.is_six = True
    return render_template('/childins/result.html', **locals())


class InsuranceWillForm(Form):
    childins_program = StringField(
        'childins_program',
        validators=[
            DataRequired(),
            AnyOf(['1', '2', '4', '5', ''], message=u'参数错误')])


class InsuranceForm(Form):
    birthdate = StringField('birthdate', validators=[DataRequired()])
    gender = StringField(
        'gender',
        validators=[
            DataRequired(),
            AnyOf(['0', '1'], message=u'性别参数错误')])
    child_medicare = StringField(
        'child_medicare',
        validators=[
            DataRequired(),
            AnyOf(['0', '1'], message=u'社保参数错误')])
    childins_supplement = StringField(
        'childins_supplement',
        validators=[
            DataRequired(),
            AnyOf(['0', '1'], message=u'补充医疗参数错误')])
    child_genetic = StringField(
        'child_genetic',
        validators=[
            DataRequired(),
            AnyOf(['0', '1'], message=u'遗传病史参数错误')])
    child_edu = StringField(
        'child_edu',
        validators=[
            DataRequired(),
            AnyOf(['0', '1'], message=u'教育金参数错误')])

    project = StringField(
        'project',
        validators=[
            AnyOf(['',
                   'a1', 'a2', 'a3',
                   'b1', 'b2', 'b3',
                   'c1', 'c2', 'c3'], message=u'教育金额度参数错误')])

    def validate_baby_birthday(self, field):
        try:
            datetime.strptime(field.data, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(u'日期格式错误')
