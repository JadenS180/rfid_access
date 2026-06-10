import sqlite3
import hashlib
import os
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            uid TEXT NOT NULL UNIQUE,
            pin_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            active INTEGER NOT NULL DEFAULT 1,
            allowed_start TEXT DEFAULT NULL,
            allowed_end TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Access log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS access_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            name TEXT,
            result TEXT NOT NULL,
            reason TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Failed attempts table
    c.execute('''
        CREATE TABLE IF NOT EXISTS failed_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def enroll_user(name, uid, pin, role='user', allowed_start=None, allowed_end=None):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (name, uid, pin_hash, role, allowed_start, allowed_end)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, uid.strip(), hash_pin(pin), role, allowed_start, allowed_end))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE uid = ? AND active = 1', (uid.strip(),))
    user = c.fetchone()
    conn.close()
    return user

def verify_pin(user, pin):
    return user['pin_hash'] == hash_pin(pin)

def log_access(uid, name, result, reason=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO access_log (uid, name, result, reason)
        VALUES (?, ?, ?, ?)
    ''', (uid, name, result, reason))
    conn.commit()
    conn.close()

def log_failed_attempt(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO failed_attempts (uid) VALUES (?)', (uid,))
    conn.commit()
    conn.close()

def get_recent_failed_attempts(uid, seconds=60):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT COUNT(*) as count FROM failed_attempts
        WHERE uid = ?
        AND timestamp >= datetime('now', ? || ' seconds')
    ''', (uid, f'-{seconds}'))
    count = c.fetchone()['count']
    conn.close()
    return count

def revoke_user(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET active = 0 WHERE uid = ?', (uid,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = c.fetchall()
    conn.close()
    return users

def get_access_log(limit=100):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM access_log ORDER BY timestamp DESC LIMIT ?', (limit,))
    logs = c.fetchall()
    conn.close()
    return logs
