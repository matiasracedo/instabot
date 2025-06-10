import sqlite3

DB_PATH = 'instabot.db'

def print_recent_errors(limit=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, action_type, error
        FROM actions
        WHERE action_type = 'error'
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    errors = c.fetchall()
    conn.close()
    if not errors:
        print("No error logs found.")
    else:
        print(f"Last {len(errors)} error logs:")
        for row in errors:
            print(f"Time: {row[0]} | Type: {row[1]} | Error: {row[2]}")

if __name__ == "__main__":
    print_recent_errors()