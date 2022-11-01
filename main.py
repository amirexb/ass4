from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
import requests


app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'

DB_HOST = "localhost"
DB_NAME = "nftdb"
DB_USER = "postgres"
DB_PASS = "Nmobilee1@"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/res', methods=['GET', 'POST'])
def api_function(conn, cursor, token):
  if 'loggedin' in session:

    url = f'https://solana-gateway.moralis.io/nft/mainnet/' + token + '/metadata'
    headers = {"accept": "application/json", "X-API-Key": "u8emWI08OHGRqpKRzmO3Y3gW4OhbTdOdVRuJobooGeSvYRGjep6bmjuIDVu8RqEI"}
    info = requests.get(url, headers=headers)
    cursor.execute(
        "INSERT INTO nft_table1 (token, nftapi) values (" + "'" + token + "'" + "," + "'" + info.text + "'" + ")");
    conn.commit()
    return f''' <p1>Info about your nft: {info.text} </p1> '''
  return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        if request.method == 'POST':

            cursor = conn.cursor()
            token = request.form.get('nftaddress')
            try:
                postgreSQL_select_Query = "SELECT nftapi FROM nft_table1 WHERE token=" + "'" + token + "'" + ";"
                cursor.execute(postgreSQL_select_Query)
                mobile_records = cursor.fetchall()

                if mobile_records == []:
                    api_function(token)
                else:
                    for row in mobile_records:
                        return f''' <h1>Your data from db: {row[0]} </h1>'''
            except:
                return api_function(conn, cursor, token)
            cursor.close()
            conn.close()
        return '''<form method="POST"><div><label>Input address: <input type="text" name="nftaddress"></label></div>
        <input type="submit" value="Input">
                           </form>'''
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                           (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')








if __name__ == "__main__":
    app.run(debug=True)