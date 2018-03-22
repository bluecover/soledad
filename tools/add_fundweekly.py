#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
添加基金周报
"""

import sys
import getopt

from libs.logger.rsyslog import rsyslog
from core.models.article.fundweekly import FundWeekly


def get_content_of_file(mdfile):
    txt = ''
    f = open(mdfile, 'r')
    while True:
        line = f.readline()
        if line:
            txt += line
        else:
            break
    return txt


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:],
                               'h',
                               ['id=', 'category=', 'description=', 'title=', 'mdfile='])

    id = None
    category = 0
    title = ''
    description = ''
    mdfile = ''

    for op, value in opts:
        if op == '--id':
            id = int(value)
        elif op == '--category':
            category = int(value)
        elif op == '--title':
            title = value
        elif op == '--description':
            description = value
        elif op == '--mdfile':
            mdfile = value

    if id:
        fw = FundWeekly.get(id)
        if not fw:
            rsyslog.send('FundWeekly %s not fund' % id, tag='fund')
            sys.exit(0)
    else:
        fw = FundWeekly.add(category=category)

    if title:
        fw.title = title

    if description:
        fw.description = description

    if mdfile:
        fw.content = get_content_of_file(mdfile)

    rsyslog.send('FundWeekly %s updated' % fw.id, tag='fund')
