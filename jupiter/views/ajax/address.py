# coding: utf-8

from itertools import chain
from gb2260 import Division

from flask import jsonify, g, Blueprint, request
from flask_wtf import Form

from wtforms import StringField
from wtforms.validators import DataRequired, ValidationError

from core.models import errors
from core.models.profile.address import Address
from core.models.utils.validator import validate_phone

bp = Blueprint('jaddress', __name__, url_prefix='/j/address')


@bp.route('/submit', methods=['POST'])
def submit_address():
    if not g.user:
        return jsonify(r=False), 401

    name = request.form.get('name')
    phone = request.form.get('phone')
    district = request.form.get('district', type=Division.search)
    street = request.form.get('street')
    infos = [district.code, street, name, phone]

    form = AddressForm()
    if not form.validate():
        return jsonify(r=False, error=u''.join(chain(*form.errors.values())))

    address = Address.get(request.form.get('address_id', None))
    if address:
        if address.user_id != g.user.id_:
            return jsonify(r=False, error=u'X﹏X')
        address.update(*infos)
    else:
        existent = Address.get_multi_by_user(g.user.id_)
        if existent:
            return jsonify(r=False, error=u'您已在其他页面绑定了地址，请刷新页面修改~')
        address = Address.add(g.user.id_, *infos)
    return jsonify(r=True, address_id=address.id_)


class AddressForm(Form):
    name = StringField('name', validators=[DataRequired()])
    phone = StringField('phone', validators=[DataRequired()])
    district = StringField('district', validators=[DataRequired()])
    street = StringField('street', validators=[DataRequired()])

    def validate_name(self, field):
        if not field.data:
            raise ValidationError(u'请输入姓名')

    def validate_phone(self, field):
        error = validate_phone(field.data)
        if error != errors.err_ok:
            raise ValidationError(u'无效的手机号')

    def validate_district(self, field):
        try:
            Division.search(field.data)
        except ValueError:
            raise ValidationError('地区不存在')

    def validate_street(self, field):
        if not field.data:
            raise ValidationError(u'请填写收货地址')
        if len(unicode(field.data)) > 80:
            raise ValueError(u'收货地址超过限制长度')
