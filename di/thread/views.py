import time
import re

from flask import g, request, render_template, abort, session, redirect,\
    url_for, flash

from di.app import app
from di.utils import get_gravatar_url, redirect_back
from di.decorators import require_login
from di.notification import Notification, MENTION, NEW_REPLY
from .utils import find_mentions

def get_replies(thread_id):
    cur = g.db.execute('''select u.username, u.email, reply.text,
                          reply.pub_date from reply, user u
                          where thread_id = ?
                          and u.user_id = reply.user_id''', [thread_id])

    replies = cur.fetchall()
    return replies

def create_tag_if_not_exist(tag_name):
    g.db.execute('insert or ignore into tag(tag_name) values(?)', [tag_name])
    g.db.commit()
    cur = g.db.execute('select tag_id from tag where tag_name=?', [tag_name])
    tag_id = cur.fetchone()[0]
    return tag_id

def mark(thread_id, notify=0):
    '''mark thread, the notification is unset by default'''
    mark_time = int(time.time())

    g.db.execute('insert into mark(thread_id, user_id, mark_time, notify) values(?,?,?,?)',
                 [thread_id, g.user['user_id'], mark_time, notify])
    g.db.commit()


@app.route('/thread/create', methods=['GET', 'POST'])
@require_login
def create_thread():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        user_id = g.user['user_id']
        pub_date = int(time.time())
        cur = g.db.execute('''insert into thread(user_id, title, text,
                              pub_date, last_update) values(?,?,?,?,?)''',
                           [user_id, title, text, pub_date, pub_date])
        g.db.commit()
        thread_id = cur.lastrowid

        #process the tags
        tags = request.form['tags'].split(',')
        for tag in tags:
            if tag:
                tag_id = create_tag_if_not_exist(tag)
                g.db.execute('insert into thread_tag values(?,?)', [thread_id,
                                                                    tag_id])

        g.db.commit()

        #mark the thread and set notify
        mark(thread_id, notify=1)

        return redirect(url_for('view_thread', thread_id=thread_id))
    return render_template('create_thread.html')

@app.route('/thread/<int:thread_id>')
def view_thread(thread_id):
    cur = g.db.execute('''select thread_id, title, text, username, email, pub_date,
                          click, reply from thread, user  where thread_id = ?
                          and thread.user_id = user.user_id''', [thread_id])
    thread = cur.fetchone()
    if not thread:
        abort(404)

    #process tags
    cur = g.db.execute('''select tag_name from tag, thread_tag
                          where thread_id = ? and
                          tag.tag_id = thread_tag.tag_id''', [thread_id])
    tags = [row[0] for row in cur.fetchall()]

    #inc click
    g.db.execute('update thread set click = click + 1 where thread_id = ?',
                 [thread_id])
    g.db.commit()

    #get mark state
    is_mark = False
    if g.user:
        cur = g.db.execute('select * from mark where thread_id = ? and user_id = ?',
                           [thread_id, g.user['user_id']])
        is_mark = True if cur.fetchone() else False

        #set notifications to read
        g.db.execute('''update notification set is_read = 1 
                        where user_id = ? and thread_id = ?
                        and is_read = 0''',
                      [g.user['user_id'], thread_id])
        g.db.commit()

    return render_template('view_thread.html', thread=thread, tags=tags,
                           is_mark=is_mark, replies=get_replies(thread_id))


@app.route('/reply/create', methods=['POST'])
@require_login
def create_reply():
    thread_id = request.form['thread_id'] #todo:check
    text = request.form['text']
    notify_me = request.form.getlist('notify_me')
    pub_date = int(time.time())

    g.db.execute('''insert into reply(thread_id,user_id,text,pub_date)
                    values(?,?,?,?)''', [thread_id, g.user['user_id'], text, pub_date])
    g.db.execute('update thread set reply = reply + 1, last_update = ? where thread_id = ?',
                 [pub_date, thread_id])
    g.db.commit()

    #get other users who mark this thread and notify field is set
    cur = g.db.execute('select user_id from mark where thread_id = ? and notify = 1',
                       [thread_id])
    user_ids = [row[0] for row in cur.fetchall() if row[0] != g.user['user_id']]

    #send notifications
    for user_id in user_ids:
        n = Notification(user_id, thread_id, NEW_REPLY, g.user['user_id'])
        n.send()

    #mention
    mention_usernames = find_mentions(text)
    if mention_usernames:
        for username in mention_usernames:
            cur = g.db.execute('select user_id from user where username = ?',
                         [username])
            result = cur.fetchone()
            if result:
                user_id = result[0]
                n = Notification(user_id, thread_id, MENTION, g.user['user_id'])
                n.send()

    #set the mark
    if notify_me:
        mark(thread_id, notify=1)

    flash('Reply success!')
    return redirect(url_for('view_thread', thread_id=thread_id))

@app.route('/mark/thread/<int:thread_id>')
@require_login
def mark_thread(thread_id):
    mark(thread_id)
    flash('Mark success!')
    return redirect(url_for('view_thread', thread_id=thread_id))

@app.route('/unmark/thread/<int:thread_id>')
@require_login
def unmark_thread(thread_id):
    g.db.execute('delete from mark where thread_id = ? and user_id = ?',
                 [thread_id, g.user['user_id']])
    g.db.commit()
    flash('Unmark success!')
    return redirect_back('view_thread', thread_id=thread_id)

@app.route('/mark')
@require_login
def list_marked():
    cur = g.db.execute('''select * from thread, user, mark
                          where mark.thread_id = thread.thread_id
                          and mark.user_id = ?
                          and thread.user_id = user.user_id
                          order by mark_time desc
                       ''', [g.user['user_id']])
    threads = cur.fetchall()
    return render_template('list_marked.html', threads=threads)

@app.route('/notification')
@require_login
def list_notification():
    cur = g.db.execute('''select * from thread t, notification n, user u
                          where t.thread_id = n.thread_id and n.user_id = ?
                          and u.user_id = n.other_user_id
                          order by time desc''', [g.user['user_id']])
    notifications = cur.fetchall()
    return render_template('list_notification.html', notifications=notifications)

@app.route('/notification/count')
@require_login
def count_notification():
    cur = g.db.execute('''select count(*) from notification n 
                          where n.user_id = ? and n.is_read = 0''',
                       [g.user['user_id']])
    count = cur.fetchone()[0]
    return str(count)
