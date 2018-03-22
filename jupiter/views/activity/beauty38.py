# coding: utf-8

from flask import Blueprint, request, redirect, url_for, abort
from flask_mako import render_template
from flask_wtf import Form
from wtforms.fields import StringField
from sms_client.provider import YIMEI_AD

from core.models.user.account import Account
from core.models.sms.sms import ShortMessage
from core.models.sms.kind import women_day_2016_register_sms
from jupiter.integration.wtforms.validators import MobilePhone

bp = Blueprint('activity.beauty38', __name__, url_prefix='/activity')


@bp.route('/2016/beauty38/', methods=['GET', 'POST'])
def index():
    form = ReserveForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            mobile = form.data['mobile']
            user = Account.get_by_alias(mobile)
            if user:
                return redirect(url_for('.login', mobile=mobile))
            else:
                sms = ShortMessage.create(mobile, women_day_2016_register_sms)
                sms.send(provider=YIMEI_AD)
                return redirect(url_for('.register', mobile=mobile))
    return render_template('activity/beauty38/index.html')


@bp.route('/2016/beauty38/register', methods=['GET'])
def register():
    mobile = request.args.get('mobile', None)
    if not mobile:
        abort(403)
    return render_template('activity/beauty38/register.html', mobile=mobile)


@bp.route('/2016/beauty38/login', methods=['GET'])
def login():
    mobile = request.args.get('mobile', None)
    if not mobile:
        abort(403)
    return render_template('activity/beauty38/login.html', mobile=mobile)


class ReserveForm(Form):
    mobile = StringField(u'手机号', validators=[MobilePhone()])
