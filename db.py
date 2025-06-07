import sqlite3
from datetime import datetime

DB_PATH = 'instabot.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action_type TEXT NOT NULL,  -- 'like', 'comment', 'error'
            media_id TEXT,
            hashtag TEXT,
            comment TEXT,
            error TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_action(action_type, media_id=None, hashtag=None, comment=None, error=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO actions (timestamp, action_type, media_id, hashtag, comment, error)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.utcnow().isoformat(), action_type, media_id, hashtag, comment, error))
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT action_type, COUNT(*) FROM actions GROUP BY action_type')
    stats = dict(c.fetchall())
    conn.close()
    return stats
