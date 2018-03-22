# coding: utf-8


# 合同错误


class ContractError(Exception):
    pass


class ContractFetchingError(ContractError):
    pass
