# coding: utf-8

from mock import patch

from libs.utils.log import bcolors
from core.models.user.account import Account
from core.models.user.register import register_without_confirm
from core.models.user.consts import ACCOUNT_REG_TYPE
from core.models.profile.identity import Identity
from core.models.profile.bankcard import BankCardManager
from core.models.hoard.zhiwang.account import ZhiwangAccount


EMAIL = u'zw@guihua.com'
MOBILE_PHONE = u'13548384636'
PERSON_NAME = u'张无忌'
PERSON_RICN = u'13112319920611251X'
ZHIWANG_TOKEN = u'41bveexx'
BANKCARD_NO = u'5000526620771884'
BANKCARD_DIVISION = u'110100'  # 北京市市辖区
BANKCARD_BANK = u'1'  # 工商银行


def main():
    user = Account.get_by_alias(EMAIL)
    if not user:
        user = register_without_confirm(
            EMAIL, 'testtest', ACCOUNT_REG_TYPE.EMAIL)
        bcolors.run(repr(user), key='zhiwang')

    # 绑定身份证和手机
    user.add_alias(MOBILE_PHONE, ACCOUNT_REG_TYPE.MOBILE)
    identity = Identity.save(user.id_, PERSON_NAME, PERSON_RICN)
    bcolors.run(repr(identity), key='zhiwang')

    # 绑定指旺帐号
    ZhiwangAccount.bind(user.id_, ZHIWANG_TOKEN)
    bcolors.run(repr(ZhiwangAccount.get_by_local(user.id_)), key='zhiwang')

    # 绑定银行卡
    bankcards = BankCardManager(user.id_)
    with patch('core.models.profile.bankcard.DEBUG', True):
        bankcard = bankcards.create_or_update(
            mobile_phone=user.mobile,
            card_number=BANKCARD_NO,
            bank_id=BANKCARD_BANK,
            city_id=BANKCARD_DIVISION[:4] + u'00',
            province_id=BANKCARD_DIVISION[:2] + u'0000',
            local_bank_name=u'')
        bcolors.run(repr(bankcard), key='zhiwang')
    bcolors.run('success: %s' % EMAIL, key='zhiwang')


if __name__ == '__main__':
    main()
