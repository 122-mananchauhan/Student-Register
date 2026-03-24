import sqlite3
def get_db_connection():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       email TEXT UNIQUE NOT NULL,
                       username TEXT NOT NULL,
                       password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

print("Database initialized and users table created if it didn't exist.")

get_db_connection()