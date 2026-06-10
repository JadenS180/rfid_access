from flask import Flask, render_template, request, redirect, url_for, session, flash
import functools
from config import DASHBOARD_PORT, DASHBOARD_HOST, ADMIN_DEFAULT_PIN
from database import (
    get_all_users, get_access_log, enroll_user,
    revoke_user, hash_pin, get_connection
)

app = Flask(__name__)
app.secret_key = 'rfid_dashboard_secret_change_this'

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pin = request.form.get('pin')
        if pin == ADMIN_DEFAULT_PIN:
            session['logged_in'] = True
            return redirect(url_for('index'))
        flash('Invalid PIN')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    logs = get_access_log(50)
    return render_template('index.html', logs=logs)

@app.route('/users')
@login_required
def users():
    all_users = get_all_users()
    return render_template('users.html', users=all_users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        uid = request.form.get('uid')
        pin = request.form.get('pin')
        role = request.form.get('role', 'user')
        allowed_start = request.form.get('allowed_start') or None
        allowed_end = request.form.get('allowed_end') or None

        if not all([name, uid, pin]):
            flash('Name, UID, and PIN are required')
            return render_template('add_user.html')

        success = enroll_user(name, uid, pin, role, allowed_start, allowed_end)
        if success:
            flash(f'User {name} enrolled successfully')
            return redirect(url_for('users'))
        else:
            flash('UID already exists in database')
    return render_template('add_user.html')

@app.route('/users/revoke/<uid>')
@login_required
def revoke(uid):
    revoke_user(uid)
    flash('User revoked')
    return redirect(url_for('users'))

@app.route('/logs')
@login_required
def logs():
    result_filter = request.args.get('result', None)
    conn = get_connection()
    c = conn.cursor()
    if result_filter:
        c.execute('''
            SELECT * FROM access_log
            WHERE result = ?
            ORDER BY timestamp DESC LIMIT 200
        ''', (result_filter,))
    else:
        c.execute('SELECT * FROM access_log ORDER BY timestamp DESC LIMIT 200')
    all_logs = c.fetchall()
    conn.close()
    return render_template('logs.html', logs=all_logs, result_filter=result_filter)

@app.route('/status')
@login_required
def status():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as count FROM users WHERE active = 1')
    active_users = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM access_log WHERE result = 'DENIED' AND timestamp >= datetime('now', '-24 hours')")
    failed_24h = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM access_log WHERE result = 'GRANTED' AND timestamp >= datetime('now', '-24 hours')")
    granted_24h = c.fetchone()['count']
    conn.close()
    return render_template('status.html',
                           active_users=active_users,
                           failed_24h=failed_24h,
                           granted_24h=granted_24h)

if __name__ == '__main__':
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=False)
