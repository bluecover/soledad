# coding: utf-8


class PackageDistributor(object):
    """The coupon package distributor."""

    def __init__(self, kind_id):
        self.kind_id = kind_id

    @property
    def kind(self):
        from ..kind import PackageKind
        return PackageKind.get(self.kind_id)

    def bestow(self, **kwargs):
        """distributor bestow package to user"""
        raise NotImplementedError

    def can_obtain(self, **kwargs):
        """is user qualified to be bestowed package"""
        raise NotImplementedError

    def can_unpack(self, user, package, **kwargs):
        """is user qualified to unpack the bestowed package"""
        return True
