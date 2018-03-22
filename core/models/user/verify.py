# -*- coding: utf-8 -*-

import re
import random
from datetime import datetime, timedelta

from MySQLdb import IntegrityError

from libs.db.store import db

from core.models.utils import randbytes
from core.models.user.consts import VERIFY_CODE_TYPE


MAX_RETRY = 3
SHORT_CODE_KIND_GROUP = [
    VERIFY_CODE_TYPE.REG_MOBILE,
    VERIFY_CODE_TYPE.BIND_MOBILE,
    VERIFY_CODE_TYPE.FORGOT_PASSWORD_MOBILE,
    VERIFY_CODE_TYPE.CHILD_INSURE,
    VERIFY_CODE_TYPE.REBATE_WITHDRAW,
    VERIFY_CODE_TYPE.CHANGE_MOBILE_VERIFY_OLD,
    VERIFY_CODE_TYPE.CHANGE_MOBILE_SET_NEW]


class Verify(object):

    re_short_code = re.compile(r'^[0-9]{6}$')
    re_long_code = re.compile(r'^[0-9a-z]{32}$')

    def __init__(self, id, user_id, type,
                 code, created_time, verify_time):
        self.id = str(id)
        self.user_id = str(user_id)
        self.type = str(type)
        self.code = code
        self.created_time = created_time
        self.verify_time = verify_time

    @classmethod
    def _remove(cls, user_id):
        '''
        if user add verify and then
        readd verify, need to remove
        first
        '''
        db.execute('delete from user_verify where user_id=%s', user_id)
        db.commit()

    @classmethod
    def add(cls, user_id, code_type, verify_delta=timedelta(hours=24)):
        assert isinstance(verify_delta, timedelta)

        created_time = datetime.now()
        verify_time = created_time + verify_delta

        cls._remove(user_id)

        verify_code = gen_verify_code(code_type)

        i = 0
        while i < MAX_RETRY:
            try:
                id = db.execute(
                    'insert into user_verify '
                    '(user_id, code_type, verify_code, created_time, '
                    'verify_time) values(%s, %s, %s, %s, %s)',
                    (user_id, code_type, verify_code,
                     created_time, verify_time))
                if id:
                    db.commit()
                    c = cls.get(id)
                    return c
                else:
                    i += 1
                    verify_code = gen_verify_code(code_type)
                    db.rollback()
            except IntegrityError:
                i += 1
                verify_code = gen_verify_code(code_type)
                db.rollback()

    @classmethod
    def get(cls, id):
        rs = db.execute('select id, user_id, code_type, verify_code, '
                        'created_time, verify_time from '
                        'user_verify where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    def gets_by_user_id(cls, uid):
        rs = db.execute('select id, user_id, code_type, verify_code, '
                        'created_time, verify_time from '
                        'user_verify where user_id=%s', (uid,))
        return [cls(*r) for r in rs if r] if rs else []

    @classmethod
    def get_by_user_id_and_type(cls, uid, type):
        rs = db.execute('select id, user_id, code_type, verify_code, '
                        'created_time, verify_time from '
                        'user_verify where user_id=%s '
                        'and code_type=%s',
                        (uid, type))
        return cls(*rs[0]) if rs else None

    @classmethod
    def gets_by_code(cls, code):
        rs = db.execute('select id, user_id, code_type, verify_code, '
                        'created_time, verify_time from '
                        'user_verify where verify_code=%s', (code,))
        return [cls(*r) for r in rs or []]

    def delete(self):
        db.execute('delete from user_verify where id=%s', (self.id,))
        db.commit()

    @property
    def outdated(self):
        return datetime.now() > self.verify_time

    @classmethod
    def validate(cls, user_id, code, kind):
        code = bytes(code)
        if kind in SHORT_CODE_KIND_GROUP:
            pattern = cls.re_short_code
        else:
            pattern = cls.re_long_code
        if not pattern.search(code):
            raise InvalidVerifyCodeError()

        fits = [v for v in cls.gets_by_code(code)
                if v.user_id == user_id and v.type == kind]

        if not fits:
            raise WrongVerifyCodeError()

        # as user_id * kind is unique key currently,
        # this error won't happen in normal cases
        if len(fits) > 1:
            raise DuplicateVerifyCodeError()

        fit = fits[0]
        if fit.outdated:
            raise OutdatedVerifyCodeError
        return fit


def gen_verify_code(code_type):
    verify_code = randbytes(16)
    if code_type in SHORT_CODE_KIND_GROUP:
        verify_code = '%06d' % random.randint(1, 999999)
    return verify_code


class VerifyCodeException(Exception):
    def __unicode__(self):
        return u'验证码填写有误，请重新输入'


class InvalidVerifyCodeError(VerifyCodeException):
    pass


class DuplicateVerifyCodeError(VerifyCodeException):
    pass


class WrongVerifyCodeError(VerifyCodeException):
    pass


class OutdatedVerifyCodeError(VerifyCodeException):

    def __unicode__(self):
        return u'验证码已过期，请重新获取验证码'
