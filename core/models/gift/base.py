# coding: utf-8
import time
from datetime import datetime

from libs.db.store import db
from libs.cache import static_mc

from core.models.invitation.invitation import Invitation
from core.models.hoard.xinmi.order import XMOrder
from core.models.hoard.zhiwang.order import ZhiwangOrder


class RedisLock(object):
    DEFAULT_EXPIRES = 15

    def __init__(self, client, key):
        self.client = client
        self.key = key

    def is_locked(self):
        if self.client.get(self.key):
            return True
        return False

    def try_lock(self):
        if self.client.setnx(self.key, 1):
            self.client.expire(self.key, RedisLock.DEFAULT_EXPIRES)
            return True
        return False

    def lock_sync(self):
        while True:
            if self.try_lock():
                return True
            else:
                time.sleep(1)
        return False

    def unlock(self):
        self.client.delete(self)


class RedisNum(object):

    def __init__(self, client, key, val):
        self.client = client
        self.key = key
        self.client.set(self.key, val)

    def get(self):
        return self.client.get(self.key)

    def set(self, new_val):
        return self.client.set(self.key, new_val)

    def decr(self):
        return self.client.decr(self.key)

    def incr(self):
        return self.client.incr(self.key)

    def consume(self):
        if self.get() <= 0:
            return False
        if self.decr() < 0:
            return False
        return True


class UserLotteryRecord(object):

    class Entity(object):

        table_name = u'user_lottery_record'

        def __init__(self, id_, user_id, gift_id, creation_time):
            self.id_ = id_
            self.user_id = user_id
            self.gift_id = gift_id
            self.creation_time = creation_time

        @classmethod
        def add(cls, user_id, gift_id, creation_time):
            sql = (u'insert into {.table_name}'
                   u' (user_id, gift_id, creation_time)'
                   u' values (%s, %s, %s)').format(cls)
            params = (user_id, gift_id, creation_time)
            db.execute(sql, params)
            db.commit()

        @classmethod
        def gets_by_user(cls, user_id):
            sql = (u'select id, user_id, gift_id, creation_time'
                   u' from {.table_name} where user_id=%s').format(cls)
            params = (user_id, )
            rs = db.execute(sql, params)
            return [cls(*r) for r in rs]

    def __init__(self, entity):
        self.entity = entity

    @classmethod
    def add(cls, user_id, gift_id):
        now = datetime.now()
        return cls(cls.Entity.add(user_id, gift_id, now))


class LotteryGift(object):

    class Entity(object):

        table_name = u'lottery_gift'

        def __init__(self, id_, name, num, last, creation_time):
            self.id_ = id_
            self.name = name
            self.num = num
            self.last = last
            self.creation_time = creation_time

        @classmethod
        def add(cls, id_, name, num, last, creation_time):
            sql = (u'insert into {.table_name}'
                   u' (id, name, num, last, creation_time)'
                   u' values (%s, %s, %s, %s, %s)').format(cls)
            params = (id_, name, num, last, creation_time)
            db.execute(sql, params)
            db.commit()
            return cls(*params)

        @classmethod
        def get(cls, id_):
            sql = (u'select id, name, num, last, creation_time'
                   u' from {.table_name} where id=%s').format(cls)
            params = (id_, )
            rs = db.execute(sql, params)
            return cls(*(rs[0])) if rs else None

        @classmethod
        def get_all(cls):
            sql = (u'select id, name, num, last, creation_time'
                   u' from {.table_name}').format(cls)
            rs = db.execute(sql)
            return [cls(*r) for r in rs]

        def commit(self):
            sql = (u'update {.table_name} set name=%s, num=%s, last=%s'
                   u' where id=%s').format(LotteryGift.Entity)
            params = (self.name, self.num, self.last, self.id_)
            db.execute(sql, params)
            db.commit()

    obj_cache = {}

    def __init__(self, entity):
        self.entity = entity
        LotteryGift.obj_cache[self.entity.id_] = self

        lock_key = u'solar:LotteryGift:lock:{0}'.format(entity.id_)
        self.lock = RedisLock(static_mc, lock_key)

        last_key = u'solar:LotteryGift:last:{0}'.format(entity.id_)
        self.last_num = RedisNum(static_mc, last_key, entity.last)

    @classmethod
    def get(cls, gift_id):
        if gift_id in cls.obj_cache:
            return cls.obj_cache[gift_id]
        entity = cls.Entity.get(gift_id)
        if entity:
            return cls(entity)
        else:
            return None

    @classmethod
    def add(cls, id_, name, num):
        res = cls.get(id_)
        if not res:
            now = datetime.now()
            entity = cls.Entity.add(id_, name, num, num, now)
            res = cls(entity)
        return res

    @property
    def last(self):
        return self.last_num.get()

    @last.setter
    def last(self, new_value):
        self.last_num.set(new_value)

    def consume(self):
        if not self.last_num.consume():
            return False
        self.entity.last = self.last
        self.entity.commit()
        return True


class UserLottery(object):

    class Entity(object):

        table_name = u'user_lottery'

        def __init__(self, user_id, remain_num, used_num, creation_time):
            self.user_id = user_id
            self.remain_num = remain_num
            self.used_num = used_num
            self.creation_time = creation_time

        @classmethod
        def get(cls, user_id):
            sql = (u'select user_id, remain_num, used_num, creation_time'
                   u' from {.table_name} where user_id=%s').format(cls)
            params = (user_id, )
            rs = db.execute(sql, params)
            return cls(*(rs[0])) if rs else None

        @classmethod
        def add(cls, user_id, remain_num, used_num, creation_time):
            sql = (u'insert into {.table_name}'
                   u' (user_id, remain_num, used_num, creation_time)'
                   u' values (%s, %s, %s, %s)').format(cls)
            params = (user_id, remain_num, used_num, creation_time)
            db.execute(sql, params)
            db.commit()
            return cls(*params)

        def commit(self):
            sql = (u'update {.table_name} set remain_num=%s, used_num=%s'
                   u' where user_id=%s').format(UserLottery.Entity)
            params = (self.remain_num, self.used_num, self.user_id)
            db.execute(sql, params)
            db.commit()

    def __init__(self, entity):
        self.entity = entity

    @classmethod
    def get_user_lottery_num(cls, user_id):
        invs = Invitation.get_multi_by_inviter_id(user_id)
        inv_user_num = len(invs)
        inv_user_have_order_num = 0
        inv_user_all_order_num = 0
        for inv in invs:
            zw_order_num = len(ZhiwangOrder.get_multi_by_user(inv.invitee_id))
            xm_order_num = len(XMOrder.get_multi_by_user(inv.invitee_id))
            inv_order_num = zw_order_num + xm_order_num
            inv_user_all_order_num += inv_order_num
            if inv_order_num:
                inv_user_have_order_num += 1

        lottery_num = 3 + inv_user_num*3 + inv_user_all_order_num*5
        return lottery_num

    @classmethod
    def get(cls, user_id):
        entity = cls.Entity.get(user_id)
        if not entity:
            remain_num = cls.get_user_lottery_num(user_id)
            now = datetime.now()
            entity = cls.Entity.add(user_id, remain_num, 0, now)
            UserLotteryNum.add(user_id, UserLotteryNum.TYPE_INIT, remain_num)
        return cls(entity)

    @property
    def remain_num(self):
        return self.entity.remain_num

    @remain_num.setter
    def remain_num(self, new_value):
        self.entity.remain_num = new_value
        self.entity.commit()

    @property
    def used_num(self):
        return self.entity.used_num

    def add_remain_num(self, num):
        self.remain_num += num

    def consume(self):
        if self.entity.remain_num <= 0:
            return False
        self.entity.remain_num -= 1
        self.entity.used_num += 1
        self.entity.commit()
        return True


class UserLotteryNum(object):

    TYPE_INIT = 0
    TYPE_SHARE = 1
    TYPE_INVITE = 2
    TYPE_INVITE_ORDER = 3

    class Entity(object):

        table_name = 'user_lottery_num'

        def __init__(self, id_, user_id, get_type, lottery_num, creation_time):
            self.id_ = id_
            self.user_id = user_id
            self.get_type = get_type
            self.lottery_num = lottery_num
            self.creation_time = creation_time

        @classmethod
        def add(cls, user_id, get_type, lottery_num, creation_time):
            sql = ('insert into {.table_name}'
                   ' (user_id, get_type, lottery_num, creation_time)'
                   ' values (%s, %s, %s, %s)').format(cls)
            params = (user_id, get_type, lottery_num, creation_time)
            db.execute(sql, params)
            db.commit()

        @classmethod
        def get_by_type(cls, user_id, get_type):
            sql = ('select id, user_id, get_type, lottery_num, creation_time'
                   ' from {.table_name} where user_id=%s and get_type=%s').format(cls)
            params = (user_id, get_type)
            rs = db.execute(sql, params)
            return [cls(*r) for r in rs]

    @classmethod
    def add(cls, user_id, get_type, lottery_num):
        now = datetime.now()
        cls.Entity.add(user_id, get_type, lottery_num, now)

    @classmethod
    def add_by_share(cls, user_id):
        today_share = False
        now_date = datetime.now().date()
        for entity in cls.Entity.get_by_type(user_id, cls.TYPE_SHARE):
            if entity.creation_time.date() == now_date:
                today_share = True
                break
        if today_share:
            return
        user_lottery = UserLottery.get(user_id)
        user_lottery.add_remain_num(1)
        cls.add(user_id, cls.TYPE_SHARE, 1)

    @classmethod
    def add_by_invite(cls, user_id):
        user_lottery = UserLottery.get(user_id)
        user_lottery.add_remain_num(3)
        cls.add(user_id, cls.TYPE_INVITE, 3)

    @classmethod
    def add_by_invite_order(cls, user_id):
        user_lottery = UserLottery.get(user_id)
        user_lottery.add_remain_num(5)
        cls.add(user_id, cls.TYPE_INVITE_ORDER, 5)
