# -*- coding: utf-8 -*-

from .framework import BaseTestCase

from core.models.mixin.props import PropsItem, PropsMixin


class NotSecretTest(PropsMixin):
    def __init__(self, id=None):
        self.id = id or 10000

    def get_db(self):
        return 'test_db'

    def get_uuid(self):
        return self.id

    data = PropsItem('data', 'nothing')


class SecretTest(PropsMixin):
    def __init__(self, id=None):
        self.id = id or 10000

    def get_db(self):
        return 'test_db_secret'

    def get_uuid(self):
        return self.id

    data = PropsItem('data', 'nothing', secret=True)


class MultiSecretTest(PropsMixin):
    def __init__(self, id=None):
        self.id = id or 10000

    def get_db(self):
        return 'test_db_multi'

    def get_uuid(self):
        return self.id

    data = PropsItem('data', 'nothing')


setattr(NotSecretTest, 'long_data' * 20,
        PropsItem('long_data' * 20, 'nothing'))
setattr(SecretTest, 'long_data' * 20,
        PropsItem('long_data' * 20, 'nothing', secret=True))
setattr(MultiSecretTest, 'long_data' * 20,
        PropsItem('long_data' * 20, 'nothing', secret=True))


class PropsTest(BaseTestCase):
    def test_props_get_and_set(self):
        t = NotSecretTest()
        self.assertEqual(t.data, 'nothing')
        self.assertEqual(getattr(t, 'long_data' * 20), 'nothing')
        t.data = '123'
        setattr(t, 'long_data' * 20, '123')
        t = NotSecretTest()
        self.assertEqual(t.data, '123')
        self.assertEqual(getattr(t, 'long_data' * 20), '123')
        t.data = [1, 2, 3]
        setattr(t, 'long_data' * 20, [1, 2, 3])
        t = NotSecretTest()
        self.assertEqual(t.data, [1, 2, 3])
        self.assertEqual(getattr(t, 'long_data' * 20), [1, 2, 3])
        t.data = dict(a=1, b=2, c=3)
        setattr(t, 'long_data' * 20, dict(a=1, b=2, c=3))
        t = NotSecretTest()
        self.assertEqual(t.data, dict(a=1, b=2, c=3))
        self.assertEqual(getattr(t, 'long_data' * 20), dict(a=1, b=2, c=3))

    def test_secret_props_get_and_set(self):
        t = SecretTest()
        self.assertEqual(t.data, 'nothing')
        self.assertEqual(getattr(t, 'long_data' * 20), 'nothing')
        t.data = '123'
        setattr(t, 'long_data' * 20, '123')
        t = SecretTest()
        self.assertEqual(t.data, '123')
        self.assertEqual(getattr(t, 'long_data' * 20), '123')
        t.data = [1, 2, 3]
        setattr(t, 'long_data' * 20, [1, 2, 3])
        t = SecretTest()
        self.assertEqual(t.data, [1, 2, 3])
        self.assertEqual(getattr(t, 'long_data' * 20), [1, 2, 3])
        t.data = dict(a=1, b=2, c=3)
        setattr(t, 'long_data' * 20, dict(a=1, b=2, c=3))
        t = SecretTest()
        self.assertEqual(t.data, dict(a=1, b=2, c=3))
        self.assertEqual(t.data, dict(a=1, b=2, c=3))

    def test_update_props_items_no_secret(self):
        t = NotSecretTest(20000)
        self.assertEqual(t.data, 'nothing')
        self.assertEqual(getattr(t, 'long_data' * 20), 'nothing')

        t.update_props_items({
            'data': '123',
            'long_data' * 20: '123'
        })

        t = NotSecretTest(20000)

        self.assertEqual(t.data, '123')
        self.assertEqual(getattr(t, 'long_data' * 20), '123')

    def test_update_props_items_secret(self):
        t = SecretTest(20000)
        self.assertEqual(t.data, 'nothing')
        self.assertEqual(getattr(t, 'long_data' * 20), 'nothing')

        t.update_props_items({
            'data': '123',
            'long_data' * 20: '123'
        })

        t = SecretTest(20000)

        self.assertEqual(t.data, '123')
        self.assertEqual(getattr(t, 'long_data' * 20), '123')

    def test_update_props_items_multi_secret(self):
        t = MultiSecretTest(20000)
        self.assertEqual(t.data, 'nothing')
        self.assertEqual(getattr(t, 'long_data' * 20), 'nothing')

        t.update_props_items({
            'data': '123',
            'long_data' * 20: '123'
        })

        t = MultiSecretTest(20000)

        self.assertEqual(t.data, '123')
        self.assertEqual(getattr(t, 'long_data' * 20), '123')
