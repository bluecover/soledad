# -*- coding: utf-8 -*-

import hashlib

from random import randint
from simpleflake import simpleflake

from libs.db.store import db
from libs.cache import mc, cache


_SHORTEN_URL_MC_KEY = 'shorten:url:%s'


class ShortenUrl(object):

    @classmethod
    def gen_key(cls, code=None):
        '''
        生成随机带字符串的 code
        '''

        if code:
            return str(code), ''

        offset = 4
        confuse = str(simpleflake())
        index = randint(0, offset)
        last = index + offset

        code = hashlib.sha224(confuse).hexdigest()[index:last]
        return code, confuse

    @classmethod
    def gen(cls, url, code=None):
        '''
        生成短网址
        '''
        code, confuse = cls.gen_key(code)
        db.execute('insert into shorten_url '
                   '(code, confuse, url) '
                   'values '
                   '(%s, %s, %s)',
                   (code, confuse, url))
        db.commit()
        return code

    @classmethod
    @cache(_SHORTEN_URL_MC_KEY % '{code}')
    def get(cls, code):
        '''
        根据 code 获取短网址
        '''
        r = db.execute('select url from shorten_url where code=%s', (code,))
        if r:
            return r[0][0]

    @classmethod
    def update(cls, code, url):
        '''
        根据 code 更新短网址
        '''
        db.execute('update shorten_url set url=%s where code=%s', (url, code))
        db.commit()
        mc.delete(_SHORTEN_URL_MC_KEY % code)
        return True
