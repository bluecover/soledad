# coding: utf-8

'''
package class
'''

from datetime import datetime
from libs.db.store import db
from libs.cache import cache, mc
from core.models.mixin.props import PropsMixin, PropsItem
from .consts import PACKAGE_UPGRADE_1, PACKAGE_UPGRADE_2


_PACKAGE_CACHE_PREFIX = 'package:v2:'
PACKAGE_CACHE_KEY = _PACKAGE_CACHE_PREFIX + '{package_id}'


class Package(PropsMixin):
    table_name = 'insurance_package'
    insurance_ability = PropsItem('insurance_ability', '')
    addition_ability = PropsItem('addition_ability', '')
    name = PropsItem('name', u'基础套餐')
    title = PropsItem('title')
    sub_title = PropsItem('sub_title')
    quota = PropsItem('quota')
    quota_b = PropsItem('quota_b', 'quota_b commedy')
    radar = PropsItem('radar')

    def __init__(self, package_id,
                 insurance_id,
                 rec_rank_in_package,
                 package_rec_rank):
        self.id = package_id
        self.insurance_id = insurance_id
        self.rec_rank_in_package = rec_rank_in_package
        self.package_rec_rank = package_rec_rank

    def get_db(self):
        return 'package_insurance'

    def get_uuid(self):
        return 'package_insurance:ability:%s' % self.id

    @classmethod
    def add(cls, package_id, pkg_name, insurance_id, insurance_name, status,
            rec_rank_in_package, package_rec_rank):
        sql = ('insert into {.table_name} '
               '(package_id, pkg_name, insurance_id, insurance_name, status, '
               'rec_rank_in_package, package_rec_rank, create_time, update_time) '
               'values ( %s, %s, %s, %s, %s, %s, %s ,%s, %s)').format(cls)

        params = (package_id, pkg_name, insurance_id, insurance_name, status,
                  rec_rank_in_package, package_rec_rank,
                  datetime.now(), datetime.now())
        db.execute(sql, params)
        db.commit()

        cls.clear_cache(package_id)
        cls.get(package_id)

    @classmethod
    @cache(PACKAGE_CACHE_KEY)
    def get(cls, package_id):
        sql = ('select package_id, insurance_id,rec_rank_in_package, '
               'package_rec_rank from {.table_name} where package_id = %s').format(cls)
        param = package_id
        rs = db.execute(sql, param)
        return [cls(*item)
                for item in rs if item is not None]

    @classmethod
    def clear_cache(cls, package_id):
        mc.delete(PACKAGE_CACHE_KEY.format(package_id=package_id))

    @classmethod
    def get_by_insurance_id(cls, insurance_id):
        sql = ('select package_id, insurance_id from {.table_name} '
               'where insurance_id = %s').format(cls)
        param = insurance_id
        rs = db.execute(sql, param)
        pkg_ids = [str(pkg_id) for pkg_id in rs]
        return [cls.get(pkg_id) for pkg_id in pkg_ids]

    # get package by package_id and insurance_id
    @classmethod
    def get_by_pkg_id_insurance_id(cls, pkg_id, insurance_id):
        return cls(pkg_id, insurance_id)

    def cat_ability(self, ageobj):
        if (ageobj.birth[0] == 0 and ageobj.birth[1] < 60 and
                self.id in [PACKAGE_UPGRADE_1, PACKAGE_UPGRADE_2]):
            return ''.join([self.insurance_ability, self.addition_ability])
        return self.insurance_ability
