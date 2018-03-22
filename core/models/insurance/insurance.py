# coding: utf-8

'''
insurance class
'''

from datetime import datetime
from libs.db.store import db
from libs.cache import mc, cache
from .insproperty import PropertyComprenhensiveInsurance
from .insproperty import PropertyCriticalInsurance
from .insproperty import PropertyEducationInsurance
from .consts import COMPREHENSIVE, CRITICAL_DISEASE, EDUCATION

_INSURE_INSURE_CACHE_KEY_PREFIX = 'insurance:ins:v2:'
INSURE_INSURE_CACHE_KEY = _INSURE_INSURE_CACHE_KEY_PREFIX + '{insurance_id}'

ALL_CHILDREN_INSURANCE_CACHE_KEY = _INSURE_INSURE_CACHE_KEY_PREFIX + 'all'
# 保险项目表的结构： Insurace
#     Id  类型    代码    名称    开始年龄    结束年龄    性别    保费    保额    创建时间    更新时间
#
#     字段说明：保费、费率表id两者不能同时为空，
#     保费作为区分计算类型的标志，
#     如果保费为空，则查询费率表，将查找到的项目 ＊ 保额  ，然后更新保费
#     如果保费不为空，则不需要查询费率表
#     根据保费，计算保费
#     类型    字段 可以是  0，1，2 分别 代表  综合险、重疾险、教育险


class Insurance(object):
    table_name = 'insurance'

    def __init__(self, insurance_id, kind, name):
        self.id = insurance_id
        self.kind = kind
        self.name = name
        self._ins_property = None

    def get_ins_sub_title(self, package_id):
        if self._ins_property is None:
            self._ins_property = self.ins_property
        return self._ins_property.get_ins_sub_title(package_id, self.id)

    def add_insurance_props(self, feerate, rec_reason, buy_url,
                            ins_title, ins_sub_title):
        self.ins_property.add_props(feerate, rec_reason, buy_url,
                                    ins_title, ins_sub_title)

    def get_fee(self, package_id, **kwargs):
        return self.ins_property.get(package_id, **kwargs)

    @property
    def ins_property(self):
        if self._ins_property:
            return self._ins_property

        if (self.kind == COMPREHENSIVE):
            self._ins_property = PropertyComprenhensiveInsurance(
                self.id, self.kind)
        elif (self.kind == CRITICAL_DISEASE):
            self._ins_property = PropertyCriticalInsurance(
                self.id, self.kind)
        elif (self.kind == EDUCATION):
            self._ins_property = PropertyEducationInsurance(
                self.id, self.kind)
        else:
            return None
        return self._ins_property

    @classmethod
    def add(cls, kind, insurance_id, name, status, rec_rank):
        sql = ('insert into {.table_name} '
               '( kind, insurance_id, name, status, rec_rank, '
               'create_time, update_time) '
               'values ( %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (kind, insurance_id, name, status, rec_rank,
                  datetime.now(), datetime.now())
        db.execute(sql, params)
        db.commit()
        cls.clear_cache(insurance_id)
        cls.get_all()

    # 根据保险代码获取保险实例
    @classmethod
    @cache(INSURE_INSURE_CACHE_KEY)
    def get(cls, insurance_id):
        sql = ('select insurance_id, kind, name from {.table_name} '
               'where insurance_id = %s').format(cls)
        param = insurance_id
        rs = db.execute(sql, param)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(ALL_CHILDREN_INSURANCE_CACHE_KEY)
    def _get_all_ids(cls):
        rs = db.execute('select insurance_id from ' + cls.table_name)
        ids = [str(id) for (id,) in rs]
        return ids

    @classmethod
    def gets(cls, ids):
        return [cls.get(id) for id in ids]

    @classmethod
    def get_all(cls):
        ids = cls._get_all_ids()
        return cls.gets(ids)

    @classmethod
    def clear_cache(cls, insurance_id):
        mc.delete(ALL_CHILDREN_INSURANCE_CACHE_KEY)
        mc.delete(INSURE_INSURE_CACHE_KEY.format(insurance_id=insurance_id))
