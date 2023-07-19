import logging
from flask import Flask, request, redirect, url_for, render_template, flash, request, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functions import user_reply
from twilio_api import send_message
from threading import Thread
import os
import json
import firebase_admin
from firebase_admin import credentials, auth, db
#import pyrebase
import traceback
import requests


firebaseConfig = {
  "apiKey": "AIzaSyAUa2iYEwMOCi5urap0RqHjm65LRGMvc8Q",
  "authDomain": "gregai.firebaseapp.com",
  "projectId": "gregai",
  "storageBucket": "gregai.appspot.com",
  "messagingSenderId": "666761336197",
  "appId": "1:666761336197:web:857a6c24248b8e0beee0ec",
  "measurementId": "G-EVTGWKJW0H",
  "databaseURL": "https://gregai-default-rtdb.firebaseio.com/"
}

#initialize the 'firebase_admin' module with the credentials
cred_str = os.environ.get("FIREBASE_CREDENTIALS")
try:
    cred_dict = json.loads(cred_str)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {"databaseURL": "https://gregai-default-rtdb.firebaseio.com/"})
except (ValueError, KeyError, TypeError):
    logging.error("Invalid Firebase credentials")
    raise

#initialize firebase
# firebase = pyrebase.initialize_app(firebaseConfig)
# auth = firebase.auth()
# db = firebase.database()

#Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

qa = user_reply
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_info):
        self.id = user_info.uid
        self.email = user_info.email
        self.name = user_info.display_name


@login_manager.user_loader
def load_user(user_id):
    user_info = auth.get_user(user_id)
    return User(user_info)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        app.logger.info('Request form data: %s', request.form)
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
    #     if not email or not name:
    #         flash("Please fill out all fields", "error")
    #         return redirect(url_for('home'))
    #     else:
    #         return redirect(url_for('welcome', name=name))  # pass name here
    # else:
    #     if person["is_logged_in"] == True:
    #         return redirect(url_for('welcome'))
    #     else:
    #         return render_template('signup.html')

        try:
            #Try creating the user account using the provided data
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            print('Sucessfully created new user: {0}'.format(user_record.uid))
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user_record.email
            person["uid"] = user_record.uid
            person["name"] = user_record.display_name
            login_user(User(user_record))  # login user here
            #Append data to the firebase realtime database
            ref = db.reference('users')
            new_user = ref.child(person["uid"])
            new_user.set({
                'name': name,
                'email': email
            })
            #Go to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            #Log the error
            app.logger.error(traceback.format_exc())
            #If there is any error, redirect to signup
            flash(str(e), "error")
            return redirect(url_for('home'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return render_template('signup.html')
        
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Verify the password using Firebase REST API
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebaseConfig['apiKey']}"
        headers = {"content-type": "application/json"}
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            uid = response.json()['localId']
            user_info = auth.get_user(uid)
            person["is_logged_in"] = True
            person["email"] = user_info.email
            person["uid"] = user_info.uid
            person["name"] = user_info.display_name
            login_user(User(user_info))  # login user here
            return redirect(url_for('welcome'))
        else:
            flash("There was a problem logging in. Please check your email and password.", "error")
            return redirect(url_for('home'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return render_template('login.html')
        

    # if request.method == 'POST':
    #     email = request.form['email']
    #     password = request.form['password']


    #     try:
    #         user_info = auth.get_user_by_email(email)
    #         login_user(User(user_info))  # login user here
    #         return redirect(url_for('welcome'))
    #     except Exception as e:
    #         flash("There was a problem logging in. Please check your email.", "error")
    #         return redirect(url_for('home'))
    # else:
    #     return render_template('login.html')


    #     try:
    #         user = auth.get_user_by_email(email)
    #         # the below line is pseudo-code, replace it with the actual password verification method you use
    #         if not check_password_hash(user.password, password):  
    #             flash("There was a problem logging in. Please check your email and password.", "error")
    #             return redirect(url_for('home'))
    #         else:
    #             # if password verification is successful
    #             person["is_logged_in"] = True
    #             person["email"] = user.email
    #             person["uid"] = user.uid
    #             person["name"] = user.display_name
    #             login_user(User(user.uid))  # login user here
    #             return redirect(url_for('welcome'))
    #     except Exception as e:
    #         print(e)
    #         flash("There was a problem logging in. Please check your email and password.", "error")
    #         return redirect(url_for('home'))
    # else:
    #     if person["is_logged_in"] == True:
    #         return redirect(url_for('welcome'))
    #     else:
    #         return render_template('login.html')
    

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    app.logger.info(f"Current user is_authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        logout_user()
        global person
        person["is_logged_in"] = False
        flash('You have logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')

@app.route("/welcome")
@login_required
def welcome():
        name = person["name"] if person["is_logged_in"] else 'Guest'  # Use 'Guest' as the default name
        return render_template("welcome.html", name=name)


@app.route("/twilio", methods=["POST"])
def twilio():
    logging.info(request.form["Body"])
    query = request.form["Body"]
    sender_id = request.form["From"]
    logging.info(f"{sender_id}, {query}")

    def target(sender_id: str, query: str):
        user_input = {"input": query}
        res = qa(user_input=user_input)
        send_message(sender_id, res)

    thread = Thread(target=target, args=(sender_id, query))
    thread.start()

    return "OK", 200