from functools import update_wrapper

from flask import url_for
from werkzeug.utils import cached_property

from .context import ensure_app_context


__all__ = ['permalink']


class Permalink(object):
    """A decorator to transform a method into a URL property."""

    def __init__(self, endpoint, cached=True):
        self.endpoint = endpoint
        self.cached = cached
        self._property = cached_property if self.cached else property

    def __call__(self, wrapped):
        @self._property
        @ensure_app_context
        def wrapper(*args):
            kwargs = wrapped(*args)
            kwargs.setdefault('_external', True)
            return url_for(self.endpoint, **kwargs)
        return update_wrapper(wrapper, wrapped)


#: alias for decorator naming
permalink = Permalink
