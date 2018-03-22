# coding: utf-8

from flask import Blueprint, abort, jsonify

from core.models.profile.division import get_division, get_children


bp = Blueprint('jdivision', __name__, url_prefix='/j/division')


@bp.route('/<int:year>/<int:province_id>/prefectures')
@bp.route('/<int:province_id>/prefectures', defaults={'year': None})
def prefectures(year, province_id):
    province = get_division(province_id, year)
    if province and province.is_province:
        return jsonify(data=get_children(province))
    abort(404)


@bp.route('/<int:year>/<int:prefecture_id>/counties')
@bp.route('/<int:prefecture_id>/counties', defaults={'year': None})
def counties(year, prefecture_id):
    prefecture = get_division(prefecture_id, year)
    if prefecture and prefecture.is_prefecture:
        counties = get_children(prefecture)
        if not counties:
            # 中国共有五个不设市辖区的地级市
            # 分别是东莞市、中山市、三沙市、儋州市、嘉峪关市
            counties = [
                {'code': prefecture.code, 'name': prefecture.name,
                 'revision': prefecture.year}]
        return jsonify(data=counties)
    abort(404)
