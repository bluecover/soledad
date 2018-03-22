# coding: utf-8

from pytest import raises

from core.models.profile.address import Address
from .framework import BaseTestCase


class AddressTestCase(BaseTestCase):

    def setUp(self):
        super(AddressTestCase, self).setUp()
        self.user = self.add_account('foo@guihua.dev', 'foobar', 'foo')

    def test_get_nothing(self):
        assert not Address.get(1024)

    def test_create(self):
        address = Address.add(self.user.id_, u'110105', u'理财工厂')
        assert address and address.id_
        assert address.user == self.user
        assert [x.name for x in address.division.stack()] == [
            u'北京市', u'市辖区', u'朝阳区']
        assert address.street == u'理财工厂'

    def test_create_failed(self):
        with raises(ValueError) as einfo:
            Address.add(-1, u'110105', u'理财工厂')
        assert einfo.value.args[0] == 'user not found'

        with raises(ValueError) as einfo:
            Address.add(self.user.id_, u'100000', u'理财工厂')
        assert einfo.value.args[0] == 'administrative division not found'

        with raises(ValueError) as einfo:
            Address.add(self.user.id_, u'110105', u'')
        assert 'too short' in einfo.value.args[0]

        with raises(ValueError) as einfo:
            Address.add(self.user.id_, u'110105', u'理财工厂' * 1000)
        assert 'too long' in einfo.value.args[0]

        with raises(UnicodeDecodeError):
            Address.add(self.user.id_, u'110105', b'理财工厂')

    def test_update(self):
        address = Address.add(self.user.id_, u'110105', u'理财工厂')

        with raises(ValueError) as einfo:
            address.update(division_id=u'100000', street=u'理财工厂')
        assert einfo.value.args[0] == 'administrative division not found'

        with raises(ValueError) as einfo:
            address.update(division_id=u'110101', street=u'')
        assert 'too short' in einfo.value.args[0]

        with raises(ValueError) as einfo:
            address.update(division_id=u'110101', street=u'理财工厂' * 1000)
        assert 'too long' in einfo.value.args[0]

        address.update(division_id=u'110104', street=u'理财')
        assert address.user == self.user  # user not changed
        assert [x.name for x in address.division.stack()] == \
            [u'北京市', u'市辖区', u'宣武区']
        assert address.street == u'理财'

        address = Address.get(address.id_)
        assert address.user == self.user  # user not changed
        assert [x.name for x in address.division.stack()] == [
            u'北京市', u'市辖区', u'宣武区']
        assert address.street == u'理财'

        address.division  # trigger cached_property
        address.update(division_id=u'110103', street=u'理财')
        assert [x.name for x in address.division.stack()] == [
            u'北京市', u'市辖区', u'崇文区']
        address = Address.get(address.id_)
        assert [x.name for x in address.division.stack()] == [
            u'北京市', u'市辖区', u'崇文区']

    def test_get_by_user_and_delete(self):
        id_1 = Address.add(self.user.id_, u'110105', u'理财工厂').id_
        id_2 = Address.add(self.user.id_, u'110101', u'测试工厂').id_

        addresses = Address.get_multi_by_user(self.user.id)
        assert len(addresses) == 2
        assert addresses[0].id_ == id_1
        assert addresses[0].division.code == '110105'
        assert addresses[0].street == u'理财工厂'
        assert addresses[1].id_ == id_2
        assert addresses[1].division.code == '110101'
        assert addresses[1].street == u'测试工厂'

        Address.delete(id_2)
        addresses = Address.get_multi_by_user(self.user.id)
        assert len(addresses) == 1
        assert addresses[0].id_ == id_1

        Address.delete(id_1)
        addresses = Address.get_multi_by_user(self.user.id)
        assert len(addresses) == 0
