from flask import Flask, render_template, request, redirect, url_for ,session

app = Flask(__name__)

# Store users properly
users = {"mananchauhan@gmail.com": {'username': 'manan' , 'password': '1234'}
         , "yash@gmail.com": {'username': 'yash', 'password': 'yash'}}   # format: {email: {username, password}}

#super secret key for session management (not used in this example but good practice)
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if email in users:
            return "Email already registered. Please log in."
        
        users[email] = {'username': username, 'password': password}
        
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # user = users.get(email)
        if email in users and users[email]['password'] == password:
            session['user'] = email  
            return redirect(url_for('dashboard'))
        else:
            return '''Invalid email or password. Please try again.
            <a href="/register">Go back to register </a>'''
    
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    email = session['user']
    
    return render_template('dashboard.html',user=users[email]['username'])


@app.route('/logout')
def logout():
    session.pop('user', None)   
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)