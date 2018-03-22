# -*- coding: utf-8 -*-

from envcfg.json.solar import DEBUG

if DEBUG:
    from .webtest import *  # noqa
