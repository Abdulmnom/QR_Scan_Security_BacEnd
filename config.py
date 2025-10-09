import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_SAFE_BROWSING_KEY = os.getenv('GOOGLE_SAFE_BROWSING_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key-change-in-production')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/db.sqlite3')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
