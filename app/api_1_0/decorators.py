from functools import wraps
from flask import g
from .errors import forbidden

def permission_required(permission):
    def decorator(fn):
        @wraps(fn)
        def decorated_func(*args, **kw):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permission')
            return fn(*args, **kw)
        return decorated_func
    return decorator
