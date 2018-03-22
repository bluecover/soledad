# -*- coding: utf-8 -*-

from libs.logger.rsyslog import rsyslog


def log_register_source(uid, request):
    dcm = request.args.get('dcm', request.cookies.get('dcm', '0'))
    dcs = request.args.get('dcs', request.cookies.get('dcs', '0'))
    referer = request.args.get('refer', request.referrer)
    ip = request.remote_addr
    bid = request.bid
    msg = '\t'.join([uid, dcm, dcs, str(referer), ip, bid])
    rsyslog.send(msg, tag='register_logger')
