from __future__ import print_function, absolute_import, unicode_literals

import os
import datetime

from enum import Enum

from libs.db.store import db
from libs.cache import mc, cache
from core.models.base import EntityModel


class Release(EntityModel):
    """The release of download file."""

    table_name = 'download_release'
    cache_key = 'download:release:{id_}'
    cache_key_by_project = 'download:project:{project_id}:release:ids'

    class Meta:
        repr_attr_names = ['project_id', 'internal_version', 'public_version',
                           'status', 'file_name', 'creation_time']

    class Status(Enum):
        draft = 'D'
        inhouse = 'I'
        public = 'P'
        absent = 'A'

    Status.draft.next_status_set = frozenset([
        Status.inhouse, Status.public, Status.absent])
    Status.inhouse.next_status_set = frozenset([Status.public, Status.absent])
    Status.public.next_status_set = frozenset([])
    Status.absent.next_status_set = frozenset([])

    def __init__(self, id_, project_id, internal_version, public_version,
                 status, file_name, creation_time):
        self.id_ = bytes(id_)
        self.project_id = bytes(project_id)
        self.internal_version = internal_version
        self.public_version = public_version
        self._status = status
        self.file_name = file_name
        self.creation_time = creation_time

    @property
    def status(self):
        return self.Status(self._status)

    @property
    def project(self):
        from .project import Project
        return Project.get(self.project_id)

    @property
    def display_version(self):
        return '{0.public_version} ({0.internal_version})'.format(self)

    @property
    def file_path(self):
        return os.path.join(self.project.name, self.file_name)

    @classmethod
    def add(cls, project_id, internal_version, public_version, file_name):
        sql = ('insert into {0} (project_id, internal_version, public_version,'
               ' status, file_name, creation_time)'
               'values (%s, %s, %s, %s, %s, %s)').format(cls.table_name)
        params = (project_id, internal_version, public_version,
                  cls.Status.draft.value, file_name, datetime.datetime.now())
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_project(project_id)
        return cls.get(id_)

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, project_id, internal_version, public_version, '
               'status, file_name, creation_time '
               'from {0} where id = %s').format(cls.table_name)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_key_by_project)
    def get_ids_by_project(cls, project_id):
        sql = 'select id from {0} where project_id = %s'.format(cls.table_name)
        params = (project_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def get_multi_by_project(cls, project_id):
        ids = cls.get_ids_by_project(project_id)
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_project(cls, project_id):
        mc.delete(cls.cache_key_by_project.format(**locals()))

    def can_transfer_status(self, new_status):
        return new_status in self.status.next_status_set

    def transfer_status(self, status):
        if not self.can_transfer_status(status):
            raise ValueError('%r can not transfer to %r' % (self.status, status))

        sql = 'update {0} set status = %s where id = %s'.format(self.table_name)
        params = (status.value, self.id_)
        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)
        self._status = status.value
