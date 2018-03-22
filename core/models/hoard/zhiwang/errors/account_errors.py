# coding: utf-8


# 注册错误


class SignUpError(Exception):
    pass


class MissingIdentityError(SignUpError):
    pass


class MissingMobilePhoneError(SignUpError):
    pass

# 账号绑定错误


class AccountError(Exception):
    pass


class UnboundAccountError(AccountError):
    pass


class RemoteAccountOccupiedError(AccountError):
    pass


class MismatchUserError(AccountError):
    pass


class RepeatlyRegisterError(AccountError):
    pass
