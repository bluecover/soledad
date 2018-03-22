# coding: utf-8

from __future__ import absolute_import

from libs.utils.log import bcolors
from core.models.user.account import Account


def main():
    channels = [
        Account.channel_class.add(u'西方记者', 'west'),
        Account.channel_class.add(u'香港记者', 'hk'),
    ]
    for channel in channels:
        bcolors.run(repr(channel), key='channel')


if __name__ == '__main__':
    main()
