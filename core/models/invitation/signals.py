# coding: utf-8

from blinker import Namespace


_signals = Namespace()

invitation_accepted = _signals.signal('invitation-accepted')
