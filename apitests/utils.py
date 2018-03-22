# coding: utf-8
import datetime


def get_testurl(testurl):
    return '{0}/{1}'.format('/api/v1', str(testurl))


def get_testurl_v2(testurl):
    return '{0}/{1}'.format('/api/v2', str(testurl))


def get_date():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')


def get_start_date():
    day = datetime.datetime.weekday(datetime.datetime.now())
    if day == 4:
        return datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=3),
                                          '%Y-%m-%d')
    elif day == 5:
        return datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2),
                                          '%Y-%m-%d')
    else:
        return datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1),
                                          '%Y-%m-%d')


def get_create_at_time():
    # '2015-04-15T00:00:00+08:00'
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT00:00:00+08:00')


def get_op_days_time(day):
    return datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=day),
                                      '%Y-%m-%d %H:%M:%S')


def get_op_days_date(day):
    return datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=day),
                                      '%Y-%m-%d')


class Obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [Obj(x) if isinstance(x, dict) else x for x in b])
            else:
                if 'time' in a and b is not None:
                    setattr(self, a, Obj(b) if isinstance(b, dict) else datetime.datetime.strptime(
                        b, '%Y-%m-%d %H:%M:%S'))
                elif 'date' in a and b is not None:
                    setattr(self, a, Obj(b) if isinstance(b, dict) else datetime.datetime.strptime(
                        b, '%Y-%m-%d %H:%M:%S').date())
                else:
                    setattr(self, a, Obj(b) if isinstance(b, dict) else b)
        self.dict = d

    def __getitem__(self, item):
        return self.dict[item]
