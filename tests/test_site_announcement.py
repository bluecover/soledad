from datetime import date, datetime, timedelta
from collections import namedtuple

from core.models.site import Announcement
from .framework import BaseTestCase


class AnnouncementTest(BaseTestCase):

    request = namedtuple('Request', ['endpoint'])

    def test_get_nothing(self):
        assert Announcement.get_multi_by_date(date.today()) == []

    def test_add_and_get(self):
        start_time = datetime.now() - timedelta(days=1)
        stop_time = datetime.now() + timedelta(days=1)

        foo = Announcement.add(
            subject=u'Foo',
            subject_type=Announcement.SubjectType.notice,
            content=u'Foo' * 200,
            content_type=Announcement.ContentType.markdown,
            start_time=start_time,
            stop_time=stop_time,
            endpoint='*')
        bar = Announcement.add(
            subject=u'Bar',
            subject_type=Announcement.SubjectType.notice,
            content=u'Bar' * 200,
            content_type=Announcement.ContentType.markdown,
            start_time=start_time,
            stop_time=stop_time,
            endpoint='wallet.*')

        assert foo
        assert bar

        items = Announcement.get_multi_by_date(date.today())
        assert set(items) == {foo, bar}

        assert foo.is_suitable(self.request('wallet.foo'))
        assert foo.is_suitable(self.request('hoard.foo'))

        assert bar.is_suitable(self.request('wallet.foo'))
        assert not bar.is_suitable(self.request('hoard.foo'))

    def test_markdown(self):
        start_time = datetime.now() - timedelta(days=1)
        stop_time = datetime.now() + timedelta(days=1)

        foo = Announcement.add(
            subject=u'Foo',
            subject_type=Announcement.SubjectType.notice,
            content=u'**foo**',
            content_type=Announcement.ContentType.markdown,
            start_time=start_time,
            stop_time=stop_time,
            endpoint='*')

        assert foo.content_type is Announcement.ContentType.markdown
        assert foo.subject_type is Announcement.SubjectType.notice

        assert foo.subject == u'Foo'
        assert foo.content_as_html == u'<p><strong>foo</strong></p>'
