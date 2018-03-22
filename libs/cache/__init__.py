from __future__ import absolute_import

from solar.redis.consts import CACHE_NAME, STATIC_NAME
from solar.redis.decorator import create_decorators

from libs.db.rdstore import rdstore


mc = rdstore.get_redis(CACHE_NAME)
static_mc = rdstore.get_redis(STATIC_NAME)

globals().update(create_decorators(mc))
