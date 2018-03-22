# -*- coding: utf-8 -*-

from solar.utils.storify import storify

# Do not use this direct
VIEWPOINT_CATEGORY = {
    '10000': '理财课堂',
    '10001': '产品评测',
    '10002': '投资机会',
    '10003': '风险提示',
    '10004': '理财周报',
    '10005': '我问理财师',
}
TOPIC_CATEGORY = {}
QUESTION_CATEGORY = {}
FUNDWEEKLY_CATEGORY = {
    '1': '主题精选',
    '2': '稳拿计划',
}

# Use these as article consts
VIEWPOINT = storify(dict(KIND='viewpoint',
                         TYPE=1,
                         CATEGORY=VIEWPOINT_CATEGORY))

TOPIC = storify(dict(KIND='topic',
                TYPE=2,
                CATEGORY=TOPIC_CATEGORY))

QUESTION = storify(dict(KIND='question',
                   TYPE=3,
                   CATEGORY=QUESTION_CATEGORY))

FUNDWEEKLY = storify(dict(KIND='fundweekly',
                          TYPE=4,
                          CATEGORY=FUNDWEEKLY_CATEGORY))
