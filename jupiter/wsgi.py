from werkzeug.contrib.fixers import ProxyFix
from werkzeug.contrib.profiler import ProfilerMiddleware

from .app import create_app

__all__ = ['app']

#: WSGI endpoint
app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app)

if app.config.get('PROFILING', False):
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app, profile_dir=app.config['PROFILING_DIR'])
