# coding:utf-8

from __future__ import print_function, absolute_import

import datetime

from enum import Enum
from werkzeug.utils import cached_property

from .consts import MAGIC_SEED
from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.base import EntityModel
from core.models.user.account import Account
from core.models.welfare.package.kind import invite_investment_package
from core.models.hoard.signals import zw_order_succeeded, xm_order_succeeded
from .signals import invitation_accepted


class Invitation(EntityModel):
    """用户受邀记录

    :param invitee_id: 受邀请用户 ID
    :param inviter_id: 发出邀请用户 ID
    :param kind: 邀请活动类型
    :param status: 本条记录所处在的状态
    :param expire_time: 到期时间
    """

    table_name = 'invitation'
    cache_key = 'invitation:{id_}:v1'
    cache_key_by_inviter_id = 'invitation:inviter:{inviter_id}:v1'
    cache_key_by_invitee_id = 'invitation:invitee:{invitee_id}:v1'

    class Status(Enum):
        sent = 'S'
        accepted = 'A'

    class Kind(Enum):
        invite_investment = 1

    Kind.invite_investment.default_expire_days = datetime.timedelta(days=7300)
    Kind.invite_investment.award_package = invite_investment_package

    def __init__(self, id_, invitee_id, inviter_id, kind, status, expire_time):
        self.id_ = str(id_)
        self.invitee_id = str(invitee_id)
        self.inviter_id = str(inviter_id)
        self._kind = kind
        self._status = status
        self.expire_time = expire_time

    @cached_property
    def invitee(self):
        return Account.get(self.invitee_id)

    @cached_property
    def inviter(self):
        return Account.get(self.inviter_id)

    @cached_property
    def kind(self):
        return self.Kind(self._kind)

    @property
    def status(self):
        return self.Status(self._status)

    @status.setter
    def status(self, status):
        assert isinstance(status, self.Status)
        self._status = status.value

    @property
    def is_usable(self):
        """邀请是否有效."""
        return (
            self.status is self.Status.sent and
            self.expire_time > datetime.datetime.now()
        )

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, invitee_id, inviter_id, kind, status, expire_time'
               ' from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    @cache(cache_key_by_invitee_id)
    def get_by_invitee_id(cls, invitee_id):
        sql = 'select id from {.table_name} where invitee_id=%s'.format(cls)
        params = (invitee_id,)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    @cache(cache_key_by_inviter_id)
    def get_ids_by_inviter_id(cls, inviter_id):
        sql = 'select id from {.table_name} where inviter_id=%s'.format(cls)
        params = (inviter_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def get_multi_by_inviter_id(cls, inviter_id):
        ids = cls.get_ids_by_inviter_id(inviter_id)
        return cls.get_multi(ids)

    @classmethod
    def add(cls, inviter, invitee, kind):
        assert isinstance(kind, cls.Kind)
        assert isinstance(invitee, Account)
        assert isinstance(inviter, Account)

        expire_date = datetime.date.today() + kind.default_expire_days
        expire_time = datetime.datetime.combine(expire_date, datetime.time(23, 59, 59))

        sql = ('insert into {.table_name} (invitee_id, inviter_id, kind, status,'
               ' expire_time) values(%s, %s, %s, %s, %s)').format(cls)
        params = (invitee.id_, inviter.id_, kind.value, cls.Status.sent.value, expire_time)
        id_ = db.execute(sql, params)
        db.commit()
        cls.clear_cache(id_)
        cls.clear_cache_by_inviter_id(inviter.id_)
        cls.clear_cache_by_invitee_id(invitee.id_)
        return cls.get(id_)

    def accept(self):
        sql = 'update {.table_name} set status=%s where id=%s'.format(self)
        params = (self.Status.accepted.value, self.id_)
        db.execute(sql, params)
        db.commit()

        # 清缓存并刷新状态
        self.clear_cache(self.id_)
        self.clear_cache_by_inviter_id(self.inviter_id)
        self.clear_cache_by_invitee_id(self.invitee_id)
        self.status = self.Status.accepted

        # 发送完成邀请信号
        invitation_accepted.send(self)

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_inviter_id(cls, inviter_id):
        mc.delete(cls.cache_key_by_inviter_id.format(inviter_id=inviter_id))

    @classmethod
    def clear_cache_by_invitee_id(cls, invitee_id):
        mc.delete(cls.cache_key_by_invitee_id.format(invitee_id=invitee_id))


@xm_order_succeeded.connect
@zw_order_succeeded.connect
def on_order_succeeded(sender):
    invite = Invitation.get_by_invitee_id(sender.user.id_)
    if invite and invite.is_usable:
        rsyslog.send('\t'.join([sender.user.id_, sender.id_, invite.id_]),
                     tag='invitation_events')
        invite.accept()


def transform_digit(raw):
    """
    对raw做简单的异或运算
    """
    return int(raw) ^ MAGIC_SEED
