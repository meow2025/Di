from flask import g, request, render_template, session, redirect, url_for,\
    flash, abort

from di.app import app
from di.utils import gen_salt, hash_password, get_user_id, redirect_back
from di.decorators import require_login


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    def check_email(email):
        cur = g.db.execute('select 1 from user where email=?', [email])
        row = cur.fetchone()
        return True if row else False

    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        raw_password = request.form['password']
        raw_password2 = request.form['password2']

        if get_user_id(username):
            error = 'username exists!'
        elif check_email(email):
            error = 'email exists!'
        elif raw_password != raw_password2:
            error = '2 password dont match'
        else:
            salt = gen_salt()
            salted_pwd = salt + '.' + hash_password(username, raw_password,
                                                    salt)
            g.db.execute('''insert into user(username, salted_pwd, email)
                            values(?,?,?)''', [username, salted_pwd, email])
            g.db.commit()
            return redirect(url_for('signin'))
    return render_template('signup.html', error=error)

@app.route('/signin', methods=['GET', 'POST'])
def signin(redirect_url=None):
    error = None
    if request.method == 'POST':
        error = 'email/password error'
        email = request.form['email']
        password = request.form['password']

        cur = g.db.execute('select username, salted_pwd from user where email=?', [email])
        result = cur.fetchone()
        if result:
            username, salted_pwd = result
            salt, hashed_password = salted_pwd.split('.')
            if hash_password(username, password, salt) == hashed_password:
                session['username'] = username
                return redirect_back('index')
    return render_template('signin.html', error=error)

@app.route('/signout')
def signout():
    session.pop('username')
    return redirect(url_for('index'))

@app.route('/user/setting', methods=['GET', 'POST'])
@require_login
def user_setting():
    if request.method == 'POST':
        flash('Your info is up to date.')
        return redirect(url_for('user_setting'))
    return render_template('user_setting.html')

@app.route('/user/setting/password', methods=['POST'])
@require_login
def modify_password():
    raw_password = request.form['password']
    raw_password2 = request.form['password2']

    if raw_password != raw_password2:
        flash('2 password dont match.')
    else:
        salt = gen_salt()
        salted_pwd = salt + '.' + hash_password(session['username'],
                                                raw_password, salt)
        g.db.execute('update user set salted_pwd=? where user_id=?',
                     [salted_pwd, g.user['user_id']])
        g.db.commit()
        flash('Password update successful.')
    return redirect(url_for('user_setting'))

@app.route('/user/<username>')
def view_user(username):
    cur = g.db.execute('select * from user where username = ?', [username])
    user = cur.fetchone()
    if not user:
        abort(404)

    cur = g.db.execute('''select * from thread, user 
                          where thread.user_id = user.user_id
                          and thread.user_id = ?
                          order by last_update desc''', [user['user_id']])
    threads = cur.fetchall()
    return render_template('view_user.html', user=user, threads=threads)