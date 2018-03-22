from libs.cache import mc


class FeatureVoucher(object):

    def __bool__(self):
        return self.is_enabled

    @property
    def is_enabled(self):
        raise NotImplementedError


class VerifyVoucher(FeatureVoucher):

    def __init__(self, name):

        self.key = '%s:validated_key' % name

    @property
    def voucher(self):
        return mc.get(self.key)

    @voucher.setter
    def voucher(self, base):
        mc.set(self.key, base)

    @property
    def is_enabled(self):
        return bool(mc.get(self.key))

    def disable(self):
        mc.delete(self.key)
