# -*- coding: utf-8 -*-

from flask import session, request, jsonify, g, Blueprint
from core.models.wxplan.data import PlanData
from core.models.wxplan.formula import Formula
from core.models import errors

bp = Blueprint('wxplan', __name__, url_prefix='/j/plan')


@bp.route('/add', methods=['POST'])
def add():
    gender = request.form.get('info_gender', type=int)
    age = request.form.get('info_age', type=int)
    province = request.form.get('info_province')
    stock = request.form.get('info_stock', type=int)
    insurance = request.form.get('info_ins', type=int)
    travel = request.form.get('info_travel', type=int)
    children = request.form.get('info_children', type=int)
    monthly = request.form.get('info_monthly', type=int)
    rent = request.form.get('info_rent', type=int)
    income = request.form.get('info_income', type=int)
    savings = request.form.get('info_savings', type=int)
    plan = PlanData(id_=None, gender=gender, user_id=None, age=age, province_code=province,
                    stock=stock, rent=rent, mpayment=monthly, insurance=insurance, tour=travel,
                    has_children=children, savings=savings, mincome=income, create_time=None,
                    update_time=None)
    validator = Formula(plan=plan).validate()
    if validator['code'] == errors.err_ok:
        session['wxplan'] = plan.to_dict()
        if g.user:
            PlanData.add_or_update(gender=gender, user_id=g.user.id, age=age,
                                   province_code=province, stock=stock, rent=rent,
                                   mpayment=monthly, insurance=insurance, tour=travel,
                                   has_children=children, savings=savings, mincome=income)
        return jsonify(r=True)
    return jsonify(r=False, d=validator)
