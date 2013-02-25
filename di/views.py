import time
from flask import g, request, render_template, abort, session, redirect,\
    url_for, flash

from di.app import app
from di.utils import gen_salt, hash_password, get_user_id, get_gravatar_url
from di.decorators import require_login


@app.route('/')
def index():
    cur = g.db.execute('''select * from thread, user 
                          where thread.user_id = user.user_id
                          order by last_update desc''')
    threads = cur.fetchall()
    cur = g.db.execute('select tag_name from tag')
    tags = [row[0] for row in cur.fetchall()]
    return render_template('index.html', threads=threads, tags=tags)

@app.route('/tag/<tag_name>')
def list_thread(tag_name):
    cur = g.db.execute('select tag_id from tag where tag_name=?', [tag_name])
    result = cur.fetchone()
    if not result:
        abort(404)
    tag_id = result[0]
    cur = g.db.execute('''select * from thread, thread_tag, user
                          where thread.thread_id = thread_tag.thread_id
                          and tag_id = ? and thread.user_id = user.user_id
                          order by last_update desc''', [tag_id])
    threads = cur.fetchall()
    return render_template('index.html', threads=threads)
