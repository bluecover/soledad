# coding: utf-8

import uuid
import decimal

from jupiter.app import create_app
from jupiter.integration.firewood import firewood
from libs.utils.log import bcolors
from core.models.user.account import Account
from core.models.firewood.facade import FirewoodWorkflow


EMAIL = 'zw@guihua.com'
AMOUNT = decimal.Decimal('100')
TAGS = ('test', 'dev')


def main():
    user = Account.get_by_alias(EMAIL)
    if not user:
        bcolors.fail('%s is not found' % EMAIL, key='firewood')

    flow = FirewoodWorkflow(user.id_)

    transaction = firewood.create_transaction(flow.account_uid, AMOUNT, TAGS)
    transaction_uid = uuid.UUID(transaction.json()['uid'])
    transaction = firewood.confirm_transaction(flow.account_uid, transaction_uid)
    transaction_uri = transaction.json()['_links']['self']

    bcolors.run('%s +100.00' % transaction_uri, key='firewood')


if __name__ == '__main__':
    with create_app().app_context():
        main()
