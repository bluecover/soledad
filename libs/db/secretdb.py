# -*- coding: utf-8 -*-

'''
A secret db based on couchdb

基于CouchDB的一个加密的数据库，用于存放用户的隐私信息

name    -> CouchDB中的一个文档

所有的SecretDB里的值都会变成一个json的dict，经过加密后存放在
CouchDB的一个文档的secret字段中

secretdb实例是一个数据的实例

例如，设置一个用户的私密数据，则类似于core.models.user.userinfo中的写法
通过一个id拿到对应的文档，secretdb.get(user_id)
secretdb.data 可以拿到所有的数据
secretdb.update(key1=value1, key2=value2, ...) 可以设置数据
secretdb.data.get(key1) 得到 value1

所有的key-value都会变成一个json的字符串并且RSA加密，再base64 encode
存放在CouchDB中

实现：

1. 默认存放在guihua_secret_xxx数据库中。
2. 每个对象都有一个独立的id，例如用户数据是user:secret:data:id
3. 用户数据只有一个key，是secret，值为加密后的字符串
4. 用户取数据从Couchdb的guihua_secret_xxx数据库中读取对应的文档
5. 读取加密的字符串并解密
'''

from solar.db.secretdb import SecretDB


__all__ = ['SecretDB']
