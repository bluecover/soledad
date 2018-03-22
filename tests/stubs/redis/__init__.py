# -*- coding:utf-8 -*-


def from_url(url):
    return Redis()


class FakePipeLine(object):
    memdb = []

    def __init__(self, redis):
        self.redis = redis

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __enter__(self):
        return self

    def get(self, name):
        r = self.redis.get(name)
        self.memdb.append(r)

    def delete(self, name):
        r = self.redis.get(name)
        self.redis.delete(name)
        try:
            self.memdb.remove(r)
        except ValueError:
            pass

    def execute(self):
        return self.memdb


class FakeScript(object):
    def __init__(self, client, script):
        self.registered_client = client
        self.script = script
        self.sha = ''


class Redis(object):
    def __init__(self, *args, **kwargs):
        self.d = dict()
        self.ld = dict()
        self.rd = dict()

    def set(self, name, value, *args, **kwargs):
        if not self.d.get(name):
            self.d[name] = None
        self.d[name] = value

    def setnx(self, name, value):
        if not self.d.get(name):
            self.d[name] = value
            return True
        return False

    def get(self, name, *args, **kwargs):
        return self.d.get(name, None)

    def incr(self, name):
        value1 = self.d.get(name)
        if value1 is None:
            self.d[name] = 1
        else:
            self.d[name] = value1 + 1

    def incrby(self, name, amount):
        value1 = self.d.get(name)
        if value1 is None:
            self.d[name] = amount
        else:
            self.d[name] = value1 + amount

    def delete(self, name):
        self.d.pop(name, None)

    def pipeline(self):
        return FakePipeLine(self)

    def ping(self):
        return True

    def register_script(self, script):
        return FakeScript(self, script)

    def lock(self, *args, **kwargs):
        from mock import MagicMock
        return MagicMock()

    def expire(self, key, expire):
        pass

    def lpop(self, k, v):
        if not self.ld.get(k):
            return

        _list = self.ld.get(k)
        assert isinstance(_list, list)
        self.ld[k] = _list[1:]

    def lpush(self, k, v):
        if not self.ld.get(k):
            self.ld[k] = []
        self.ld[k].insert(0, v)

    def llen(self, k):
        if not self.ld.get(k):
            return 0
        return len(self.ld.get(k))

    def rpush(self, k, value):
        data = self.rd.get(k, [])
        data.append(value)
        self.rd[k] = data

    def lrange(self, k, start, stop):
        data = self.rd.get(k, [])
        if start < 0:
            start = 0
        if stop == -1:
            return data[start:]
        elif stop > 0:
            stop += 1
        return data[start:stop]

    def flushall(self):
        self.d = dict()
        self.ld = dict()
        self.rd = dict()
