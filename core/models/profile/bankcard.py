# coding: utf-8

from hashlib import sha1
from operator import attrgetter
from warnings import warn

from more_itertools import first
from enum import Enum
from gb2260 import Division
from stdnum import luhn
from stdnum.exceptions import InvalidFormat, InvalidChecksum
from envcfg.json.solar import DEBUG

from libs.db.store import db
from libs.cache import mc, cache
from libs.logger.rsyslog import rsyslog
from core.models.base import EntityModel
from core.models.mixin.props import PropsMixin, PropsItem
from core.models.user.account import Account
from core.models.bank import bank_collection
from .signals import before_deleting_bankcard, bankcard_updated


class BankCard(EntityModel, PropsMixin):
    """The information of bank cards."""

    class Meta:
        repr_attr_names = ['display_card_number', 'display_mobile_phone']

    class Status(Enum):
        active = 'A'
        # inactive = 'I'
        discarded = 'D'

    # See also http://www.stevemorse.org/ssn/List_of_Bank_Identification_Numbers.html
    # above link is updated, so we should update the following card number ranges
    CHINA_DEBIT_IIN_LIST = (
        '62',      # UnionPay
        '4213',    # China Minsheng Bank VISA Debit Card
        '434061',  # China Construction Bank Debit Card
        '434062',  # China Construction Bank Debit Card
        '436742',  # China Construction Bank Debit Card
        '442729',  # China CITIC Bank Gold Visa Debit Card
        '442730',  # China CITIC Bank Platinum Visa Debit Card
        '456351',  # Bank of China Debit card (China UnionPay)
        '4682',    # China Merchant Bank Visa Debit Card
        '524094',  # China Construction Bank Master Debit Card
        '601382',  # Bank of China Unionpay Debit card (GreatWall Debit Card)
        '602969',  # Bank of Beijing Debit Card Visa Interlink/China UnionPay CNY
        '603367',  # Bank of Hangzhou Debit Card, China UnionPay
        '95588',   # CBBC Debit Card (Mudan Lingtong card)
    )

    table_name = 'hoard_bankcard'
    cache_key = 'profile:bankcard:{id_}:v2'
    cache_key_by_user_id = 'profile:bankcard:user:{user_id}:id_list'

    #: the mobile phone number
    mobile_phone = PropsItem('mobile_phone', default='', secret=True)
    #: the bank card number for withdrawing
    card_number = PropsItem('card_number', default='', secret=True)
    #: the back id for withdrawing
    bank_id = PropsItem('bank_id', default='', secret=True)
    #: the local bank name for withdrawing
    local_bank_name = PropsItem('local_bank_name', default='', secret=True)
    #: the bank city id for withdrawing
    city_id = PropsItem('city_id', default='', secret=True)
    #: the bank province id for withdrawing
    province_id = PropsItem('province_id', default='', secret=True)
    #: default card for pay
    is_default = PropsItem('is_default', default=False)

    #: the extra bank information (obtained from the Yixin API)
    extra_info = PropsItem('extra_info', secret=True)

    def __init__(self, id_, user_id, card_number_sha1, bank_id_sha1,
                 creation_time, status):
        self.id_ = str(id_)
        self.user_id = str(user_id)
        self.card_number_sha1 = card_number_sha1
        self.bank_id_sha1 = bank_id_sha1
        self.creation_time = creation_time
        self._status = status

    def get_uuid(self):
        return 'user:bankcard:{id_}'.format(id_=self.id_)

    def get_db(self):
        return 'hoard'

    @property
    def status(self):
        return self.Status(self._status)

    @property
    def bank(self):
        return bank_collection.get_bank(self.bank_id)

    @property
    def province(self):
        return Division.search(self.province_id)

    @property
    def prefecture(self):
        return Division.search(self.city_id)

    @property
    def bank_name(self):
        warn('bankcard.bank_name -> bankcard.bank.name', DeprecationWarning)
        return self.bank.name

    @property
    def tail_card_number(self):
        return self.card_number[-4:]

    @property
    def display_card_number(self):
        return '{0}****{1}'.format(self.card_number[:2], self.tail_card_number)

    @property
    def display_mobile_phone(self):
        return '{0}****{1}'.format(self.mobile_phone[:3], self.mobile_phone[-4:])

    @property
    def is_active(self):
        return self.status is self.Status.active

    @classmethod
    @cache(cache_key)
    def get(cls, id_):
        sql = ('select id, user_id, card_number_sha1, bank_id_sha1,'
               ' creation_time, status '
               'from {.table_name} where id = %s').format(cls)
        params = (id_,)
        rs = db.execute(sql, params)
        if rs:
            return cls(*rs[0])

    @classmethod
    def get_by_card_number(cls, card_number):
        sql = ('select id from {.table_name} '
               'where card_number_sha1 = %s').format(cls)
        params = (calculate_checksum(card_number),)
        rs = db.execute(sql, params)
        if rs:
            return cls.get(rs[0][0])

    @classmethod
    def get_multi(cls, id_list):
        return list(map(cls.get, id_list))

    @classmethod
    def get_by_user(cls, user_id):
        warn(DeprecationWarning('use get_multi_by_user'))
        return cls.get_multi_by_user(user_id)

    @classmethod
    def get_multi_by_user(cls, user_id):
        return cls.get_multi(cls.get_id_list_by_user(user_id))

    @classmethod
    @cache(cache_key_by_user_id)
    def get_id_list_by_user(cls, user_id):
        sql = 'select id from {.table_name} where user_id = %s'.format(cls)
        params = (user_id,)
        rs = db.execute(sql, params)
        return [r[0] for r in rs]

    @classmethod
    def check_existing(cls, field, value, user_id=None, status=Status.active):
        if field not in ('card_number', 'bank_id'):
            raise ValueError

        if user_id is None:
            condition = 'where status = %s and {0}_sha1 = %s'.format(field)
            params = (status.value, calculate_checksum(value))
        else:
            condition = ('where status = %s and {0}_sha1 = %s'
                         ' and user_id = %s').format(field)
            params = (status.value, calculate_checksum(value), user_id)

        sql = 'select count(*) from {0.table_name} {1}'.format(cls, condition)
        rs = db.execute(sql, params)

        return int(rs[0][0]) > 0

    @classmethod
    def add(cls, user_id, mobile_phone, card_number, bank_id, city_id,
            province_id, local_bank_name, is_default):
        card_number = cls.validate_card_number(card_number)

        if not Account.get(user_id):
            raise ValueError('invalid user %r' % user_id)

        if cls.check_existing('card_number', card_number):
            raise CardConflictError()

        if cls.check_existing('bank_id', bank_id, user_id=user_id):
            raise BankConflictError()

        if cls.check_existing('card_number', card_number, cls.Status.discarded):
            instance = cls.get_by_card_number(card_number)
            instance.activate()
            return instance

        sql = ('insert into {.table_name} (user_id, card_number_sha1,'
               ' bank_id_sha1, status) values (%s, %s, %s, %s)').format(cls)
        params = (
            user_id,
            calculate_checksum(card_number),
            calculate_checksum(bank_id),
            cls.Status.active.value,
        )

        id_ = db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_user_id(user_id)

        instance = cls.get(id_)
        instance.update_props_items({
            'mobile_phone': mobile_phone,
            'card_number': card_number,
            'bank_id': bank_id,
            'city_id': city_id,
            'province_id': province_id,
            'local_bank_name': local_bank_name,
            'is_default': is_default,
        })
        return instance

    def update(self, mobile_phone, bank_id, city_id, province_id,
               local_bank_name, is_default):
        self.is_default = is_default
        changed = [field_name for field_name, field_changed in [
            ('mobile_phone', self.mobile_phone != mobile_phone),
            ('bank_id', self.bank_id != bank_id),
            ('city_id', self.city_id != city_id),
            ('province_id', self.province_id != province_id),
            ('local_bank_name', self.local_bank_name != local_bank_name),
        ] if field_changed]
        if changed:
            sql = ('update {.table_name} set bank_id_sha1 = %s '
                   'where id = %s').format(self)
            params = (calculate_checksum(bank_id), self.id_)
            db.execute(sql, params)

            self.update_props_items({
                'mobile_phone': mobile_phone,
                'card_number': self.card_number,
                'bank_id': bank_id,
                'city_id': city_id,
                'province_id': province_id,
                'local_bank_name': local_bank_name,
                'is_default': self.is_default,
            })
            db.commit()
            bankcard_updated.send(self, changed_fields=changed)

        return changed

    def discard(self):
        self._transfer_status(self.Status.discarded)

    def activate(self):
        self._transfer_status(self.Status.active)

    def _transfer_status(self, new_status):
        self._status = new_status.value

        sql = 'update {.table_name} set status = %s where id = %s'.format(self)
        params = (self.status.value, self.id_)

        db.execute(sql, params)
        db.commit()
        self.clear_cache(self.id_)

    @classmethod
    def delete_by_card_number(cls, card_number, user_id):
        condition = 'where card_number_sha1 = %s and user_id = %s'
        params = (calculate_checksum(card_number), user_id)

        sql = 'select id from {0.table_name} {1}'.format(cls, condition)
        rs = db.execute(sql, params)
        if not rs:
            return

        id_ = rs[0][0]

        results = before_deleting_bankcard.send(
            cls, bankcard_id=id_, user_id=user_id)
        for subscriber, return_value in results:
            if return_value is False:
                raise CardDeletingError(
                    'deleting operation denied by %r' % subscriber)

        sql = 'delete from {0.table_name} {1}'.format(cls, condition)
        db.execute(sql, params)
        db.commit()

        cls.clear_cache(id_)
        cls.clear_cache_by_user_id(user_id)

    @classmethod
    def restore(cls, id_, user_id):
        if not Account.get(user_id):
            raise ValueError('invalid user %r' % user_id)

        instance = cls(id_, user_id, None, None, None, None)
        new_card = cls.get_by_card_number(instance.card_number)
        if new_card:
            raise BankCardChanged(new_card.id_)

        card_number_sha1 = calculate_checksum(instance.card_number)
        bank_id_sha1 = calculate_checksum(instance.bank_id)

        sql = ('insert into {.table_name} (id, user_id, card_number_sha1,'
               ' bank_id_sha1, status) '
               'values (%s, %s, %s, %s, %s)').format(cls)
        params = (id_, user_id, card_number_sha1, bank_id_sha1,
                  cls.Status.active.value)
        db.execute(sql, params)
        db.commit()

        bankcard = cls.get(id_)
        rsyslog.send('\t'.join([
            str(id_),
            str(user_id),
            str(bankcard.card_number),
            str(bankcard.bank_id),
            str(bankcard.mobile_phone),
            str(bankcard.province_id),
            str(bankcard.city_id),
            str(bankcard.local_bank_name),
        ]), tag='restore_bankcard')
        return bankcard

    @classmethod
    def clear_cache(cls, id_):
        mc.delete(cls.cache_key.format(id_=id_))

    @classmethod
    def clear_cache_by_user_id(cls, user_id):
        mc.delete(cls.cache_key_by_user_id.format(user_id=user_id))

    @classmethod
    def validate_card_number(cls, card_number):
        card_number = unicode(card_number.strip())
        if not card_number:
            raise ValueError('The number should not be none')
        if not card_number.startswith(cls.CHINA_DEBIT_IIN_LIST) and not DEBUG:
            raise ValueError('The number should be issued by China UnionPay')
        if not (16 <= len(card_number) <= 19):
            raise ValueError('The number have an unexpected length')

        try:
            luhn.validate(card_number)
        except (InvalidFormat, InvalidChecksum) as e:
            raise ValueError(*(e.args or (e.message,)))

        return card_number


class BankCardManager(PropsMixin):
    """The bank card manager which should be bound with user profiles."""

    last_used_bankcard_id = PropsItem('last_used_bankcard_id', default=0)

    def get_uuid(self):
        return 'user:{.user_id}:bankcards'.format(self)

    def get_db(self):
        return 'hoard'

    def __init__(self, user_id):
        self.user_id = user_id

    def get_all(self, partner=None):
        """Gets all bank cards of current user.

        :returns: the list of :class:
        """
        cards = [c for c in BankCard.get_by_user(self.user_id) if c.is_active]
        cards = sorted(cards, key=attrgetter('is_default'), reverse=True)
        if cards and not cards[0].is_default:
            cards[0].is_default = True
        if partner:
            cards = [c for c in cards if partner in c.bank.available_in]
        return cards

    def get_latest(self):
        bankcards = sorted(
            self.get_all(), key=attrgetter('creation_time'), reverse=True)
        return first(bankcards, default=None)

    def get_last_used(self):
        bankcard = BankCard.get(self.last_used_bankcard_id)
        if bankcard and bankcard.is_active:
            return bankcard
        return self.get_latest()

    def get_default(self):
        bankcards = self.get_all()
        card = first(bankcards, default=None)
        if not card.is_default:
            card.is_default = True
        return card

    def set_default(self, bankcard):
        if not isinstance(bankcard, BankCard):
            raise TypeError
        if bankcard.is_default:
            return True
        bankcards = self.get_all()
        if bankcard not in bankcards:
            raise BankCardNotActive(bankcard.id_)
        default_card = self.get_default()
        default_card.is_default = False
        bankcard.is_default = True
        return True

    def add(self, **kwargs):
        """Adds a new bank card for current user.

        :params kwargs: the same as :meth:`BankCard.add` except ``user_id``.
        :returns: the created bank card.
        """
        # 静默删除已存在但未使用过的同一银行的卡
        for bankcard in self.get_multi_by_bank(kwargs['bank_id']):
            self.remove(bankcard.card_number, silent=True)
        # 静默删除同一个卡号但未使用过的卡
        bankcard = self.get_by_card_number(kwargs['card_number'])
        if bankcard:
            self.remove(bankcard.card_number, silent=True)

        return BankCard.add(user_id=self.user_id, **kwargs)

    def create_or_update(self, card_number, **kwargs):
        # TODO (tonyseek) 不应该让所有字段都可以更新
        cards = self.get_all()
        is_default = False if cards else True
        kwargs.update({'is_default': is_default})
        card = self.get_by_card_number(card_number)
        if card:
            card.update(**kwargs)
            self.last_used_bankcard_id = card.id_
            return card
        else:
            return self.add(card_number=card_number, **kwargs)

    def get_by_card_number(self, card_number):
        digest = calculate_checksum(card_number)
        return first(
            (c for c in self.get_all() if c.card_number_sha1 == digest), None)

    def get(self, id_):
        return first((c for c in self.get_all() if c.id_ == str(id_)), None)

    def get_multi_by_bank(self, bank_id):
        return [c for c in self.get_all() if c.bank_id == str(bank_id)]

    def remove(self, card_number, silent=False):
        try:
            BankCard.delete_by_card_number(card_number, user_id=self.user_id)
        except CardDeletingError as deleting_error:
            if silent:
                rsyslog.send('%s\t%s' % (card_number, deleting_error),
                             'bankcard_removing_denied')
            else:
                raise
        else:
            rsyslog.send(card_number, 'bankcare_removed')

    def restore(self, id_):
        return BankCard.restore(id_, self.user_id)


def calculate_checksum(raw):
    if isinstance(raw, int):
        raw = str(raw)
    return sha1(raw.strip()).hexdigest()


class BankCardException(Exception):
    """The base exception."""


class BankCardChanged(BankCardException):
    """The id of bank card has been changed."""


class BankCardNotActive(BankCardException):
    pass


class CardDeletingError(BankCardException):
    """The bank card could not be deleted."""


class BankConflictError(BankCardException):
    """Another card in the same bank exists."""

    def __unicode__(self):
        return u'抱歉，每家银行只可绑定一张卡，请选择其他银行重试'


class CardConflictError(BankCardException):
    """The bank card number exists."""

    def __unicode__(self):
        return u'该银行卡已被其他账号使用，无法重复绑定'
