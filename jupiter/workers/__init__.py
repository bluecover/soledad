# coding: utf-8

from __future__ import absolute_import

from envcfg.json.solar import BEANSTALKD_DSN

from jupiter.integration.mq import MessageQueuePool


pool = MessageQueuePool(BEANSTALKD_DSN)
