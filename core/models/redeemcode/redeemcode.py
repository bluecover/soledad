# coding:utf-8

import random
import MySQLdb
from datetime import datetime, date

from enum import Enum
from werkzeug.utils import cached_property

from libs.db.store import db
from libs.cache import mc, cache
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.welfare.package.package import distribute_welfare_gift
from core.models.utils.validator import is_include_chinese
from .usage import RedeemCodeUsage
from .activity import RedeemCodeActivity
from .consts import REDEEM_CODE_ALPHABET
from .errors import (RedeemCodeIneffectiveError, RedeemCodeExpiredError,
                     RedeemCodeExistedError, RedemptionBeyondLimitPerUserError)


class RedeemCode(PropsMixin):
    """兑换码为8位随机码或者定制码, 用来换取对应奖品

    兑换码有两种，一种是8位随机码，由数字和字母随机生成，另外一种为定制码(可能包含汉字),
    用户可根据兑换码在规定时间内，根据活动规则，领取兑换码内包含的奖品（奖品因活动不同而不同），
    使用兑换码时不区分字母的大小写

    :param code: 兑换码
    :param activity_id: 兑换码所属活动的id
    :param max_usage_limit_per_code: 每个兑换码允许使用的最大次数
    """

    table_name = 'redeem_code'
    cache_key = 'redeem_code:{id_}'
    cache_ids_by_activity_id_key = 'redeem_code:activity_id:{activity_id}'

    #: 兑换码用途的详细描述
    description = PropsItem('description', '')

    class Status(Enum):
        """兑换码的使用状态

        兑换码的状态分为有效和无效，有效的兑换码才能兑换礼包
        """
        #: 有效
        validated = 'V'

        #: 无效
        invalidated = 'I'

    class Source(Enum):
        """兑换码生成方式

        兑换码可由后台管理员根据需求生成或者由系统调用相应方法生成
        """

        #: 系统
        robot = 'R'

        #: 管理员
        manager = 'M'

    class Kind(Enum):
        """兑换码兑换策略

        兑换码进行分发礼包的策略，根据不同的策略完成分发
        """

        # 正常
        normal_package = 1

        # 特殊
        special_package = 2

    def __init__(self, id_, code, source, kind, status, activity_id,
                 max_usage_limit_per_code, creation_time, effective_time, expire_time):
        self.id_ = str(id_)
        self.code = code
        self._source = source
        self._kind = kind
        self._status = status
        self.activity_id = str(activity_id)
        self.max_usage_limit_per_code = max_usage_limit_per_code
        self.creation_time = creation_time
        self.effective_time = effective_time
        self.expire_time = expire_time

    def get_db(self):
        return 'redeem_code'

    def get_uuid(self):
        return 'redeem_code:{id_}'.format(id_=self.id_)

    @cached_property
    def kind(self):
        return self.Kind(self._kind)

    @cached_property
    def activity(self):
        return RedeemCodeActivity.get(self.activity_id)

    @property
    def is_effective(self):
        return self.effective_time <= datetime.now()

    @property
    def is_expired(self):
        return self.expire_time < datetime.now()

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, new_status):
        assert isinstance(new_status, self.Status)
        self._status = new_status.value

    @cached_property
    def source(self):
        return self.Source(self._source)

    @classmethod
    def create(cls, activity_id, kind, description, max_usage_limit_per_code,
               customized_code, effective_time, expire_time, _commit=True):
        assert isinstance(effective_time, date)
        assert isinstance(expire_time, date)
        assert max_usage_limit_per_code >= 1

        if customized_code:
            code = (
                customized_code.encode('utf-8') if is_include_chinese(customized_code)
                else customized_code)
        else:
            code = ''.join(random.sample(REDEEM_CODE_ALPHABET, 8))
        sql = ('insert into {.table_name} (code, activity_id, source,'
               ' max_usage_limit_per_code, kind, status, creation_time,'
               ' effective_time, expire_time)'
               ' values (%s, %s, %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (code, activity_id, cls.Source.manager.value, max_usage_limit_per_code,
                  kind, cls.Status.validated.value, datetime.now(), effective_time, expire_time)
        try:
            id_ = db.execute(sql, params)
        except MySQLdb.IntegrityError:
            raise RedeemCodeExistedError()
        if _commit:
            db.commit()

        #: 清除缓存
        cls.clear_cache(id_)
        cls.clear_cache_ids_by_activity_id(activity_id)

        instance = cls.get(id_)
        instance.description = unicode(description)
        return instance

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, code, source, kind, status, activity_id, max_usage_limit_per_code,'
               ' creation_time, effective_time, expire_time'
               ' from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_id_by_code(cls, code):
        sql = 'select id from {.table_name} where code=%s'.format(cls)
        params = (code,)
        rs = db.execute(sql, params)
        if rs:
            return rs[0][0]

    @classmethod
    def get_by_code(cls, code):
        id_ = cls.get_id_by_code(code)
        return cls.get(id_)

    @classmethod
    @cache(cache_ids_by_activity_id_key)
    def get_ids_by_activity_id(cls, activity_id):
        sql = 'select id from {.table_name} where activity_id=%s'.format(cls)
        params = (activity_id,)
        rs = db.execute(sql, params)
        if rs:
            return [r[0] for r in rs]

    @classmethod
    def get_by_activity_id(cls, activity_id):
        ids = cls.get_ids_by_activity_id(activity_id)
        return cls.get_multi_by_ids(ids)

    @classmethod
    def get_multi_by_ids(cls, ids):
        return [cls.get(str(id_)) for id_ in ids]

    def invalidate(self):
        sql = 'update {.table_name} set status = %s where id=%s'.format(self)
        params = (self.Status.invalidated.value, self.id_)
        db.execute(sql, params)
        db.commit()

        #: 清除缓存并更新兑换码可用状态
        self.clear_cache(self.id_)
        self.clear_cache_ids_by_activity_id(self.activity_id)
        self._clear_cached_properties()
        self.status = self.Status.invalidated

    @classmethod
    def create_multi_codes(cls, activity_id, kind, description, max_usage_limit_per_code,
                           redeem_code_count, effective_time, expire_time):
        customized_code = None
        try:
            for _ in xrange(int(redeem_code_count)):
                cls.create(activity_id, kind, description, max_usage_limit_per_code,
                           customized_code, effective_time, expire_time, _commit=False)
        except:
            db.rollback()
            raise
        else:
            db.commit()

    def _redeem_normal_package(self, user, redeem_code_usage):
        distribute_welfare_gift(user, self.activity.reward_welfare_package_kind, redeem_code_usage)

    kind_to_strategy = {
        Kind.normal_package: _redeem_normal_package
    }

    def _apply_strategy(self, user, redeem_code_usage):
        strategy = self.kind_to_strategy[self.kind]
        return strategy(self, user, redeem_code_usage)

    def redeem(self, user):
        self.check_for_available(user)
        redeem_code_usage = RedeemCodeUsage.add(self, user)
        try:
            self._apply_strategy(user, redeem_code_usage)
        except (RedeemCodeIneffectiveError, RedeemCodeExpiredError,
                RedemptionBeyondLimitPerUserError):
            redeem_code_usage.delete_by_id(redeem_code_usage.id_)
            raise

    def check_for_available(self, user):
        if not self.is_effective:
            raise RedeemCodeIneffectiveError()
        if self.is_expired:
            raise RedeemCodeExpiredError()

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_ids_by_activity_id(cls, activity_id):
        mc.delete(cls.cache_ids_by_activity_id_key.format(activity_id=activity_id))

    def _clear_cached_properties(self):
        self.__dict__.pop('source', None)
        self.__dict__.pop('kind', None)
        self.__dict__.pop('activity', None)
