from .models import Permission
from flask import abort
from functools import wraps
from flask_login import current_user

def permission_required(permission):
    def decrator(fn):
        @wraps(fn)
        def decrated_func(*args, **kw):
            if current_user.can(permission):
                return fn(*args, **kw)
            abort(403)
        return decrated_func
    return decrator
    
def admin_required(fn):
    return permission_required(Permission.ADMINISTER)(fn)
    
