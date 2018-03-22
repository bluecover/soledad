from __future__ import print_function, absolute_import, unicode_literals

import datetime
import pkg_resources

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel
from .release import Release


class Project(EntityModel):
    """The project of download files."""

    table_name = 'download_project'
    cache_key = 'download:project:{id_}'
    cache_key_by_name = 'download:project:name:{name}:id'

    class Meta:
        repr_attr_names = ['name', 'display_name', 'creation_time']

    def __init__(self, id_, name, display_name, bucket_name, creation_time):
        self.id_ = bytes(id_)
        self.name = name
        self.display_name = display_name
        self.bucket_name = bucket_name
        self.creation_time = creation_time

    @classmethod
    def add(cls, name, display_name, bucket_name='guihua-download'):
        sql = ('insert into {0} (name, display_name, bucket_name,'
               ' creation_time) '
               'values (%s, %s, %s, %s)').format(cls.table_name)
        params = (name, display_name, bucket_name, datetime.datetime.now())
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, name, display_name, bucket_name, creation_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_by_name)
    def get_id_by_name(cls, name):
        sql = 'select id from {0} where name = %s'.format(cls.table_name)
        params = (name,)
        rs = db.execute(sql, params)
        return rs[0][0] if rs else None

    @classmethod
    def get_by_name(cls, name):
        id_ = cls.get_id_by_name(name)
        return cls.get(id_) if id_ else None

    @classmethod
    def get_all_ids(cls):
        sql = 'select id from {0}'.format(cls.table_name)
        rs = db.execute(sql, ())
        return [r[0] for r in rs]

    @classmethod
    def get_all(cls):
        ids = cls.get_all_ids()
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    def edit_display_name(self, display_name):
        display_name = unicode(display_name)
        sql = ('update {0} set display_name = %s '
               'where id = %s').format(self.table_name)
        params = (display_name, self.id_)
        db.execute(sql, params)
        db.commit()
        self.display_name = display_name
        self.clear_cache(self.id_)

    def get_latest_release(self, include_draft=False, include_inhouse=False):
        allowed_status_set = {Release.Status.public}
        if include_draft:
            allowed_status_set.add(Release.Status.draft)
        if include_inhouse:
            allowed_status_set.add(Release.Status.inhouse)
        releases = [
            r for r in self.list_releases() if r.status in allowed_status_set]
        if not releases:
            return
        return max(releases, key=obtain_public_version)

    def list_releases(self):
        return Release.get_multi_by_project(self.id_)

    def add_release(self, internal_version, public_version, file_name):
        return Release.add(
            self.id_, internal_version, public_version, file_name)


def obtain_public_version(release):
    return pkg_resources.parse_version(release.public_version)
