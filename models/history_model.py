import sqlite3
from config import Config

class History:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                result TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_scan(self, user_id, url, result):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO history (user_id, url, result) VALUES (?, ?, ?)',
            (user_id, url, result)
        )
        conn.commit()
        scan_id = cursor.lastrowid
        conn.close()

        return scan_id

    def get_user_history(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, url, result, timestamp FROM history WHERE user_id = ? ORDER BY timestamp DESC',
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'url': row[1],
                'result': row[2],
                'timestamp': row[3]
            })

        return history
