# -*- coding: utf-8 -*-

'''
这是一个基本的文本的基类，继承时需要编写参数

prefix    -> 唯一性存储前缀
type      -> 文章的类型，例如问答也是从这里继承的

class SomeArticle(Article):
    prefix = 'some'
    type = 0

这个基类实现了基本的文章的id、类型、创建时间和修改时间

其他的全都使用Props作为存储，并且存储在NoSQL中

所以继承Article的子类的数据都存在一个数据库中

其中prefix和type都不允许和其他类型的Article重复

并且名称和类型都需要从 core.models.article.consts 中引入
'''


from datetime import datetime

from warnings import warn
from MySQLdb import IntegrityError
from libs.db.store import db
from libs.cache import mc, cache, pcache

from core.models.mixin.props import PropsMixin, PropsItem
from solar.utils.storify import storify

from .consts import VIEWPOINT, QUESTION, FUNDWEEKLY

_ARTICLE_CACHE_PREFIX = 'article:'

ARTICLE_CACHE_KEY = _ARTICLE_CACHE_PREFIX + '%s'
ARTICLE_ALL_CACHE_KEY = _ARTICLE_CACHE_PREFIX + 'all:%s:%s'
ARTICLE_ALL_TYPE_CACHE_KEY = _ARTICLE_CACHE_PREFIX + 'alltype:%s'
ARTICLE_CATE_CACHE_KEY = _ARTICLE_CACHE_PREFIX + 'cate:%s:%s:%s'
ARTICLE_COUNT_CACHE_KEY = _ARTICLE_CACHE_PREFIX + 'count:%s:%s'

STATUS = storify(dict(
    NONE=0,
    PUBLISHED=1,
    DELETED=2
))


class Article(PropsMixin):
    # need to add
    # kind is uuid
    # type is article type

    _const = {}
    kind = 'article'
    type = 'article'

    # admin record
    _add_admin = PropsItem('add_admin', '')
    _publish_admin = PropsItem('publish_admin', '')
    _delete_admin = PropsItem('delete_admin', '')

    def __init__(self, id, category, create_time,
                 update_time, publish_time, status):
        self.id = str(id)
        self.category = str(category)
        self.create_time = create_time
        self.update_time = update_time
        self.publish_time = publish_time
        self.status = int(status)

    def __repr__(self):
        return '<Article id=%s, type=%s, status=%s>' % (
            self.id, self.type, self.status
        )

    def get_uuid(self):
        return '%s:content:%s' % (self.kind, self.id)

    def get_db(self):
        # All the articles save in one CouchDB
        return 'article'

    @classmethod
    @cache(ARTICLE_CACHE_KEY % '{doc_id}')
    def get(cls, doc_id):
        from .viewpoint import ViewPoint
        from .question import Question
        from .fundweekly import FundWeekly
        doc_id = str(doc_id)
        rs = db.execute('select id, type, category, create_time, update_time, '
                        'publish_time, '
                        'status from article where id=%s',
                        (doc_id,))
        if rs:
            (id, type, category, create_time,
             update_time, publish_time, status) = rs[0]
            if type == VIEWPOINT.TYPE:
                return ViewPoint(id, category, create_time,
                                 update_time, publish_time, status)
            elif type == QUESTION.TYPE:
                return Question(id, category, create_time,
                                update_time, publish_time, status)
            elif type == FUNDWEEKLY.TYPE:
                return FundWeekly(id, category, create_time,
                                  update_time, publish_time, status)

    @classmethod
    def gets(cls, doc_ids):
        return [cls.get(id) for id in doc_ids]

    @classmethod
    @pcache(ARTICLE_CATE_CACHE_KEY % ('{type}', '{category}', '{status}'), count=20)
    def _get_article_ids_by_type_and_category(cls, type, category,
                                              status=STATUS.PUBLISHED, start=0, limit=20):
        rs = db.execute('select id '
                        'from article '
                        'where type=%s and category=%s and status=%s '
                        'order by publish_time desc limit %s, %s',
                        (type, category, status, start, limit))
        return [str(id) for (id,) in rs]

    @classmethod
    def get_articles_by_type_and_category(cls, type, category,
                                          status=STATUS.PUBLISHED, start=0, limit=20):
        ids = cls._get_article_ids_by_type_and_category(
            type, category, status, start, limit)
        return cls.gets(ids)

    @classmethod
    def get_articles_by_category(cls, category, status=STATUS.PUBLISHED, start=0, limit=20):
        return cls.get_articles_by_type_and_category(cls.type, category, status, start, limit)

    @classmethod
    @pcache(ARTICLE_ALL_CACHE_KEY % ('{type}', '{status}'))
    def _get_all_ids(cls, type, status=STATUS.PUBLISHED, start=0, limit=20):
        rs = db.execute('select id from article '
                        'where status=%s and type=%s '
                        'order by publish_time desc limit %s,%s ',
                        (status, type, start, limit))
        ids = [str(id) for (id,) in rs]
        return ids

    @classmethod
    def get_all(cls, type=None, status=STATUS.PUBLISHED, start=0, limit=20):
        if type is None:
            type = cls.type
        ids = cls._get_all_ids(type=type, status=status,
                               start=start, limit=limit)
        return cls.gets(ids)

    @classmethod
    @cache(ARTICLE_COUNT_CACHE_KEY % ('{type}', '{status}'))
    def get_count(cls, type=None, status=STATUS.PUBLISHED):
        if type is None:
            type = cls.type
        return db.execute('select count(id) from article '
                          'where status=%s and type=%s',
                          (status, type))[0][0]

    @classmethod
    def get_count_by_category(cls, category):
        ids = cls._get_article_ids_by_type_and_category(cls.kind, category)
        return len(ids)

    @classmethod
    def add(cls, type=None, category=0, create_time=None, admin_id=None):
        type = type or cls.type
        create_time = create_time or datetime.now()
        try:
            id = db.execute('insert into article '
                            '(type, category, create_time) '
                            'values (%s, %s, %s)',
                            (type, category, create_time))
            if id:
                db.commit()
                article = cls.get(id)
                article.clear_cache()
                article._add_admin = admin_id
                return article
            else:
                db.rollback()
        except IntegrityError:
            db.rollback()
            warn('insert article failed')

    def is_deleted(self):
        return self.status == STATUS.DELETED

    def is_published(self):
        return self.status == STATUS.PUBLISHED

    @property
    def category_name(self):
        _cate_type = self._const.CATEGORY
        if _cate_type:
            return _cate_type.get(self.category)

    def _upadte_status(self, status):
        db.execute('update article set status=%s where id=%s',
                   (status, self.id))
        db.commit()
        self.clear_cache()

    def delete(self):
        self._upadte_status(STATUS.DELETED)

    def publish(self, publish_time=None):
        publish_time = publish_time or datetime.now()
        db.execute('update article set publish_time=%s where id=%s',
                   (publish_time, self.id))
        self._upadte_status(STATUS.PUBLISHED)
        self.clear_cache()

    def hide(self):
        self._upadte_status(STATUS.NONE)

    def clear_cache(self):
        mc.delete(ARTICLE_CACHE_KEY % (self.id))
        for name, status in STATUS.items():
            mc.delete(ARTICLE_ALL_CACHE_KEY % (self.type, status))
            mc.delete(ARTICLE_ALL_TYPE_CACHE_KEY % (status))
            mc.delete(ARTICLE_COUNT_CACHE_KEY % (self.type, status))
            mc.delete(ARTICLE_CATE_CACHE_KEY % (
                self.type, self.category, status))
