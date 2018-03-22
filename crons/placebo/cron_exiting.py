#!/usr/bin/env python
# coding:utf-8

"""
    攒钱助手体验金转出处理
    ~~~~~~~~~~~~~~~~~~~~~~
"""

from jupiter.app import create_app
from jupiter.workers.hoard_placebo import placebo_order_exiting
from core.models.hoard.placebo import PlaceboOrder


app = create_app()


def main():
    for order, product in PlaceboOrder.iter_multi_for_exiting():
        placebo_order_exiting.produce(order.id_)


if __name__ == '__main__':
    main()
