#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
宜定盈产品信息更新
"""

from jupiter.app import create_app
from jupiter.ext import yixin
from core.models.hoard import YixinService
from libs.logger.rsyslog import rsyslog


app = create_app()


def main():
    """Downloads the product data of Yixin."""
    with app.app_context():
        response = yixin.query.p2p_service_list()
    for service_info in response.data:
        service = YixinService.add(service_info)
        rsyslog.send(service.uuid.hex, tag='yixin_updating_services')

if __name__ == '__main__':
    main()
