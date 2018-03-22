# coding: utf-8

from flask import request, redirect, Blueprint, g, abort
from werkzeug.urls import url_parse
from solar.utils.aes import decode

from libs.utils.link import is_guihua_url, make_valid_url
from libs.logger.rsyslog import rsyslog

bp = Blueprint('link', __name__)


@bp.route('/link')
def link():
    if not len(request.args.keys()) == 1:
        return redirect('/')
    ref = request.args.get('ref', type=decode)
    if not ref:
        abort(404)

    url = make_valid_url(ref)

    try:
        url_parse(url)
    except ValueError:
        abort(404)

    send_link_log(url=ref, referrer=request.referrer)

    if is_guihua_url(url):
        return redirect(url)
    # TODO: Could add some check here

    return redirect(url)


def send_link_log(url, referrer):
    user_id = g.user.id if g.user else 0
    agent_type = 'mobile' if request.user_agent.is_mobile else 'pc'
    rsyslog.send('%s\t%s\t%s\t"%s"' % (user_id, url, agent_type, referrer or '-'), tag='link')
