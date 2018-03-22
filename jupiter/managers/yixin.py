import os
import sys
import json

from flask_script import Manager
from yxlib.response import RemoteError

from core.models.user.account import Account
from core.models.hoard import YixinService, YixinAccount, HoardProfile, HoardOrder
from core.models.hoard.profile import ORDER_STATUS_MAP
from libs.utils.log import bcolors
from jupiter.ext import yixin


manager = Manager()
manager.__doc__ = 'The commands for yixin services.'


@manager.command
def init():
    """Downloads the product data of Yixin."""
    try:
        response = yixin.query.p2p_service_list()
    except RemoteError as e:
        bcolors.fail('%s : %s : %s' % e.args)
    else:
        for service_info in response.data:
            service = YixinService.add(service_info)
            bcolors.success('YixinService: %s' % service.p2pservice_name)


@manager.command
def orders(user_alias):
    """Lists all orders of specific user."""
    user = Account.get_by_alias(user_alias)
    if not user:
        bcolors.fail('user not found')
        return

    profile = HoardProfile.get(user.id)
    if not profile:
        bcolors.fail('profile not initialized')
        return

    for order, _, status in profile.orders():
        data = [
            order.id_,
            order.creation_time,
            round(order.order_amount, 2),
            order.service.p2pservice_name,
            status,
        ]
        print(u'\t'.join(map(unicode, data)))


def remote_statuses():
    return [s.encode(sys.stdin.encoding or 'utf-8') for s in ORDER_STATUS_MAP]


@manager.option('new_status', type=bytes, choices=remote_statuses())
@manager.option('order_id', type=int)
def order_status(order_id, new_status):
    """Edits the status of specific order."""
    if new_status in remote_statuses():
        new_status = new_status.decode(sys.stdin.encoding)
    else:
        status_list = ', '.join(remote_statuses())
        bcolors.fail('status must be one of %s' % status_list)
        return

    order = HoardOrder.get(order_id)
    if not order:
        bcolors.fail('order not found')
        return

    profile = HoardProfile.get(order.user_id)
    matched_index = [
        index
        for index, order_info in enumerate(profile.person_account_info)
        if order_info['finOrderNo'] == order.fin_order_id]

    if not matched_index:
        bcolors.fail('failed')
        return

    account_info = list(profile.person_account_info)
    account_info[matched_index[0]]['finOrderStatus'] = unicode(new_status)
    profile.person_account_info = account_info

    bcolors.success('done')


@manager.command
def token_dump(user_alias, workdir=None):
    """Dumps API token from database."""
    account = Account.get_by_alias(user_alias)
    if not account:
        return bcolors.fail('user %r not found' % user_alias)

    workdir = os.path.expanduser(workdir or '~/.guihua')
    if not os.path.exists(workdir):
        os.makedirs(workdir)

    yixin_account = YixinAccount.get_by_local(account.id_)
    if not yixin_account:
        return bcolors.fail('%r need to bind yixin account' % user_alias)

    jsonfile_location = os.path.join(workdir, 'solar-yixin-token.json')

    if os.path.exists(jsonfile_location):
        with open(jsonfile_location) as jsonfile:
            data = json.load(jsonfile)
        if not isinstance(data, dict):
            return bcolors.fail('unexpected data')
    else:
        data = {}

    data[user_alias] = {
        'user_alias': user_alias,
        'yixin_account': yixin_account.p2p_account,
        'yixin_token': yixin_account.p2p_token,
    }

    with open(jsonfile_location, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    bcolors.success('success: %s %s' % (user_alias, yixin_account.p2p_account))


@manager.command
def token_load(workdir=None):
    """Loads API token from local file."""
    workdir = os.path.expanduser(workdir or '~/.guihua')
    if not os.path.exists(workdir):
        return bcolors.fail('token not found')

    jsonfile_location = os.path.join(workdir, 'solar-yixin-token.json')
    if not os.path.exists(jsonfile_location):
        return bcolors.fail('token not found')

    with open(jsonfile_location) as jsonfile:
        data = json.load(jsonfile)

    for user_alias, item in data.iteritems():
        account = Account.get_by_alias(item['user_alias'])
        if not account:
            bcolors.fail('user %s not found' % user_alias)
            continue

        p2p_account = item['yixin_account']
        p2p_token = item['yixin_token']
        YixinAccount.bind(account.id_, p2p_account, p2p_token)

        bcolors.success('restored %s %s' % (account, p2p_account))
