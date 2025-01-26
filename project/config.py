import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    DATABASE_PATH = os.path.join('data', 'database.db')
