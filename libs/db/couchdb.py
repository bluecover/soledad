# -*- coding: utf-8 -*-

"""
A simple client for couchdb

db       -> CouchDB中的一个数据库，也就是一个文件
document -> CouchDB中的一个文档，必须在某个数据库下面

例如，一个用户需要放在一个叫user的db中，document的id可以是user的id
那么，couchdb.get('user', 'userid') 可以拿到用户的数据
等同，http://couchdb.server/user/userid 直接获得用户的JSON数据

couchdb.set('user', 'userid') 可以设置一个用户的数据

不需要直接使用这个类，而推荐使用core.models.mixin.props里的类
"""

from __future__ import absolute_import

from solar.db.couchdb.context import init_context
from solar.db.couchdb import CouchDB
from libs.cache import mc


cdb = CouchDB.init_by_context(init_context('solar'), mc)
