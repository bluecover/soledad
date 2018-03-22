# -*- coding: utf-8 -*-


"""
保险产品更新
"""

import csv
import os

from core.models.product.insure import Insure


def clear_insurance():
    for ins in Insure.get_all():
        ins.delete()


def add_insurance(path):
    with open(path, 'r') as f:
        skip = True
        for d in csv.DictReader(f):
            if skip:
                skip = False
                continue
            id = Insure.add(d.pop('type'), d.pop('rec_rank', '5'))
            ins = Insure.get(id)
            ins.update_props_items(d)


if __name__ == '__main__':
    clear_insurance()
    path = os.path.join(os.path.dirname(__file__), 'insure.csv')
    add_insurance(path)
