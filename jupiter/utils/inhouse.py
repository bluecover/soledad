from __future__ import absolute_import

from functools import update_wrapper

from ipaddress import ip_address, IPv4Network
from flask import has_request_context, request, abort


__all__ = ['inhouse', 'check_is_inhouse']


inhouse_network_list = [
    # office
    IPv4Network(u'111.202.32.0/24'),

    # vpn
    IPv4Network(u'114.113.229.0/24'),
    IPv4Network(u'114.113.226.0/24'),
]


def check_is_inhouse():
    if request.remote_addr:
        remote_addr = ip_address(unicode(request.remote_addr))
        if remote_addr.is_private:
            return True
        return any(remote_addr in network for network in inhouse_network_list)
    else:
        return False


def inhouse(wrapped):
    """Restricts the view endpoint be accessible by inhouse members only."""
    def wrapper(*args, **kwargs):
        if has_request_context() and not check_is_inhouse():
            abort(403, 'inhouse restircted')
        return wrapped(*args, **kwargs)
    return update_wrapper(wrapper, wrapped)
