import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_SAFE_BROWSING_KEY = os.getenv('GOOGLE_SAFE_BROWSING_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key-change-in-production')
    DATABASE_URL = os.getenv('DATABASE_URL')  # PostgreSQL URL من Render
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/db.sqlite3')  # للتطوير المحلي
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24

def get_db_connection():
    """Helper function to get a database connection."""
    if Config.DATABASE_URL:
        # استخدام PostgreSQL في الإنتاج (Render)
        conn = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        # استخدام SQLite في التطوير المحلي
        import sqlite3
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables if they don't exist."""
    conn = get_db_connection()

    if Config.DATABASE_URL:
        # PostgreSQL (إنتاج)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                url TEXT NOT NULL,
                result TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        # SQLite (تطوير محلي)
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
