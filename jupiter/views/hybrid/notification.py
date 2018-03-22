# coding:utf-8

from __future__ import absolute_import

from flask import g
from flask_mako import render_template

from jupiter.utils.hybrid import hybrid_view
from core.models.notification import Notification
from core.models.site.bulletin import Bulletin
from .blueprint import create_blueprint


bp = create_blueprint(
    'notification', __name__, url_prefix='/hybrid/notification')


@bp.route('/app', methods=['GET'])
@hybrid_view(['user_info'])
def notification():
    notices = Notification.get_multi_by_user(g.user.id_)
    origin_bulletins = Bulletin.get_multi()
    bulletins = sorted(origin_bulletins, key=lambda x: x.creation_time, reverse=True)

    # 当用户打开通知页面则默认全部消息为已读
    unreads = Notification.get_multi_unreads_by_user(g.user.id_)
    for u in unreads:
        u.mark_as_read()
    return render_template('notification/index.html', notices=notices, bulletins=bulletins[:1])


@bp.route('/announcement', methods=['GET'])
@hybrid_view(['user_info'])
def announcement():
    return render_template('notification/announcement.html')
