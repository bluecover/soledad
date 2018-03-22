# coding: utf-8

# 礼包错误


class PackageError(Exception):
    pass


class WrongPackageTokenError(PackageError):
    pass


class InvalidPackageStatusTransferError(PackageError):

    @property
    def current_status(self):
        return self.args[0]

    @property
    def target_status(self):
        return self.args[1]


class PackageDistributorDenied(PackageError):
    pass
