# -*- coding: utf-8 -*-

from pytest import raises
from mock import patch

from core.models.profile.bankcard import (
    BankCard, BankCardManager, CardConflictError, BankConflictError)
from .framework import BaseTestCase


class BankCardTest(BaseTestCase):

    local_user_info = ('foo@guihua.dev', 'foobar', 'Foo')

    def setUp(self):
        super(BankCardTest, self).setUp()
        self.local_account = self.add_account(*self.local_user_info)
        self.bankcards = BankCardManager(self.local_account.id)

    def test_create(self):
        with patch('core.models.profile.bankcard.DEBUG', True):
            b1 = BankCard.add(
                self.local_account.id, '13800138000', '6222980000000002',
                '1', '440113', '440000', '大望路支行', True)
            b2 = BankCard.add(
                self.local_account.id, '13800138001', '6222980000010001',
                '2', '440113', '440000', '西二旗支行', False)
            assert b1
            assert b2

        bank_card = BankCard.get(b1.id_)
        assert bank_card.mobile_phone == '13800138000'
        assert bank_card.card_number == '6222980000000002'
        assert bank_card.city_id == '440113'
        assert bank_card.province_id == '440000'
        assert bank_card.local_bank_name == '大望路支行'
        assert bank_card.is_default

        bank_card = BankCard.get(b2.id_)
        assert bank_card.mobile_phone == '13800138001'
        assert bank_card.card_number == '6222980000010001'
        assert bank_card.city_id == '440113'
        assert bank_card.province_id == '440000'
        assert bank_card.local_bank_name == '西二旗支行'
        assert bank_card.is_default is False

    def test_failed_to_create(self):
        with patch('core.models.profile.bankcard.DEBUG', True):
            BankCard.add(
                self.local_account.id, '13800138000', '6222980000000002',
                '1', '440113', '440000', '大望路支行', False)

            with raises(CardConflictError):
                BankCard.add(
                    self.local_account.id, '13800138000', '6222980000000002',
                    '2', '440113', '440000', '大望路支行', False)

            with raises(BankConflictError):
                BankCard.add(
                    self.local_account.id, '13800138000', '6222980000010001',
                    '1', '440113', '440000', '大望路支行', False)

    def test_discard(self):
        def create_bankcard_in_the_same_bank():
            return BankCard.add(
                self.local_account.id, '13800138000', '6222980000010001',
                '1', '440113', '440000', '大望路支行', False)

        with patch('core.models.profile.bankcard.DEBUG', True):
            bankcard = BankCard.add(
                self.local_account.id, '13800138000', '6222980000000002',
                '1', '440113', '440000', '大望路支行', False)

            with raises(BankConflictError):
                create_bankcard_in_the_same_bank()

            bankcard.discard()
            assert self.bankcards.get_all() == []
            assert self.bankcards.get_latest() is None
            assert self.bankcards.get_last_used() is None

            new_bankcard = create_bankcard_in_the_same_bank()
            assert new_bankcard

        card_ids = {c.id_ for c in self.bankcards.get_all()}
        assert bankcard.id_ not in card_ids
        assert new_bankcard.id_ in card_ids
        assert BankCard.get(bankcard.id_).status is BankCard.Status.discarded
        assert self.bankcards.get_latest().id_ == new_bankcard.id_
        assert self.bankcards.get_last_used().id_ == new_bankcard.id_

    def test_bank_card_manager(self):
        with patch('core.models.profile.bankcard.DEBUG', True):
            b1 = BankCard.add(
                self.local_account.id, '13800138000', '6222980000000002',
                '1', '440113', '440000', '大望路支行', False)
            b2 = BankCard.add(
                self.local_account.id, '13800138001', '6222980000010001',
                '2', '440113', '440000', '大望路支行', False)

        cards = self.bankcards.get_all()
        assert len(cards) == 2

        assert cards[0].mobile_phone == b1.mobile_phone
        assert cards[0].card_number == b1.card_number
        assert cards[0].local_bank_name == b1.local_bank_name

        assert cards[1].mobile_phone == b2.mobile_phone
        assert cards[1].card_number == b2.card_number
        assert cards[1].local_bank_name == b2.local_bank_name

        self.bankcards.add(
            mobile_phone='13800138002',
            card_number='6222980000030009',
            bank_id='3',
            city_id='440113',
            province_id='440000',
            local_bank_name='西二旗支行',
            is_default=False)

        cards = self.bankcards.get_all()
        assert len(cards) == 3

        assert cards[2].mobile_phone == '13800138002'
        assert cards[2].card_number == '6222980000030009'
        assert cards[2].local_bank_name == '西二旗支行'

    def test_delete_and_restore(self):
        with patch('core.models.profile.bankcard.DEBUG', True):
            b1 = BankCard.add(
                self.local_account.id, '13800138000', '6222980000000002',
                '1', '440113', '440000', '大望路支行', False)
            assert b1

        BankCard.delete_by_card_number(
            '6222980000000002', self.local_account.id)
        b2 = BankCard.get(b1.id_)
        assert b2 is None

        BankCard.restore(b1.id_, self.local_account.id)
        b3 = BankCard.get(b1.id_)
        assert b3

        assert b3.mobile_phone == '13800138000'
        assert b3.card_number == '6222980000000002'
        assert b3.city_id == '440113'
        assert b3.province_id == '440000'
        assert b3.local_bank_name == '大望路支行'
