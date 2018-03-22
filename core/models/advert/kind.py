# coding: utf-8

from datetime import datetime

from weakref import WeakValueDictionary

from core.models.base import EntityModel


class AdvertKind(EntityModel):
    """好规划弹窗广告类型"""

    storage = WeakValueDictionary()

    def __init__(self, id_, name, target_link, pic_link,
                 effective_time, expire_time):
        self.id_ = str(id_)
        self.name = name
        self.target_link = target_link
        self.pic_link = pic_link
        self.effective_time = effective_time
        self.expire_time = expire_time
        self.storage[self.id_] = self

    @property
    def is_effective(self):
        return self.effective_time < datetime.now() < self.expire_time

    @classmethod
    def get(cls, id_):
        return cls.storage.get(id_)


test_advert = AdvertKind(
    id_=1,
    name=u'测试',
    target_link='http://guihua.me.tuluu.com/',
    pic_link='https://dn-ghimg.qbox.me/brBE6MTUbfe60KvV',
    effective_time=datetime(2016, 3, 1),
    expire_time=datetime(2016, 4, 10)
    )
