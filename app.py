from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
from flask_session import Session
from flask_cors import CORS
import psycopg2
from datetime import datetime, timedelta
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from time import sleep
import json

app = Flask(__name__)
app.secret_key = 'yaani_mahar'
CORS(app, resources={r"*": {"origins": "*"}})
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

app.config["SESSION_PERMANENT"] = True
Session(app)

# with app.app_context():
# session.modified = True
# session.permanent = True

# database details 

db_name = "flask_db"
db_user = "postgres"
db_password = "Kevin"
db_host = "localhost"
db_port = "5435"

conn = psycopg2.connect(database=db_name, user=db_user,
                        password=db_password, host=db_host, port=db_port)

# class Todo(db.Model):
#     sno = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(200), nullable=False)
#     desc = db.Column(db.String(500), nullable=False)
#     title = db.Column(db.DateTime, nullable=False, default = datetime.utcnow)

#     def __repr__(self) -> str:
#         return f"{self.sno} - {self.title}"




# @app.route('/')
# def hello_world():
#     cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
#         account = cursor.fetchone()
#         # Show the profile page with account info
#         return render_template('profile.html', account=account)
#     return redirect(url_for('register'))


@app.route('/get_all_users')
def get_all_users():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    users_dict = []
    for user in users:
        users_dict.append({"id":user[0], "fullName":user[1], "username":user[2],"password":user[3], "email":user[4]})
    # Show the profile page with account info
    json_data = json.dumps(users_dict, indent=2)
    # resp = jsonify(json_data)
    return json_data

@app.route('/deleteuser/<int:id>')
def deleteuser(id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    resp = ""
    try:
        cursor.execute('DELETE FROM users WHERE id=%s;', (id,))
        resp = jsonify({'status_code' : 200})

    except:
        resp = jsonify({'status_code' : 400})

    return resp

@app.route('/edituser/<int:id>', methods=['POST', 'GET'])
def edituser(id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        _json = request.json
        email = _json['email']
        password = _json['password']
        fullname = _json['fullname']
        username = _json['username']

        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchall()
        if len(account)>1:
            resp = jsonify({'message' : 'Account already exists! Change Username/Email! '})
            return resp
        else:
            if password:
                _hashed_password = generate_password_hash(password)
                cursor.execute('UPDATE users SET  email= %s, fullname=%s, username=%s, password=%s WHERE id = %s', (email,fullname,username,_hashed_password, id))
            else:
                cursor.execute('UPDATE users SET  email= %s, fullname=%s, username=%s WHERE id = %s', (email,fullname,username, id))
            conn.commit()

            resp = jsonify({'message' : 'DONE! '})
            return resp


    else:

    
        # Check if user is loggedin
        # try:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (id,))
        user = cursor.fetchone()

        user_dict = {"id":user[0], "fullName":user[1], "username":user[2],"password":user[3], "email":user[4]}
        json_data = json.dumps(user_dict, indent=2)

        return json_data


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    # if request.method == "POST":
    #     fullname = request.form['full_name']
    #     username = request.form['username']
    #     password = request.form['password']
    #     email = request.form['email_address']
    #     print(fullname)
    #     print(username)
    #     print(password)
    #     print(email)
    if request.method == 'POST' and 'username' in request.json and 'password' in request.json and 'email' in request.json:
        # Create variables for easy access
        _json = request.json
        email = _json['email']
        password = _json['password']
        fullname = _json['fullname']
        username = _json['username']


        _hashed_password = generate_password_hash(password)

        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            resp = jsonify({'message' : 'Account already exists! Change Email! '})
            return resp
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            resp = jsonify({'message' : 'Invalid email address!'})
            return resp
        elif not re.match(r'[A-Za-z0-9]+', username):
            resp = jsonify({'message' : 'Username must contain only characters and numbers!'})
            return resp
        elif not username or not password or not email:
            resp = jsonify({'message' : 'Please fill out the form!'})
            return resp
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()
            resp = jsonify({'message' : 'You have successfully registered!'})
            return resp
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        resp = jsonify({'message' : 'Please fill out the form!'})
        return resp
    # Show registration form with message (if any)
    # return render_template('register.html')



# @app.route('/')
# def home():
#     if 'username' in session:
#         username = session['username']
#         return jsonify({'message' : 'You are already logged in', 'username' : username})
#     else:
#         resp = jsonify({'message' : 'Unauthorized'})
#         resp.status_code = 401
#         return resp


@app.route('/login', methods=['POST'])
def login():
    _json = request.json
    _email = _json['email']
    _password = _json['password']
    # print(_json)
    # validate the received values
    if _email and _password:
        try:
        #check user exists          
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            sql = "SELECT * FROM users WHERE email=%s"
            sql_where = (_email,)
            
            cursor.execute(sql, sql_where)
            row = cursor.fetchone()
            email = row['email']
            password = row['password']
            if row:
                if check_password_hash(password, _password):
                    # session['email'] = email
                    cursor.close()
                    return jsonify({'message' : 'You are logged in successfully', 'email': email, 'username':row['username'], 'fullName':row['fullname'] , 'status_code': 200})
                else:
                    resp = jsonify({'message' : 'Bad Request - invalid password', 'status_code': 400})
                    resp.status_code = 400
                    return resp
        except:
            resp = jsonify({'message' : 'Account Not Found' , 'status_code': 400})
            resp.status_code = 400
            return resp
    else:
        resp = jsonify({'message' : 'Bad Request - invalid credendtials'})
        resp.status_code = 400
        return resp



# @app.route('/check', methods=['POST', 'GET'])
# def check():
#     if 'email' in session:
#         email = session['email']
        
#         return jsonify({'message' : 'You are already logged in', 'email' : email})
#     else:
#         resp = jsonify({'message' : 'Unauthorized'})
#         resp.status_code = 401
#         return resp


if __name__ == "__main__":
    app.secret_key = 'yaani_mahar'
    app.config['SESSION_TYPE'] = 'yaani_mahar'
    app.run(debug=True, port=8000)