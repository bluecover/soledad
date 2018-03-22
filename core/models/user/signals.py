from blinker import Namespace


_signals = Namespace()

user_register_completed = _signals.signal('user-register-completed')
before_freezing_user = _signals.signal('before-freezing-user')
