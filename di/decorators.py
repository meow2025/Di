import functools

from flask import g, redirect, url_for, request

from di.app import app

def require_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kargs):
        if not g.user:
            return redirect(url_for('signin', redirect_url=request.url))
        return func(*args, **kargs)
    return wrapper
