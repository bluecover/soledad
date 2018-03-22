# coding: utf-8

from itertools import chain

from flask import Blueprint, abort, g, jsonify
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError

from core.models import errors
from core.models.utils.validator import validate_identity, validate_han
from core.models.profile.identity import Identity, IdentityBindingError
from core.models.hoard.zhiwang.transaction import register_zhiwang_account
from core.models.hoard.zhiwang import ZhiwangAccount
from core.models.hoard.xinmi.transaction import register_xm_account
from core.models.hoard.xinmi import XMAccount
from core.models.hoard.xinmi.errors import (
    MismatchUserError, RepeatlyRegisterError)

bp = Blueprint('jauth', __name__, url_prefix='/j/auth')


@bp.before_request
def check_for_login():
    if not g.user:
        abort(401)


@bp.route('/identity', methods=['POST'])
def identity():
    form = IdentityForm()
    if Identity.get(g.user.id_):
        return jsonify(r=False, error='您已经绑定了身份信息，无需再次绑定')
    if not form.validate():
        return jsonify(r=False, error=u','.join(chain(*form.errors.values())))
    try:
        Identity.save(
            user_id=g.user.id_,
            person_name=form.data['person_name'],
            person_ricn=form.data['person_ricn'])
    except IdentityBindingError as e:
        return jsonify(r=False, error=unicode(e))
    else:
        return jsonify(r=True)


@bp.route('/channel/savings/c01', methods=['POST'])
def channel_yixin():
    abort(410)


@bp.route('/channel/savings/c02', methods=['POST'])
def channel_zhiwang():
    if ZhiwangAccount.get_by_local(g.user.id_):
        return jsonify(r=True)
    try:
        register_zhiwang_account(g.user.id_)
    except MismatchUserError as e:
        return jsonify(r=False, error=e.args[0])
    except RepeatlyRegisterError as e:
        return jsonify(r=False, error=e.args[0])
    else:
        return jsonify(r=True), 201


@bp.route('/channel/savings/xm', methods=['POST'])
def channel_xm():
    if XMAccount.get_by_local(g.user.id_):
        return jsonify(r=True)
    try:
        register_xm_account(g.user.id_)
    except MismatchUserError as e:
        return jsonify(r=False, error=e.args[0])
    except RepeatlyRegisterError as e:
        return jsonify(r=False, error=e.args[0])
    else:
        return jsonify(r=True), 201


class IdentityForm(Form):
    person_name = StringField('person_name', validators=[DataRequired()])
    person_ricn = StringField('person_ricn', validators=[DataRequired()])

    def validate_person_ricn(self, field):
        error = validate_identity(field.data)
        if error != errors.err_ok:
            raise ValidationError(u'无效的身份证号')

    def validate_person_name(self, field):
        error = validate_han(field.data, 2, 20)
        if error != errors.err_ok:
            raise ValidationError(u'无效的姓名')
