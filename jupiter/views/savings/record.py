# coding: utf-8

from flask import g, redirect, request, url_for
from flask_mako import render_template

from core.models.hoard import HoardProfile
from core.models.hoard.zhiwang import ZhiwangProfile

from ._blueprint import create_blueprint


bp = create_blueprint('record', __name__, url_prefix='/record')


@bp.route('/')
def record():
    cur_path = 'record'
    yx_profile = HoardProfile.add(g.user.id_)
    zw_profile = ZhiwangProfile.add(g.user.id_)

    if not yx_profile and not zw_profile:
        return redirect(url_for('savings.landing.index'))

    filtered = bool(request.args.get('filter'))
    yx_orders = yx_profile.orders(filter_due=filtered)
    zw_mixins = zw_profile.mixins(filter_due=filtered)

    records = yx_orders + zw_mixins
    records = sorted(records, key=lambda x: x[0].creation_time, reverse=True)
    return render_template(
        'savings/record.html', records=records, filter_due=filtered,
        cur_path=cur_path)
