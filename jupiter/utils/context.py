from functools import update_wrapper

from flask import current_app, _request_ctx_stack

from ..app import create_app


__all__ = ['ensure_app_context']


def ensure_app_context(wrapped):
    """Ensures the decorated function will be executed inside an app context.

    Example::

        @ensure_app_context
        def print_home_url():
            url = url_for('home.home', _external=True)
            print(url)
    """
    def wrapper(*args, **kwargs):
        if current_app and current_app.name == 'jupiter.app':
            return wrapped(*args, **kwargs)
        current_request_context = _request_ctx_stack.pop()
        try:
            with create_app().app_context():
                value = wrapped(*args, **kwargs)
        finally:
            if current_request_context is not None:
                current_request_context.push()
        return value

    return update_wrapper(wrapper, wrapped)
