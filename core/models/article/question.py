# -*- coding: utf-8 -*-

from core.models.mixin.props import PropsItem
from jupiter.utils import permalink
from .article import Article
from .consts import QUESTION


class Question(Article):
    kind = QUESTION.KIND
    type = QUESTION.TYPE

    ask = PropsItem('ask', '')
    answer = PropsItem('answer', '')

    _const = QUESTION

    def __repr__(self):
        return '<Question id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    @permalink('article.article_detail')
    def url(self):
        return {'article_type': 'consultations', 'id': self.id}
