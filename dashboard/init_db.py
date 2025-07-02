# init_db.py
import sqlite3

def init_db():
    conn = sqlite3.connect('weather.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature FLOAT NOT NULL,
            humidity FLOAT NOT NULL,
            pressure FLOAT
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()