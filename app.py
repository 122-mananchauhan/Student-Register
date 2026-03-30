import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# -------------------------------
# Database connection
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------
# Initialize database
# -------------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# -------------------------------
# Home
# -------------------------------
@app.route('/')
def home():
    return render_template('home.html')


# -------------------------------
# NEW FEATURE: INPUT FORM
# -------------------------------
@app.route('/input')
def input_page():
    return render_template('input.html')


# -------------------------------
# NEW FEATURE: PROCESS INPUT
# -------------------------------
@app.route('/process', methods=['POST'])
def process():
    name = request.form.get('name')
    age = request.form.get('age')

    # Example processing
    message = f"Hello {name}, you are {age} years old!"

    return render_template('result.html', message=message)


# -------------------------------
# Register
# -------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()

        if user:
            conn.close()
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        cursor.execute(
            'INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
            (email, username, password)
        )
        conn.commit()
        conn.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# -------------------------------
# Login
# -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


# -------------------------------
# Dashboard
# -------------------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    pfp = session.get('pfp', 'default.png')

    return render_template('dashboard.html',
                           username=user['username'],
                           pfp=pfp)


# -------------------------------
# View Users Table
# -------------------------------
@app.route('/users')
def users():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, username, email FROM users')
    all_users = cursor.fetchall()

    conn.close()

    return render_template('users.html', users=all_users)


# -------------------------------
# Upload Profile Picture
# -------------------------------
@app.route('/upload_pfp', methods=['POST'])
def upload_pfp():
    if 'user' not in session:
        return redirect(url_for('login'))

    file = request.files.get('pfp')

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['pfp'] = filename

    return redirect(url_for('dashboard'))


# -------------------------------
# Logout
# -------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# -------------------------------
# Run App
# -------------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8000)