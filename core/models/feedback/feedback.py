# -*- coding: utf-8 -*-
from MySQLdb import IntegrityError

from libs.db.store import db
from libs.cache import cache, pcache
from warnings import warn

from datetime import datetime

from core.models.mixin.props import PropsMixin
from core.models.mixin.props import PropsItem
from core.models.mail.kind import feedback_mail
from core.models.mail.mail import Mail


_FEEDBACK_CACHE_PREFIX = 'feedback:'
FEEDBACK_CACHE_KEY = _FEEDBACK_CACHE_PREFIX + '%s'
ALL_FEEDBACK_CACHE_KEY = _FEEDBACK_CACHE_PREFIX + 'all'

MAX_FEEDBACK_CONTACT_LEN = 60
MAX_FEEDBACK_CONTENT_LEN = 2000


class Feedback(PropsMixin):

    def __init__(self, id, contact, create_time, update_time):
        self.id = str(id)
        self.contact = contact
        self.create_time = create_time
        self.update_time = update_time

    def get_db(self):
        return 'feedback'

    def get_uuid(self):
        return 'feedback:%s' % self.id

    content = PropsItem('content', '')
    answer = PropsItem('answer', '')
    admin = PropsItem('admin', '')

    @classmethod
    def add(cls, contact, content):
        try:
            id = db.execute('insert into feedback '
                            '(contact, create_time) '
                            'values(%s, %s)',
                            (contact, datetime.now()))
            if id:
                db.commit()
                c = cls.get(id)
                c.content = content
                return c
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert feedback failed')

    @classmethod
    @cache(FEEDBACK_CACHE_KEY % '{id}')
    def get(cls, id):
        rs = db.execute('select id, contact, create_time, '
                        'update_time from feedback '
                        'where id=%s', (id,))
        return cls(*rs[0]) if rs else None

    @classmethod
    @pcache(ALL_FEEDBACK_CACHE_KEY)
    def _get_all_ids(cls, start=0, limit=20):
        sql = 'select id from feedback order by update_time desc limit %s,%s'
        rs = db.execute(sql, (start, limit))
        ids = [str(id) for (id,) in rs]
        return ids

    @classmethod
    def get_all(cls, start=0, limit=20):
        ids = cls._get_all_ids(start=start, limit=limit)
        return [cls.get(id) for id in ids]


def reply_feedback(feed, answer, admin_id):
    from flask import url_for

    if not feed or not answer:
        return
    feed.answer = answer
    feed.admin = admin_id
    mail_template_args = {
        'feedback': feed.content,
        'answer': answer,
        'server': url_for('home.home', _external=True),
    }
    mail = Mail.create(feed.contact, feedback_mail, sender_name=feed.contact, **mail_template_args)
    mail.send()
