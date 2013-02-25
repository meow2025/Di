import urllib
import hashlib
import random

import markdown
from flask import g, request, redirect, url_for


def gen_salt():
    letter = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join([random.choice(letter) for i in range(5)])

def hash_password(username, raw_password, salt):
    return hashlib.md5('%s%s%s' % (username, raw_password, salt)).hexdigest()

def get_user_id(username):
    cur = g.db.execute('select user_id from user where username=?', [username])
    row = cur.fetchone()
    return row[0] if row else None

def get_gravatar_url(email, size = 50):
    gravatar_url = "http://www.gravatar.com/avatar/" + \
        hashlib.md5(email.lower()).hexdigest() + "?" + \
        urllib.urlencode({'d':'identicon', 's':str(size)})
    return gravatar_url

def markdown_text(text):
    return markdown.markdown(text, safe_mode='escape')

def timestamp_filter(timestamp, precise=True):
    if precise:
        return '<span timestamp="%s" precise="true" ></span>' % timestamp
    else:
        return '<span timestamp="%s"></span>' % timestamp

def redirect_back(endpoint, **values):
    referrer = request.referrer if request.url != request.referrer else None
    target = request.args.get('redirect_url', None) or referrer
    if not target:
        target = url_for(endpoint, **values)
    return redirect(target)   