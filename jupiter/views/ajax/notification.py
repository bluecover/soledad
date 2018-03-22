# coding: utf-8

from flask import jsonify, g, Blueprint, abort

from core.models.notification import Notification
from core.models.notification.kind import (
    spring_gift_reserved_notification, spring_gift_obtained_notification,
    welfare_gift_notification)

bp = Blueprint('jnotification', __name__, url_prefix='/j/notification')


@bp.route('/get_all', methods=['GET'])
def get_all_notifications():
    if not g.user:
        abort(401)

    all_unreads = Notification.get_multi_unreads_by_user(g.user.id_)
    welfare_unreads = []
    spring_reserved_unreads = []
    spring_obtained_unreads = []

    for notice in all_unreads:
        if notice.kind is welfare_gift_notification:
            welfare_unreads.append(notice)
        elif notice.kind is spring_gift_reserved_notification:
            spring_reserved_unreads.append(notice)
        elif notice.kind is spring_gift_obtained_notification:
            spring_obtained_unreads.append(notice)

    targets = spring_obtained_unreads or spring_reserved_unreads or welfare_unreads
    if not targets:
        return jsonify(template=None)

    template = Notification.get_merged_popout_template(targets)
    # simply mark all unreads read once here requested
    for t in all_unreads:
        t.mark_as_read()
    return jsonify(template=template)
