# coding: utf-8

from datetime import datetime

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from core.models.consts import SetOperationKind
from .account import Account


def collect_user_tags(user_id):
    from core.models.hoard.manager import SavingsManager

    tags = set()

    # 判断用户是否是攒钱用户
    sm = SavingsManager(user_id)
    if not sm.is_new_savings_user:
        tags.add('savings')

    return tags


class UserTag(EntityModel):
    """用户与标签的绑定"""

    table_name = 'user_tag'
    cache_key = 'user:tag:v1:{id_}'
    cache_key_by_user_id = 'user:tag:v1:user:{user_id}'

    def __init__(self, id_, user_id, tag, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.tag = tag
        self.creation_time = creation_time

    @classmethod
    def check_before_create(cls, user, tag):
        assert isinstance(user, Account)

        tag = str(tag) if tag else ''
        if len(tag) < 2:
            raise ValueError('invalid tag %s' % tag)

    @classmethod
    def create(cls, user, tag, _commit=True):
        """为指定设备添加单个标签"""
        cls.check_before_create(user, tag)

        sql = ('insert into {.table_name} (user_id, tag, creation_time) '
               'values (%s, %s, %s)').format(cls)
        params = (user.id_, tag, datetime.now())
        id_ = db.execute(sql, params)
        if _commit:
            db.commit()
            cls.clear_cache_by_user(user.id_)
            return cls.get(id_)
        return id_

    @classmethod
    def create_multi_by_user(cls, user, tags, _commit=True):
        """为指定用户添加多个标签"""
        tags = set(tags) if tags else set()
        if not tags:
            return

        id_list = []
        try:
            for tag in tags:
                id_list.append(cls.create(user, tag, _commit=False))
        except:
            db.rollback()
            raise
        else:
            if _commit:
                db.commit()
                cls.clear_cache_by_user(user.id_)
                return cls.get_multi(id_list)
            return id_list

    @classmethod
    def remove_multi_by_user(cls, user, tags, _force=False, _commit=True):
        """为指定设备删除部分标签，通常发生在当设备登录用户标签组发生变化时"""
        tags = set(tags) if tags else set()
        if not tags:
            return

        if not _force:
            existed_tags = set(cls.get_multi_by_user(user))
            if not (tags - existed_tags):
                raise ValueError('deleting tags which are not belong to the binding')

        extra_condition = 'and (%s)' % ' or '.join(['tag=%s'] * len(tags))
        sql = 'delete from {0.table_name} where user_id=%s {1}'.format(cls, extra_condition)
        params = (user.id_, ) + tuple(tags)
        db.execute(sql, params)
        if _commit:
            db.commit()
            cls.clear_cache_by_user(user.id_)

    @classmethod
    def align_tags_by_user(cls, user, latest_tags):
        """为指定设备在单事务中进行多标签的增删"""
        # 获取用户已存标签
        existed_tags = [t.tag for t in cls.get_multi_by_user(user.id_)]

        # 本地标签调整
        additions = set(latest_tags) - set(existed_tags)
        deletions = set(existed_tags) - set(latest_tags)

        if not (additions or deletions):
            return

        try:
            cls.create_multi_by_user(user, additions, _commit=False)
            cls.remove_multi_by_user(user, deletions, _commit=False)
        except:
            db.rollback()
            raise
        else:
            db.commit()
            cls.clear_cache_by_user(user.id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, tag, creation_time '
               'from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_user_id_list_by_tags(cls, tags_set, set_operation_kind=SetOperationKind.union):
        assert isinstance(set_operation_kind, SetOperationKind)

        tags = tuple(tags_set)
        if not tags:
            return

        union_segment = ' or '.join(['tag=%s'] * len(tags))

        if set_operation_kind is SetOperationKind.union:
            sql = ('select distinct(user_id) from {0.table_name} '
                   'where ({1})').format(cls, union_segment)
            params = tags
        elif set_operation_kind is SetOperationKind.intersection:
            sql = ('select distinct(user_id) from (select user_id, count(*) '
                   'as tcount from {0.table_name} where ({1}) group by user_id) '
                   'tb where tcount=%s').format(cls, union_segment)
            params = tags + (len(tags),)
        else:
            raise ValueError('invalid set operation kind')

        rs = db.execute(sql, params)
        for r in rs:
            yield r[0]

    @classmethod
    @cache(cache_key_by_user_id)
    def get_id_list_by_user_id(cls, user_id):
        sql = 'select id from {.table_name} where user_id=%s'.format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        id_list = cls.get_id_list_by_user_id(user_id)
        return cls.get_multi(id_list)

    @classmethod
    def get_multi(cls, id_list):
        return [cls.get(id_) for id_ in id_list]

    @classmethod
    def get_all_tags(cls):
        sql = 'select distinct(tag) from {.table_name}'.format(cls)
        rs = db.execute(sql)
        return [r[0] for r in rs]

    @classmethod
    def clear_by_user(cls, user):
        """为用户清空全部标签"""
        sql = 'delete from {.table_name} where user_id=%s'.format(cls)
        params = (user.id_, )
        db.execute(sql, params)
        db.commit()

    @classmethod
    def clear_by_tag(cls, abandon_tag):
        """根据标签清空所有对应记录"""
        sql = 'select user_id from {.table_name} where tag=%s'.format(cls)
        params = (abandon_tag, )
        rs = db.execute(sql, params)
        influenced_user_ids = [r[0] for r in rs]

        sql = 'delete from {.table_name} where tag=%s'.format(cls)
        db.execute(sql, params)
        db.commit()

        for uid in influenced_user_ids:
            cls.clear_cache_by_user(uid)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_key_by_user_id.format(**locals()))
