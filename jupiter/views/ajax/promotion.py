# coding: utf-8

from __future__ import absolute_import

from flask import jsonify
from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired

from jupiter.integration.wtforms import validators
from core.models.user.account import Account
from core.models.promotion.festival.christmas import ChristmasGift, GiftAwaredError
from .blueprint import create_blueprint, ValidationMixin


bp = create_blueprint('promotion', __name__, url_prefix='/j/promotion')


@bp.route('/christmas/2015', methods=['POST'])
def christmas_gift():
    form = GameResultForm()
    form.raise_for_validation()
    mobile = form.mobile_phone.data

    try:
        gift = ChristmasGift.add(mobile, form.rank.data)
    except GiftAwaredError as e:
        return jsonify(error=unicode(e)), 405

    user = Account.get_by_alias(mobile)
    if user and user.is_normal_account():
        # 手机号对应用户是激活用户则直接派发礼包，否则等待用户注册触发
        gift.award()
    return '', 204


class GameResultForm(Form, ValidationMixin):
    mobile_phone = StringField(
        validators=[DataRequired(), validators.MobilePhone()])
    rank = SelectField(
        choices=[(r, r.name) for r in ChristmasGift.Rank],
        coerce=lambda x: ChristmasGift.Rank(int(x)))
