# -*- coding: utf-8 -*-

'''
基于SecretDB实现的一个加密的数据结构
需要实现的方法：

get_uuid    -> 获得文档的唯一key
get_db      -> 文档所属的db名称

例如下面的实例说明这个数据存放在：

CouchDB数据库中的 guihua_secret_user_data 中
并且每个文档的名称是 user:secret:data:id

HTTP URL:
http://couchdb.server/guihua_secret_user_data/user:secret:data:100
'''


from core.models.mixin.props import SecretPropsMixin


class UserSecretMixin(SecretPropsMixin):

    def get_uuid(self):
        return 'user:secret:data:%s' % self.id

    def get_db(self):
        return 'user_data'
