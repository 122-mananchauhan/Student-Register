import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for ,session,flash

app = Flask(__name__)


#super secret key for session management (not used in this example but good practice)
app.secret_key = 'supersecretkey'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('home.html')

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
            flash('Email already registered. Please log in.', 'error')
            return "Email already registered. Please log in."
        
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, password))
        conn.commit()
        conn.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password=?', (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return '''Invalid email or password. Please try again.
            <a href="/register">Go back to register </a>'''
    
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    email = session['user']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    # get profile picture from session (default if not uploaded)
    pfp = session.get('pfp', 'default.png')

    return render_template('dashboard.html',
                           username=user['username'],
                           pfp=pfp)


@app.route('/logout')
def logout():
    session.pop('user', None)   
    return redirect(url_for('login'))

@app.route('/upload_pfp', methods=['POST'])
def upload_pfp():
    file = request.files.get('pfp')

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/uploads', filename))

        # Save filename (session or DB)
        session['pfp'] = filename

    return redirect('/dashboard')


if __name__ == '__main__':
    app.run(debug=True,port = 8000)