import sqlite3

conn = sqlite3.connect("main.db", check_same_thread=False)
cur = conn.cursor()

# MAIN TABLES
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    fullname TEXT,
    messages INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS owners (
    user_id INTEGER PRIMARY KEY
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS blocked (
    user_id INTEGER PRIMARY KEY
)
""")

conn.commit()

# ---------------- FUNCTIONS ---------------- #

def add_user(uid, username, fullname):
    cur.execute(
        "INSERT OR REPLACE INTO users (user_id, username, fullname) VALUES (?, ?, ?)",
        (uid, username, fullname)
    )
    conn.commit()

def increment_messages(uid):
    cur.execute("UPDATE users SET messages = messages + 1 WHERE user_id = ?", (uid,))
    conn.commit()

def is_blocked(uid):
    cur.execute("SELECT 1 FROM blocked WHERE user_id=?", (uid,))
    return cur.fetchone() is not None

def block_user(uid):
    cur.execute("INSERT OR REPLACE INTO blocked VALUES (?)", (uid,))
    conn.commit()

def unblock_user(uid):
    cur.execute("DELETE FROM blocked WHERE user_id=?", (uid,))
    conn.commit()

def add_admin(uid):
    cur.execute("INSERT OR REPLACE INTO admins VALUES (?)", (uid,))
    conn.commit()

def remove_admin(uid):
    cur.execute("DELETE FROM admins WHERE user_id=?", (uid,))
    conn.commit()

def get_admins():
    cur.execute("SELECT user_id FROM admins")
    return [row[0] for row in cur.fetchall()]

def add_owner(uid):
    cur.execute("INSERT OR REPLACE INTO owners VALUES (?)", (uid,))
    conn.commit()

def get_owners():
    cur.execute("SELECT user_id FROM owners")
    return [row[0] for row in cur.fetchall()]

def stats():
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM blocked")
    blocked = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM admins")
    admins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM owners")
    owners = cur.fetchone()[0]

    return total_users, blocked, admins, owners
