# coding:utf-8

from __future__ import absolute_import

import sys


def install_stub():
    from jupiter.stubs.sms_client import client

    sys.modules['sms_client.client'] = client
