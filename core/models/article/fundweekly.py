# -*- coding: utf-8 -*-

from core.models.mixin.props import PropsItem
from jupiter.utils import permalink
from libs.cache import mc
from .article import Article
from .consts import FUNDWEEKLY

_FUNDWEEKLY_CACHE_PREFIX = 'fundweekly:'
FUNDWEEKLY_READ_CACHE_KEY = _FUNDWEEKLY_CACHE_PREFIX + 'read:%s:%s'


class FundWeekly(Article):
    kind = FUNDWEEKLY.KIND
    kind_cn = u'基金组合周报'
    type = FUNDWEEKLY.TYPE

    title = PropsItem('title', '')
    description = PropsItem('description', '')
    content = PropsItem('content', '')
    author = PropsItem('author', '')

    _const = FUNDWEEKLY

    def __repr__(self):
        return '<FundWeekly id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @permalink('article.article_detail')
    def url(self):
        return {'article_type': 'fund/weekly', 'id': self.id}

    def mark_as_read(self, user_id):
        mc.set(FUNDWEEKLY_READ_CACHE_KEY % (self.id, user_id), True)

    def has_read(self, user_id):
        return mc.get(FUNDWEEKLY_READ_CACHE_KEY % (self.id, user_id))
