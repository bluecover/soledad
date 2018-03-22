# coding:utf-8

from core.models.bank.banks import bank_collection
from core.models.utils.switch import TimeWindowSwitch


wallet_suspend = {
    'deposit': TimeWindowSwitch('wallet-deposit'),
    'withdraw': TimeWindowSwitch('wallet-withdraw')}
wallet_bank_suspend = {
    'purchase': {
        bank: TimeWindowSwitch('wallet-bank-deposit:%s' % bank.id_)
        for bank in bank_collection.banks},
    'redeem': {
        bank: TimeWindowSwitch('wallet-bank-withdraw:%s' % bank.id_)
        for bank in bank_collection.banks}}
