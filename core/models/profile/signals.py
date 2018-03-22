from blinker import Namespace


_signals = Namespace()

identity_saved = _signals.signal('identity-saved')
before_deleting_bankcard = _signals.signal('before-deleting-bankcard')
bankcard_updated = _signals.signal('bankcard_updated')
