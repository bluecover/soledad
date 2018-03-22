# coding: utf-8

from __future__ import absolute_import

from core.models.user.account import Account
from .product import PlaceboProduct


@PlaceboProduct.strategy_storage.register('1', u'2016 新春体验金')
def strategy_2016_spring(user_id):
    from core.models.promotion.festival.spring import SpringGift
    user = Account.get(user_id)
    gift = SpringGift.get_by_user(user)
    return gift.status is SpringGift.Status.reserved
