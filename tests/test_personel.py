# coding: utf-8

from .framework import BaseTestCase
from pytest import raises
from core.models.user.personel import PersonelGroup, staff


class PersonelTestCase(BaseTestCase):

    def setUp(self):
        super(PersonelTestCase, self).setUp()
        self.user1 = self.add_account(mobile='13800000001')
        self.identity1 = self.add_identity(self.user1.id_, u'张无忌', '13112319920611251X')

    def test_personel(self):
        staff.del_personel(self.user1.id_)
        assert self.user1.id_ not in staff.users

        staff.add_personel(self.user1.id_, self.identity1.person_name)

        assert self.user1.id_ in staff.users
        assert staff.users[self.user1.id_] == self.identity1.person_name

        staff.update_personel(self.user1.id_, u'李四')
        assert staff.users[self.user1.id_] == u'李四'

    def test_add_repeat_persondel(self):
        with raises(ValueError):
            PersonelGroup('staff')

    def test_existed_user(self):
        with raises(KeyError):
            staff.add_personel(self.user1.id_, self.identity1.person_name)
            staff.add_personel(self.user1.id_, self.identity1.person_name)

    def test_unexisted_user(self):
        with raises(ValueError):
            staff.add_personel('100001', u'王五')

    def test_normal_personel(self):
        test = PersonelGroup('test')

        assert test.name == 'test'
