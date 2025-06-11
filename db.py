import sqlite3
from datetime import datetime

DB_PATH = 'instabot.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Add post_link column if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        action_type TEXT NOT NULL,  -- 'like', 'comment', 'error'
        media_id TEXT,
        hashtag TEXT,
        comment TEXT,
        error TEXT,
        post_link TEXT
    )''')
    # Try to add post_link column if missing (for existing DBs)
    try:
        c.execute('ALTER TABLE actions ADD COLUMN post_link TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

def log_action(action_type, media_id=None, hashtag=None, comment=None, error=None, post_link=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO actions (timestamp, action_type, media_id, hashtag, comment, error, post_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.utcnow().isoformat(), action_type, media_id, hashtag, comment, error, post_link))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT action_type, COUNT(*) FROM actions GROUP BY action_type')
    stats = dict(c.fetchall())
    conn.close()
    return stats
