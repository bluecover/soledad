from __future__ import absolute_import

from solar.redis.context import init_context
from solar.redis.rdstore import RedisStore


rdstore = RedisStore.init_by_context(init_context('solar'))
