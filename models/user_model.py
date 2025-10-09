import sqlite3
import bcrypt
from config import Config

class User:
    def __init__(self, db_path=None):
        self.db_path = db_path or Config.DATABASE_PATH
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def create_user(self, name, email, password):
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                (name, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()

            return {'id': user_id, 'name': name, 'email': email}
        except sqlite3.IntegrityError:
            return None

    def get_user_by_email(self, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, password_hash FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'password_hash': user[3]
            }
        return None

    def verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)
