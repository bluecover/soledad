# coding: utf-8
import random
import os

from jupiter.workers import pool
from libs.logger.rsyslog import rsyslog

from core.models.welfare.package.kind import (invest_lottery_package_2_0,
                                              invest_lottery_package_1_8,
                                              invest_lottery_package_1_0,
                                              invest_lottery_package_0_8)
from core.models.welfare.package.package import distribute_welfare_gift
from core.models.invitation.invitation import Invitation
from core.models.hoard.signals import zw_order_succeeded, xm_order_succeeded
from core.models.user.account import Account
from .base import LotteryGift, UserLottery, UserLotteryRecord, UserLotteryNum


class EntitySender(object):

    def __init__(self, gift_id):
        self.gift_id = gift_id

    def send(self, user_id):
        pass


class PackageSender(object):

    def __init__(self, gift_id, package):
        self.gift_id = gift_id
        self.package = package

    def send(self, user_id):
        user = Account.get(user_id)
        distribute_welfare_gift(user, self.package)


@pool.async_worker('send_gift_worker')
def send_gift_worker(str_user_gift):
    str_log = ('SendGitWorkerPid: {0}').format(os.getpid())
    rsyslog.send(str_log, tag='send_gift_worker')
    user_id, gift_id = str_user_gift.split(':')
    gift_id = int(gift_id)
    UserLotteryRecord.add(user_id, gift_id)
    LotteryGiftMgr.send_gift(user_id, gift_id)


class LotteryGiftMgr(object):

    KEY_KINDLE = 1
    KEY_FIREWOOD_2_0 = 2
    KEY_FIREWOOD_1_8 = 3
    KEY_FIREWOOD_1_0 = 4
    KEY_FIREWOOD_0_8 = 5
    KEY_NONE = 0

    sender_map = {
        KEY_KINDLE: EntitySender(KEY_KINDLE),
        KEY_FIREWOOD_2_0: PackageSender(KEY_FIREWOOD_2_0, invest_lottery_package_2_0),
        KEY_FIREWOOD_1_8: PackageSender(KEY_FIREWOOD_1_8, invest_lottery_package_1_8),
        KEY_FIREWOOD_1_0: PackageSender(KEY_FIREWOOD_1_0, invest_lottery_package_1_0),
        KEY_FIREWOOD_0_8: PackageSender(KEY_FIREWOOD_0_8, invest_lottery_package_0_8)
    }

    @classmethod
    def send_gift(cls, user_id, gift_id):
        if gift_id not in cls.sender_map:
            return False
        sender = LotteryGiftMgr.sender_map[gift_id]
        sender.send(user_id)
        return True

    @classmethod
    def send_gift_async(cls, user_id, gift_id):
        lottery_log = 'User: {0}, gift_id: {1}'.format(user_id, gift_id)
        rsyslog.send(lottery_log, tag='LotteryGiftMgr')
        if gift_id == cls.KEY_NONE:
            return
        str_task = ('{0}:{1}').format(user_id, gift_id)
        send_gift_worker.produce(str_task)

    @classmethod
    def init_gift(cls):
        LotteryGift.add(cls.KEY_KINDLE, u'kindle大奖', 10)
        LotteryGift.add(cls.KEY_FIREWOOD_2_0, u'红包2.0元', 999999)
        LotteryGift.add(cls.KEY_FIREWOOD_1_8, u'红包1.8元', 999999)
        LotteryGift.add(cls.KEY_FIREWOOD_1_0, u'红包1.0元', 999999)
        LotteryGift.add(cls.KEY_FIREWOOD_0_8, u'红包0.8元', 999999)

    @classmethod
    def get_luck_key(cls, count):
        if count <= 3:
            odds = [0, 625, 3125, 5625, 8125]
        elif count <= 10:
            odds = [0, 833, 2500, 4166, 6666]
        elif count <= 29:
            odds = [2, 416, 833, 1666, 5000]
        else:
            odds = [1, 416, 833, 1666, 3333]
        num = random.randint(1, 10000)
        gift_list = [
            cls.KEY_KINDLE,
            cls.KEY_FIREWOOD_2_0,
            cls.KEY_FIREWOOD_1_8,
            cls.KEY_FIREWOOD_1_0,
            cls.KEY_FIREWOOD_0_8,
            cls.KEY_NONE
        ]
        for i in range(0, 5):
            if num <= odds[i]:
                return gift_list[i]
        return cls.KEY_NONE

    @classmethod
    def get_gift_id(cls, user_id):
        user_lottery = UserLottery.get(user_id)
        if not user_lottery.consume():
            return cls.KEY_NONE

        gift_id = cls.get_luck_key(user_lottery.used_num)
        if gift_id is not cls.KEY_NONE:
            gift = LotteryGift.get(gift_id)
            assert gift
            if not gift.consume():
                gift_id = cls.KEY_NONE

        return gift_id


@xm_order_succeeded.connect
@zw_order_succeeded.connect
def on_order_succeeded(sender):
    invite = Invitation.get_by_invitee_id(sender.user.id_)
    if invite and invite.is_usable:
        UserLotteryNum.add_by_invite_order(invite.id_)
