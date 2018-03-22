# coding: utf-8

from __future__ import print_function, absolute_import

from functools import update_wrapper


_missing = object()


def coerce_type(type_, default=_missing):
    """Coerces the return value of decorated function into specified type.

    Example::

        >>> @coerce_type(list)
        ... def list_one_two():
        ...     yield 1
        ...     yield 2
        >>> list_one_two()
        [1, 2]

    :param type_: The expected type.
    :param default: Optional. The fallback value while :exc:`ValueError`
                    thrown in type coercing.
    """
    def decorator(wrapped):
        def wrapper(*args, **kwargs):
            result = wrapped(*args, **kwargs)
            try:
                return type_(result)
            except ValueError:
                if default is _missing:
                    raise
                else:
                    return default
        return update_wrapper(wrapper, wrapped)
    return decorator


class DelegatedProperty(object):
    """Property delegated to client"""

    def __init__(self, name, to):
        self.name = name
        self.to = to

    def __get__(self, instance, owner):
        if instance is None:
            return self
        delegate_to = getattr(instance, self.to)
        return getattr(delegate_to, self.name)
