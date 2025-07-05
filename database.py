import sqlite3
from app import app

def init_db():
    with app.app_context():
        conn = sqlite3.connect(app.config['DATABASE'])
        with app.open_resource('schema.sql', mode='r') as f:
            conn.cursor().executescript(f.read())
        conn.commit()
        print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
