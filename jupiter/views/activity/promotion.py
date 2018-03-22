# coding: utf-8

from flask import jsonify, request, url_for, Blueprint
from flask_mako import render_template

from core.models.user.account import Account


bp = Blueprint('activity.promotion', __name__, url_prefix='/activity/promotion')


@bp.route('/travel')
def travel():
    return render_template('activity/promotion/travel.html')


@bp.route('/taxi')
def taxi():
    return render_template('activity/promotion/taxi.html')


@bp.route('/meal')
def meal():
    return render_template('activity/promotion/meal.html')


@bp.route('/sangongzi')
def sangongzi():
    download_url = url_for('download.download_app')

    return render_template('activity/promotion/sangongzi.html', download_url=download_url)


@bp.route('/is_new_user', methods=['POST'])
def check_for_new_user():
    mobile = request.form.get('mobile')
    if mobile:
        user = Account.get_by_alias(mobile)
        is_new_user = False if user else True
        return jsonify(is_new_user=is_new_user)
