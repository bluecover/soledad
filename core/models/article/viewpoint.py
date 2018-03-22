# -*- coding: utf-8 -*-

from werkzeug.contrib.atom import FeedEntry

from libs.markdown import render
from core.models.mixin.props import PropsItem
from jupiter.utils import permalink
from .article import Article
from .consts import VIEWPOINT


class ViewPoint(Article):
    kind = VIEWPOINT.KIND
    kind_cn = u'理财师观点'
    type = VIEWPOINT.TYPE

    title = PropsItem('title', '')
    content = PropsItem('content', '')
    author = PropsItem('author', '')

    _const = VIEWPOINT

    def __repr__(self):
        return '<ViewPoint id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @permalink('article.article_detail')
    def url(self):
        return {'article_type': 'viewpoints', 'id': self.id}

    def make_feed_entry(self):
        return FeedEntry(
            self.title, render(self.content),
            content_type='html',
            author=self.author or u'好规划网理财师',
            url=self.url,
            updated=self.update_time,
            published=self.publish_time)
