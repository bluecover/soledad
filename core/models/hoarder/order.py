# coding: utf-8

from datetime import datetime, timedelta, time
from decimal import Decimal
from enum import Enum

from werkzeug.utils import cached_property
from sxblib.consts import OrderStatus, RedeemStatus

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.utils import round_half_up
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.profile.bankcard import BankCard
from core.models.profile.identity import has_real_identity
from core.models.user.account import Account
from jupiter.workers.hoarder import (
    hoarder_payment_tracking, hoarder_asset_fetching,  hoarder_order_use_gift_tracking)

from .account import Account as HoarderAccount
from .bankcard_binding import BankcardBinding
from .product import Product as HoarderProduct
from .signal import hoarder_order_succeeded, hoarder_order_failed, hoarder_asset_redeemed
from .errors import (SequenceError, NotFoundEntityError, InvalidIdentityError, UnboundAccountError,
                     SuspendedError, SoldOutError, OffShelfError, OutOfRangeError,
                     UnsupportedStatusError)
from ..hoard.common import ProfitPeriod


class HoarderOrder(PropsMixin):

    table_name = 'hoarder_order'
    cache_key = 'hoarder:order:{id_}'
    cache_ids_by_user_key = 'hoarder:order:user:{user_id}:ids'
    raw_product_sold_amount_cache_key = 'hoarder:order:sold_amount:raw_product:{product_id}:'
    product_daily_sold_amount_cache_key = 'hoarder:order:daily_sold_amount:product:{product_id}:'
    order_amount_cache_key_by_user = 'hoarder:order:amount:user:{user_id}'

    #: 资产交割后支付金额
    repay_amount = PropsItem('repay_amount', default='')
    #: 加急手续费
    exp_sell_fee = PropsItem('exp_sell_fee', default='')
    #: 固定手续费
    fixed_service_fee = PropsItem('fixed_service_fee', default='')
    #: 赎回手续费
    service_fee = PropsItem('service_fee', default='')

    class Direction(Enum):
        #: 存入
        save = 'S'
        #: 赎回
        redeem = 'R'

    class Status(Enum):
        #: 本地购买初始状态
        unpaid = 'U'
        #: 本地支付前状态
        committed = 'C'
        #: 远端暂时搁置状态
        shelved = 'V'
        #: 远端正在支付状态
        paying = 'P'
        #: 远端已成功状态
        success = 'S'
        #: 远端已失败状态
        failure = 'F'

        #: 远端申请赎回状态
        applyed = 'A'
        #: 远端正在赎回状态
        redeeming = 'R'
        #: 远端待回款状态
        waiting_back = 'W'
        #: 远端回款中状态
        backing = 'B'
        #: 远端回款结束
        backed = 'D'

    #: 状态显示文案
    Status.unpaid.display_text = u'未支付'
    Status.committed.display_text = u'未支付'
    Status.shelved.display_text = u'处理中'
    Status.paying.display_text = u'处理中'
    Status.applyed.display_text = u'转出中'
    Status.redeeming.display_text = u'转出中'
    Status.waiting_back.display_text = u'待回款'
    Status.backing.display_text = u'回款中'
    Status.backed.display_text = u'已转出'
    Status.success.display_text = u'已存入'
    Status.failure.display_text = u'订单失败'

    # 状态迁移顺序
    Status.unpaid.sequence = 0
    Status.committed.sequence = 1
    Status.shelved.sequence = 2
    Status.paying.sequence = 3
    Status.applyed.sequence = 3
    Status.redeeming.sequence = 4
    Status.waiting_back.sequence = 5
    Status.backing.sequence = 6
    Status.backed.sequence = 7
    Status.success.sequence = 7
    Status.failure.sequence = 7

    #: 远端与本地状态映射
    MUTUAL_STATUS_MAP = {
        OrderStatus.waiting: Status.paying,
        OrderStatus.paying: Status.shelved,
        OrderStatus.payed: Status.success,
        OrderStatus.applying: Status.success,
        OrderStatus.applyed: Status.success,
        OrderStatus.finished: Status.success,
        OrderStatus.auto_cancel: Status.failure,
        OrderStatus.user_cancel: Status.failure,
    }
    MUTUAL_REDEEM_MAP = {
        RedeemStatus.applyed: Status.applyed,
        RedeemStatus.redeeming: Status.redeeming,
        RedeemStatus.waiting_back: Status.waiting_back,
        RedeemStatus.backing: Status.backing,
        RedeemStatus.backed: Status.backed,
    }

    #: 状态和颜色映射
    ORDER_STATUS_COLOR_MAP = {
        u'处理中': '#9B9B9B',
        u'已存入': '#6192B3',
        u'转出中': '#F5A623',
        u'回款中': '#F5A623',
        u'错误': '#D42C41',
        u'已转出': '#6C9F31',
        u'未知状态': '#9B9B9B',
    }

    def __init__(self, id_, user_id, product_id, bankcard_id, amount, pay_amount,
                 expect_interest, order_code, pay_code, direction, status, remote_status,
                 start_time, due_time, update_time, creation_time):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.product_id = str(product_id)
        self.bankcard_id = str(bankcard_id)
        self.amount = amount
        self.pay_amount = pay_amount
        self.expect_interest = expect_interest
        self.order_code = order_code if order_code else None
        self.pay_code = pay_code if pay_code else None
        self._direction = direction
        self._status = status
        self.remote_status = remote_status
        self.start_time = start_time
        self.due_time = due_time
        self.update_time = update_time
        self.creation_time = creation_time

    def __str__(self):
        return '<HoarderOrder {.id_}>'.format(self)

    def get_db(self):
        return 'hoarder'

    def get_uuid(self):
        return 'hoarder:order:{.id_}'.format(self)

    @cached_property
    def owner(self):
        return Account.get(self.user_id)

    @cached_property
    def direction(self):
        return self.Direction(self._direction)

    @cached_property
    def product(self):
        return HoarderProduct.get(self.product_id)

    @cached_property
    def asset(self):
        from .asset import Asset
        return Asset.get_by_order_code(self.order_code)

    @cached_property
    def profit_period(self):
        return ProfitPeriod((self.due_date - self.start_date).days, 'day')

    @property
    def profit_hikes(self):
        return []

    @property
    def coupon(self):
        if self.coupon_record:
            return self.coupon_record.coupon

    @property
    def coupon_record(self):
        from core.models.welfare import CouponUsageRecord
        return CouponUsageRecord.get_by_partner_order(self.product.vendor_id, self.id_)

    @property
    def woods_burning(self):
        from core.models.welfare import FirewoodBurning
        return FirewoodBurning.get_by_provider_order(self.product.vendor_id, self.id_)

    @property
    def display_status(self):
        return self.status.display_text

    @property
    def computed_expect_interest(self):
        return (self.actual_annual_rate * self.amount *
                self.profit_period.value / 100 / 365)

    @property
    def original_annual_rate(self):
        return self.product.annual_rate

    @property
    def actual_annual_rate(self):
        return self.original_annual_rate

    @property
    def bankcard(self):
        return BankCard.get(self.bankcard_id)

    @property
    def status(self):
        return self.Status(self._status)

    @property
    def status_color(self):
        return self.ORDER_STATUS_COLOR_MAP.get(self.display_status)

    @status.setter
    def status(self, new_status):
        self.check_before_setting_status(new_status)

        sql = 'update {.table_name} set status=%s, update_time=%s where id=%s;'.format(self)
        params = (new_status.value, datetime.now(), self.id_)
        db.execute(sql, params)

        db.commit()

        self.clear_cache(self.id_)
        self.clear_cache_by_user(self.user_id)

        self.act_after_setting_status(new_status)

    def update_by_remote_status(self, remote_status):
        """ remote_status 为OrderStatus 或 RedeemStatus"""
        local_status = self.get_local_status_by_remote_status(remote_status)
        if not local_status:
            raise UnsupportedStatusError(type(remote_status))
        self.check_before_setting_status(local_status)
        sql = ('update {.table_name} set status=%s, remote_status=%s, update_time=%s'
               ' where id=%s;').format(self)
        params = (local_status.value, remote_status.value, datetime.now(), self.id_)
        db.execute(sql, params)

        db.commit()

        self.clear_cache(self.id_)
        self.clear_cache_by_user(self.user_id)

        self.act_after_setting_status(local_status)

    def get_local_status_by_remote_status(self, remote_status):
        """ remote_status 为OrderStatus 或 RedeemStatus"""
        if isinstance(remote_status, OrderStatus):
            return self.MUTUAL_STATUS_MAP.get(remote_status)
        elif isinstance(remote_status, RedeemStatus):
            return self.MUTUAL_REDEEM_MAP.get(remote_status)

    def check_before_setting_status(self, new_status):
        if not isinstance(new_status, self.Status):
            raise ValueError(u'错误的状态类型：%r' % new_status)

        # 不可反向跳转状态
        if new_status.sequence < self.status.sequence:
            raise SequenceError()

    def act_after_setting_status(self, new_status):

        old_status = self._status
        # 本身已是成功状态则直接舍弃。
        if self.Status(old_status) is self.Status.success:
            return
        self._status = new_status.value
        rsyslog.send('order %s status changes from %s to %s' % (
            self.id_, old_status, self._status), tag='hoarder_order_status_change')

        if new_status in [self.Status.shelved, self.Status.paying]:
            # 当支付未完成时将订单放入状态跟踪MQ
            self.track_for_payment()
            return

        if new_status is self.Status.success:
            # 当支付成功时将订单放入获取资产MQ并发送成功广播信号
            rsyslog.send('fetch asset for order %s' % self.id_,
                         tag='hoarder_fetch_asset')
            hoarder_asset_fetching.produce(self.id_)
            hoarder_order_succeeded.send(self)
            return

        if new_status is self.Status.failure:
            # 当支付失败时发送失败广播信号
            hoarder_order_failed.send(self)

    @classmethod
    def check_before_adding(cls, vendor, user_id, bankcard_id, product_id, amount):
        if not vendor:
            raise NotFoundEntityError(vendor.id_, Account)

        product = HoarderProduct.get(product_id)
        local_account = Account.get(user_id)
        bankcard = BankCard.get(bankcard_id)
        hoarder_account = HoarderAccount.get(vendor.id_, user_id)

        if not local_account:
            raise NotFoundEntityError(user_id, Account)
        if not bankcard:
            raise NotFoundEntityError(bankcard_id, BankCard)
        if not hoarder_account:
            raise UnboundAccountError(user_id)

        if not has_real_identity(local_account):
            raise InvalidIdentityError()

        # 产品是否处于可售状态
        if product.is_sold_out:
            raise SoldOutError(product_id)
        # 产品是否处于正常销售状态
        if product.is_taken_down:
            raise SuspendedError(product_id)
        # 产品是否处于在售状态
        if not product.is_on_sale:
            raise OffShelfError(product_id)

        # checks the product amount limit
        if not isinstance(amount, Decimal):
            raise TypeError('order amount must be decimal')

        amount_range = (product.min_amount, product.max_amount)
        amount_check = [amount.is_nan(),
                        amount < 0,
                        amount < amount_range[0],
                        amount > amount_range[1]]
        if any(amount_check):
            raise OutOfRangeError(amount, amount_range)

    @classmethod
    def add(cls, user_id, product_id, bankcard_id, amount, order_code, direction,
            status, remote_status, expect_interest=None, pay_amount=None,
            pay_code=None, repay_amount=None, redeem_pay_amount=None, exp_sell_fee=None,
            fixed_service_fee=None, service_fee=None, start_time=None, due_time=None):

        assert isinstance(status, cls.Status)

        sql = (
            'insert into {.table_name} (user_id, product_id, bankcard_id, amount, pay_amount,'
            'expect_interest, order_code, pay_code, direction, status, remote_status, start_time,'
            ' due_time, update_time, creation_time) '
            'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)').format(cls)
        params = (
            user_id, product_id, bankcard_id, amount, pay_amount, expect_interest, order_code,
            pay_code, direction.value, status.value, remote_status.value, start_time, due_time,
            datetime.now(), datetime.now())

        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_user(user_id)

        instance = cls.get(id_)
        instance.update_props_items({
            'repay_amount': repay_amount,
            'exp_sell_fee': exp_sell_fee,
            'service_fee': service_fee,
            'fixed_service_fee': fixed_service_fee})
        return instance

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = (
            'select id, user_id, product_id, bankcard_id, amount, pay_amount, expect_interest, '
            'order_code, pay_code, direction, status, remote_status, start_time, due_time, '
            'update_time, creation_time '
            'from {.table_name} where id=%s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        return cls(*rs[0]) if rs else None

    @classmethod
    @cache(cache_ids_by_user_key)
    def get_ids_by_user(cls, user_id):
        sql = ('select id from {.table_name} where user_id=%s'
               ' order by creation_time desc').format(cls)
        params = (user_id, )
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_user(cls, user_id):
        ids = cls.get_ids_by_user(user_id)
        return cls.get_multi(ids)

    @classmethod
    def gets_by_user_with_page(cls, user_id, offset, count):
        """分页获取订单信息 过滤掉失败和未支付订单"""
        sql = ('select id from {.table_name} where user_id=%s and not status=%s and not status=%s'
               'order by creation_time desc limit %s, %s').format(cls)
        params = (user_id, cls.Status.unpaid.value, cls.Status.failure.value, offset, count,)
        rs = db.execute(sql, params)
        return cls.get_multi([str(r[0]) for r in rs]) if rs else []

    @classmethod
    def get_redeemed_amount_by_user_today(cls, user_id):
        sql = ('select sum(amount) from {.table_name} where user_id=%s and direction=%s'
               ' and creation_time > %s').format(cls)
        params = (user_id, cls.Direction.redeem.value, datetime.today().date())
        rs = db.execute(sql, params)
        return round_half_up(rs[0][0], 2) if rs and rs[0] and rs[0][0] else Decimal('0.00')

    @classmethod
    def get_ids_by_bankcard(cls, bankcard_id):
        sql = 'select id from {.table_name} where bankcard_id=%s'.format(cls)
        params = (bankcard_id,)
        rs = db.execute(sql, params)
        return [str(r[0]) for r in rs]

    @classmethod
    def get_multi_by_bankcard(cls, bankcard_id):
        ids = cls.get_ids_by_bankcard(bankcard_id)
        return cls.get_multi(ids)

    @classmethod
    def is_bankcard_swiped(cls, bankcard):
        assert isinstance(bankcard, BankCard)

        return bool(len([o for o in cls.get_multi_by_bankcard(
            bankcard.id_) if o.status is cls.Status.success]))

    @classmethod
    @cache(raw_product_sold_amount_cache_key)
    def get_raw_product_sold_amount(cls, raw_product_id):
        sql = (
            'select sum(amount) from {.table_name} '
            'where product_id=%s and (status=%s or status=%s)').format(cls)
        params = (raw_product_id, cls.Status.paying.value, cls.Status.success.value)
        rs = db.execute(sql, params)
        return rs[0][0] or 0

    @classmethod
    @cache(product_daily_sold_amount_cache_key)
    def get_product_daily_sold_amount_by_now(cls, product_id):
        sql = (
            'select sum(amount) from {.table_name}'
            ' where product_id=%s and (status=%s or status=%s)'
            ' and creation_time between %s and %s').format(cls)
        end_time = datetime.now()
        start_time = datetime.combine(end_time, time.min)
        params = (
            product_id, cls.Status.paying.value, cls.Status.success.value, start_time, end_time)
        rs = db.execute(sql, params)
        return rs[0][0] or 0

    @classmethod
    def get_by_order_code(cls, order_code):
        sql = 'select id from {.table_name} where order_code=%s'.format(cls)
        params = (order_code,)
        rs = db.execute(sql, params)
        return cls.get(rs[0][0]) if rs else None

    @classmethod
    @cache(order_amount_cache_key_by_user)
    def get_order_amount_by_user(cls, user_id):
        sql = (
            'select count(id) from {.table_name} '
            'where user_id=%s and (status=%s or status=%s)').format(cls)
        params = (user_id, cls.Status.paying.value, cls.Status.success.value)
        rs = db.execute(sql, params)
        return rs[0][0]

    @classmethod
    def get_multi(cls, ids):
        return [cls.get(id_) for id_ in ids]

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(**locals()))

    @classmethod
    def clear_cache_by_user(cls, user_id):
        mc.delete(cls.cache_ids_by_user_key.format(**locals()))
        mc.delete(cls.order_amount_cache_key_by_user.format(**locals()))

    @classmethod
    def clear_local_sold_amount_cache(cls, product_id):
        mc.delete(cls.raw_product_sold_amount_cache_key.format(**locals()))

    def track_for_payment(self):
        hoarder_payment_tracking.produce(self.id_)

    def lock_bonus(self):
        """对订单礼券、抵扣金进行加锁冻结（发生在订单提交支付前）"""
        from core.models.welfare import FirewoodWorkflow, FirewoodBurning

        if self.woods_burning:
            flow = FirewoodWorkflow(self.user_id)
            flow.pick(self.woods_burning, tags=[FirewoodBurning.Kind.deduction.name])

        if self.coupon:
            self.coupon.shell_out(self.product, self.amount)

    def confirm_bonus(self):
        """确认礼券、抵扣金被使用（发生在订单已经被告知成功）"""
        from core.models.welfare import FirewoodWorkflow
        if self.status is not self.Status.success:
            raise ValueError('order %s payment has not succeeded' % self.id_)

        if self.woods_burning:
            FirewoodWorkflow(self.user_id).burn(self.woods_burning)

        if self.coupon:
            self.coupon.confirm_consumption()
            self.coupon_record.commit()
            # TODO: 增加折扣判断
            # for hike in self.profit_hikes:
            #     hike.achieve()

    def unlock_bonus(self):
        """释放礼券、抵扣金（发生在订单已经被告知失败）"""
        from core.models.welfare import FirewoodWorkflow
        if self.status not in [self.Status.paying, self.Status.committed, self.Status.failure]:
            raise ValueError('order %s payment has not terminated' % self.id_)

        if self.woods_burning:
            FirewoodWorkflow(self.user_id).release(self.woods_burning)

        if self.coupon:
            self.coupon.put_back_wallet()

        for hike in self.profit_hikes:
            hike.renew()


@hoarder_order_succeeded.connect
def on_order_succeeded(sender):
    order = HoarderOrder.get(sender.id_)

    # 清除产品销售额缓存
    HoarderOrder.clear_local_sold_amount_cache(order.product_id)

    # 确认优惠已被消费使用
    # order.confirm_bonus()

    # 增加或更新银行卡信息
    BankcardBinding.add_or_update(order.user_id, order.bankcard_id, order.product.vendor.id_)

    # 记录成功订单日志
    rsyslog.send('\t'.join([
        order.id_, order.product_id, order.user_id, order.creation_time.isoformat(),
        order.order_code, order.bankcard_id, str(round(order.amount, 2))]),
        tag='hoarder_order_succeeded')

    # 发送订单成功短信
    send_order_success_sms(order)

    if order.product.kind is HoarderProduct.Kind.child:
        hoarder_order_use_gift_tracking.produce(order.id_)


def send_order_success_sms(order):
    '''随心宝交易成功短信'''
    from core.models.sms import ShortMessage
    from core.models.sms.kind import savings_order_success_sms_sxb

    str_time = order.creation_time.strftime('%Y年%m月%d日%H点%M分').decode('utf-8')
    str_amount = (u'%.2f') % (order.amount)
    value_date = order.product.value_date
    str_value_date = value_date.strftime('%Y年%m月%d日').decode('utf-8')
    earnings_day = value_date + timedelta(days=1)
    str_earnings_day = earnings_day.strftime('%Y年%m月%d日').decode('utf-8')

    sms = ShortMessage.create(order.owner.mobile, savings_order_success_sms_sxb,
                              order.user_id, time=str_time, amount=str_amount,
                              value_date=str_value_date,
                              earnings_day=str_earnings_day)
    sms.send()


@hoarder_order_failed.connect
def on_order_failure(sender):
    order = HoarderOrder.get(sender.id_)

    # 清除产品销售额缓存
    HoarderOrder.clear_local_sold_amount_cache(order.product_id)

    # 解除礼券、抵扣金锁
    order.unlock_bonus()

    # 订单失败时再次同步资产状态
    hoarder_payment_tracking.produce(sender.id_)


@hoarder_asset_redeemed.connect
def on_order_redeem_success(redeem_order):
    send_redeem_success_sms(redeem_order)


def send_redeem_success_sms(order):
    '''随心宝赎回申请提交成功短信'''
    from core.models.sms import ShortMessage
    from core.models.sms.kind import savings_redeem_success_sms_sxb

    str_time = order.creation_time.strftime('%Y年%m月%d日%H点%M分').decode('utf-8')
    str_amount = (u'%.2f') % (order.amount)
    bankcard = order.bankcard
    sms = ShortMessage.create(order.owner.mobile, savings_redeem_success_sms_sxb,
                              order.user_id, time=str_time, amount=str_amount,
                              bankname=bankcard.bank.name,
                              bankno=bankcard.tail_card_number)
    sms.send()
