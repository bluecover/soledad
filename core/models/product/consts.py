# -*- coding: utf-8 -*-

from solar.utils.storify import storify

RISK_RANK = storify(dict(LOW='1',
                         MEDIUM='2',
                         HIGH='3'))

RECOMMEND_RANK = storify(dict(ONE=1,
                              TWO=2,
                              THREE=3,
                              FOUR=4,
                              FIVE=5))

PRODUCT_STATUS = storify(dict(ON='0',
                              OFF='1'))

P2P_TYPE = storify(dict(P2P='1'))

BANK_TYPE = storify(dict(BANK='1'))

DEBT_TYPE = storify(dict(CERTIFICATE='1'))

FUND_TYPE = storify(dict(MMF='1',          # Money market fund 货币基金
                         BOND='2',        # 债券型基金
                         INDEX='3',        # 指数型基金
                         STOCK='4'))       # 股票型基金

FUND_NAME = storify(dict(MMF='货币型基金',          # Money market fund 货币基金
                         BOND='债券型基金',        # 债券型基金
                         INDEX='指数型基金',        # 指数型基金
                         STOCK='股票型基金'))       # 股票型基金

INSURE_TYPE = storify(dict(LIFE='1',       # 定期寿险
                           ACCIDENT='2',   # 综合意外险
                           DISEASE='3',    # 重疾险
                           CHILDREN='4'))  # 儿童综合险

INSURE_NAME = storify(dict(LIFE='定期寿险',       # 定期寿险
                           ACCIDENT='综合意外险',   # 综合意外险
                           DISEASE='重疾险',    # 重疾险
                           CHILDREN='儿童综合险'))  # 儿童综合险

DEBT_PAY_TYPE = storify(dict(DISPOSE_ALL='1'  # 到期一次性付息
                             ))
