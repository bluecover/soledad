# coding: utf-8

from datetime import datetime

from libs.cache import mc


class FeatureSwitch(object):

    def __nonzero__(self):
        return self.is_enabled

    def __bool__(self):
        return self.is_enabled

    @property
    def is_enabled(self):
        raise NotImplementedError


class TimeIntervalSwitch(FeatureSwitch):

    def __init__(self, close_time, open_time=None):
        self.open_time = open_time
        self.close_time = close_time

        if self.open_time is not None and self.close_time <= self.open_time:
            raise ValueError('close time should be later than open time')

    @property
    def is_enabled(self):
        if self.open_time is None:
            # open time is not specified
            return datetime.now() <= self.close_time
        return self.open_time <= datetime.now() <= self.close_time


class CacheKeySwitch(FeatureSwitch):
    """The redis switch for enabling or disabling some features."""

    def __init__(self, key):
        self.key = 'feature_switch:%s' % key

    @property
    def is_enabled(self):
        return bool(mc.get(self.key))

    def enable(self):
        mc.set(self.key, True)

    def disable(self):
        mc.set(self.key, False)


class TimeWindowSwitch(FeatureSwitch):

    def __init__(self, name):
        self.open_time_key = '%s:open_time' % name
        self.close_time_key = '%s:close_time' % name
        self.name = name

    @property
    def is_enable(self):
        if self.open_time and self.close_time:
            return self.open_time <= datetime.now() <= self.close_time

    @property
    def open_time(self):
        return mc.get(self.open_time_key)

    @open_time.setter
    def open_time(self, open_time):
        mc.set(self.open_time_key, open_time)

    @property
    def close_time(self):
        return mc.get(self.close_time_key)

    @close_time.setter
    def close_time(self, close_time):
        mc.set(self.close_time_key, close_time)

    def disable(self):
        mc.delete(self.open_time_key)
        mc.delete(self.close_time_key)


app_download_banner_switch = CacheKeySwitch('app-download-banner')
zhiwang_offline_switch = TimeIntervalSwitch(
    open_time=datetime(2016, 1, 7, 0, 55),
    close_time=datetime(2016, 1, 7, 2, 05))
spring_promotion_switch = TimeIntervalSwitch(datetime(2016, 2, 7, 23, 59, 59))
dynamic_firewood_switch = TimeIntervalSwitch(datetime(2016, 3, 14, 19, 59, 59))
xm_offline_switch = TimeIntervalSwitch(datetime(2016, 4, 30, 23, 59, 59))
zhiwang_fdb_product_on_switch = TimeIntervalSwitch(datetime(2016, 4, 30, 23, 59, 59))
