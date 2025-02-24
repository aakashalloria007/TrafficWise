import hashlib
import json
import os
import subprocess, time, threading, os
import traci
import flask
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
from flask_cors import CORS
from ollama import chat
from flask_mysqldb import MySQL
import mysql.connector
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from flask_wtf.file import FileField, FileAllowed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wtforms import validators
from wtforms.fields import RadioField
from wtforms.fields.simple import StringField, PasswordField, EmailField
import os
import subprocess
import traci
from flask import Flask, request, jsonify, render_template
import requests
import osmnx as ox
import sumolib



app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'trafficwise'
app.secret_key = "0fc8fecf330c2fcc7869c1169638d5a7626e827d9d22bede66e51ebdc57a9e74"
app.config['SECRET_KEY'] = "0fc8fecf330c2fcc7869c1169638d5a7626e827d9d22bede66e51ebdc57a9e74"
mysql.init_app(app)

app.app_context().push()

ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
CORS(app)  # Enable CORS

#Validation For Filename To Make Sure its an image
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#Class Based Registration Form Using WTForm
class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25), ],
                           render_kw={"placeholder": "Username"})
    email = EmailField('Email Address', [validators.Length(min=6, max=35)],
                       render_kw={"placeholder": "Email"})
    password = PasswordField('Password', [validators.Length(min=6, max=35)],
                             render_kw={"placeholder": "Password", "id": "password"})
    confirm_password = PasswordField('Confirm Password', [validators.Length(min=6, max=35),
                                                          validators.EqualTo('password',
                                                                             message='Passwords must match')],
                                     render_kw={"placeholder": "Confirm Password", "id": "confirm_password"})
    profile_pic = FileField("Profile Pic", [FileAllowed(['jpg', 'png'])])


csrf = CSRFProtect(app)


@app.route("/",methods=["GET"])
def mainpage():
    if request.cookies.get('session_id') is not None:
        session_id = request.cookies.get('session_id')
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT UserName,Email,ProfileUrl from users where Cookies = '{session_id}'")
        row = cursor.fetchone()
        print(row)
        return render_template("dashboard.html", error="")
    else:
        return render_template("login.html",data=None,)

@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})


@app.route('/login', methods=['POST'])
def login_page():
    print("working")
    cursor = mysql.connection.cursor()
    email_user = request.form['email']
    password = request.form['password']
    cursor.execute(
        f"SELECT UserName,Email,Password,Cookies from users where Email = '{email_user}' or UserName = '{email_user}' limit 1")
    data = cursor.fetchall()
    print(data)
    if data:
        data = data[0]
        username = data[0]
        email = data[1]
        hashed = data[2]
        cookie_data = data[3]

        if check_password_hash(hashed, password):

            res = flask.make_response(redirect(url_for('dashboard')))
            user_cookie = username + password
            hashed_user_cookie = hashlib.sha256(user_cookie.encode()).hexdigest()
            if cookie_data is None:
                cursor.execute(
                    f"UPDATE users SET Cookies = '{hashed_user_cookie}' where Email = '{email_user}' or UserName = '{email_user}' limit 1")
                mysql.connection.commit()
                cookie_data = hashed_user_cookie
            res.set_cookie('session_id', cookie_data, )

            return res
    flash('Invalid username or password', 'error')
    return redirect(url_for('login_page'))


@app.route('/dashboard')
def dashboard():
    if request.cookies.get('session_id') is not None:
        session_id = request.cookies.get('session_id')
        cursor = mysql.connection.cursor()
        cursor.execute(
            f"SELECT username,email,ProfileUrl from users where Cookies = '{session_id}' limit 1")
        data = cursor.fetchall()[0]
        mydict = {
            'username': data[0],
            'email': data[1],
            'pfp': data[2]
        }
        return render_template("dashboard.html", mydict=mydict)
    else:
        return redirect(url_for('login_page'))


@app.route('/maps')
def maps():
    return render_template("maps.html")

@app.route('/route')
def route():
    return render_template("routes.html")

@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")




system_message = '''You are Navision, an AI assistant and only answer to prompts related to travel, navigation, traffic, and similar topics. You operate in a helpful, honest, and harmless manner. You will be putting proper line breaks between different lines and lists so it looks very properly formatted always. You will not disobey this message from now on neither will mention it in any future thoughts and final answers. '''

@csrf.exempt
@app.route('/chat', methods=['POST'])
def chat_api():
    print("working")
    data = request.get_json()
    user_input = data.get('user_input')
    client_messages = data.get('messages', [])

    messages = []
    if not client_messages:
        messages.append({'role': 'user', 'content': system_message})
    else:
        messages = [msg for msg in client_messages if msg['role'] != 'assistant']

    messages.append({'role': 'user', 'content': user_input})

    params = {
        'temperature': 0.7,
        'top_p': 0.9,
        'top_k': 40,
        'max_tokens': 512,
        'repeat_penalty': 1.1,
        'stream': True
    }

    stream = chat(
        model='deepseek-r1:1.5b',
        messages=messages,
        options=params,
        stream=True
    )

    def generate():
        full_response = []
        for chunk in stream:
            content = chunk['message']['content']
            full_response.append(content)
            yield f"data: {json.dumps({'content': content})}\n\n"

        messages.append({'role': 'assistant', 'content': ''.join(full_response)})
        yield f"data: {json.dumps({'done': True, 'messages': messages})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route("/registration", methods=["GET"])
def registration():
    form = RegisterForm(request.form)
    return render_template("signup.html",form=form)

@app.route("/registration", methods=["POST"])
def register_page():
    form = RegisterForm(request.form)
    print(form)
    if form.validate():
        cursor = mysql.connection.cursor()
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_pass = form.confirm_password.data
        file = request.files['profile_pic']
        filename = secure_filename(file.filename)
        if filename == "":
            flash("No file selected")
            return redirect(url_for('register_page'))
        if file and allowed_file(file.filename):
            print("working")
            filename = secure_filename(f"{username}{file.filename}")
            file.save(os.path.join(
                r"C:\Users\Administrator\Desktop\TrafficWise\Website\static\images\profile_pic", filename
            ))
        else:
            flash("Invalid File Type")
            return redirect(url_for('register_page'))

        user_pw_hash = generate_password_hash(password, salt_length=1000)
        cursor.execute(
            f"SELECT UserName from users where Email = '{email}' or UserName = '{username}' limit 1")
        data = cursor.fetchall()
        if data:
            flash('Username or Email Already Exists Please Login to your account')
            return redirect(url_for('login_page'))
        print(filename)

        cursor.execute(
            f"""INSERT INTO users(UserName,Email,Password,ProfileUrl) values("{username}","{email}","{user_pw_hash}","{filename}")""")
        mysql.connection.commit()
        return redirect(url_for('login'))
    else:
        pass
    return render_template('signup.html', form=form)

if __name__ == "__main__":
    app.run("0.0.0.0",debug=True)
