import logging
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functions import user_reply
from twilio_api import send_message
from threading import Thread
import os
import firebase_admin
import json
from firebase_admin import credentials, auth

#initialize the 'firebase_admin' module with the credentials
cred_str = os.environ.get("FIREBASE_CREDENTIALS")
cred_dict = json.loads(cred_str)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

qa = user_reply
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL")
#local db
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Rcsouza24@localhost/finance"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.get_user_by_email(email)
            # Verify user credentials
            auth.verify_password(password, user.password)

            # Log the user in
            login_user(user)
            
            flash('You have logged in successfully!', 'success')
            return redirect(url_for('home'))
        except auth.AuthError as e:
            # Handle authentication error
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']

    #     user = Customer.query.filter_by(username=username).first()
    #     if user and user.check_password(password):
    #         login_user(user)
    #         flash('You have logged in successfully!', 'success')
    #         return redirect(url_for('home'))  # or wherever you want to redirect after login

    #     flash('Invalid username or password', 'error')

    # return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.create_user(email=email, password=password)
            # Additional logic if user creation is successful
            flash('You have signed up successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            # Handle error if user creation fails
            flash('Error creating user: ' + str(e), 'error')
            return redirect(url_for('signup'))
        
    return render_template('signup.html')
    
    
    # if request.method == 'POST':
    #     username = request.form['username']
    #     password = request.form['password']
    #     print(username, password)
    #     existing_user = Customer.query.filter_by(username=username).first()
    #     if existing_user:
    #         flash('Username already exists', 'error')
    #         return redirect(url_for('signup'))

    #     user = Customer(username=username)
    #     user.set_password(password)

    #     db.session.add(user)
    #     db.session.commit()

    #     flash('You have signed up successfully!', 'success')
    #     return redirect(url_for('login'))

    # return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out successfully!', 'success')
    return redirect(url_for('home'))  # or wherever you want to redirect after logout

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')

@app.route("/twilio-test", methods=["POST"])
def twilio_test():
    print(request.form["Body"])
    query = request.form["Body"]
    sender_id = request.form["From"]

    send_message(sender_id, f"you said: {query}")

    return "OK", 200


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

with app.app_context():
    db.create_all()