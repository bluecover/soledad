# coding: utf-8

from __future__ import absolute_import

import datetime
import glob

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from libs.markdown import render_markdown
from core.models.base import EntityModel
from core.models.utils import datetime_range
from core.models.mixin.props import PropsMixin, PropsItem


class Announcement(EntityModel, PropsMixin):
    """The announcement information of whole site."""

    class SubjectType(Enum):
        notice = 'N'

    class Status(Enum):
        present = 'P'
        absent = 'A'

    class ContentType(Enum):
        markdown = 'M'

    ContentType.markdown.to_html = render_markdown

    table_name = 'site_announcement'
    cache_key = 'site:announcement:{id_}'
    cache_by_date_key = 'site:announcement:date:{date}:ids'

    #: The subject of announcement
    subject = PropsItem('subject', default=u'')

    #: The content of announcement
    content = PropsItem('content', default=u'')

    def __init__(self, id_, subject_type_code, content_type_code, status_code,
                 start_time, stop_time, endpoint, creation_time):
        self.id_ = bytes(id_)
        self.subject_type_code = subject_type_code
        self.content_type_code = content_type_code
        self.status_code = status_code

        #: The announcement be visible since this time
        self.start_time = start_time
        #: The announcement be invisible since this time
        self.stop_time = stop_time
        #: The announcement only be visible in special Flask endpoint
        self.endpoint = endpoint
        #: The creation time of announcement
        self.creation_time = creation_time

    @cached_property
    def subject_type(self):
        """The subject type of announcement.

        :rtype: :class:`.Announcement.SubjectType`
        """
        return self.SubjectType(self.subject_type_code)

    @cached_property
    def content_type(self):
        """The content type of announcement.

        :rtype: :class:`.Announcement.ContentType`
        """
        return self.ContentType(self.content_type_code)

    @property
    def content_as_html(self):
        """The announcement content as HTML format."""
        return self.content_type.to_html(self.content).strip()

    @property
    def status(self):
        """The status of announcement.

        :rtype: :class:`.Announcement.Status`
        """
        return self.Status(self.status_code)

    def get_db(self):
        return 'site_announcement'

    def get_uuid(self):
        return self.id_

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, subject_type, content_type, status, start_time,'
               ' stop_time, endpoint, creation_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def add(cls, subject, subject_type, content, content_type, start_time,
            stop_time, endpoint):
        assert isinstance(subject_type, cls.SubjectType)
        assert isinstance(content_type, cls.ContentType)
        assert start_time < stop_time
        assert datetime.datetime.now() < stop_time

        initial_status = cls.Status.present

        sql = (
            'insert into {0} (subject_type, content_type, status,'
            ' start_time, stop_time, endpoint, creation_time) '
            'values (%s, %s, %s, %s, %s, %s, %s)').format(cls.table_name)
        params = (
            subject_type.value, content_type.value, initial_status.value,
            start_time, stop_time, endpoint, datetime.datetime.now())

        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        for date in datetime_range(start_time, stop_time):
            cls.clear_cache_by_date(date)

        instance = cls.get(id_)
        instance.subject = subject
        instance.content = content

        return instance

    @classmethod
    @cache(cache_by_date_key)
    def get_ids_by_date(cls, date):
        assert isinstance(date, datetime.date)
        sql = ('select id from {0} where date(start_time) <= %s and'
               ' date(stop_time) > %s').format(cls.table_name)
        params = (date, date)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_date(cls, date, status=Status.present):
        ids = cls.get_ids_by_date(date)
        announcements = (cls.get(id_) for id_ in ids)
        return [a for a in announcements if a.status is status]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_date(cls, date):
        mc.delete(cls.cache_by_date_key.format(**locals()))

    def is_suitable(self, request):
        return glob.fnmatch.fnmatch(request.endpoint, self.endpoint)
