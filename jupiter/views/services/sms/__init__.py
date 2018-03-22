# coding: utf-8

from urllib import unquote

import simplejson as json
from flask import request, abort

from libs.logger.rsyslog import rsyslog
from .._blueprint import create_blueprint


bp = create_blueprint('sms', __name__, url_prefix='/sms')


@bp.before_request
def check_income():
    ip = request.remote_addr
    _log('request remote_addr is %s' % ip)
    ips = ['223.4.50.111']
    if not ips or ip not in ips:
        _log('remote_addr %s is forbidden' % ip)
        abort(403)


@bp.route('/yunpian/callback', methods=['POST'])
def sms_status():
    reports = unquote(request.values.get('sms_status'))
    if not reports:
        return 'FAIL'
    results = json.loads(reports)

    items = ['mobile', 'sid', 'uid', 'user_receive_time',
             'error_msg', 'report_status']

    for result in results:
        r_keys = result.keys()
        contents = []
        for item in items:
            content = result[item] if item in r_keys else ''
            contents.append(str(content))

        _log('\t'.join(contents))
    return 'SUCCESS'


def _log(report):
    rsyslog.send(report, tag='sms_report')
