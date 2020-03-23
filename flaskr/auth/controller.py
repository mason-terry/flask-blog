from flask import flash, redirect, render_template, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


def register_user(req):
    if req.method == 'POST':
        username = req.form['username']
        password = req.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            user = log_user_in(username)
            store_user_info(user)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/register.html')


def login_user(req):
    if req.method == 'POST':
        username = req.form['username']
        password = req.form['password']
        error = None
        user = log_user_in(username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password(user, password):
            error = 'Incorrect password.'

        if error is None:
            store_user_info(user)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


def log_user_in(username):
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    return user


def check_password(user, password):
    return check_password_hash(user['password'], password)


def store_user_info(user):
    session.clear()
    session['user_id'] = user['id']