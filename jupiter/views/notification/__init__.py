# -*- coding: utf-8 -*-

from flask import Blueprint, redirect, url_for, g, request
from flask_mako import render_template

from core.models.notification import Notification

bp = Blueprint('notification', __name__, url_prefix='/notification')


@bp.route('/')
def index():
    if not g.user:
        return redirect(url_for('accounts.login.login', next=request.path))

    notices = Notification.get_multi_by_user(g.user.id_)

    # 当用户打开通知页面则默认全部消息为已读
    unreads = Notification.get_multi_unreads_by_user(g.user.id_)
    for u in unreads:
        u.mark_as_read()

    return render_template('notification/index.html', notices=notices)


@bp.route('/announcement', methods=['GET'])
def announcement():
    return render_template('notification/announcement.html')
