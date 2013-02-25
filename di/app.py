import sqlite3
from contextlib import closing

from flask import Flask, g, session

from di.utils import get_user_id, get_gravatar_url, markdown_text, timestamp_filter


app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.filters['gravatar'] = get_gravatar_url
app.jinja_env.filters['markdown'] = markdown_text
app.jinja_env.filters['timestamp'] = timestamp_filter

from di import views
from di.user import views
from di.thread import views

def connect_db():
    conn = sqlite3.connect(app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'username' in session:
        g.user = {'user_id' : get_user_id(session['username']), 
                  'username' : session['username']}

@app.teardown_request
def teardown_request(exception):
    g.db.close()

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read())
            db.commit()
