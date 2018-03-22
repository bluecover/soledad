from blinker import Namespace

__all__ = ['transaction_status_changed']

ns = Namespace()
transaction_status_changed = ns.signal('transaction_status_changed')
account_status_changed = ns.signal('account_status_changed')
