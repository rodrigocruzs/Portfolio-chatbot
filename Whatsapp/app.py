import logging
from flask import Flask, request, redirect, url_for, render_template, flash, request, session, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functions import user_reply
from twilio_api import send_message
from threading import Thread
import os

qa = user_reply
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL")
db = SQLAlchemy(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Define the User model for Flask-Login
class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Customer.query.filter_by(email=email).first()

        if user:
            flash('Email address already exists.')
        else:
            new_user = Customer(name=name, email=email, password=generate_password_hash(password, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('signup.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Customer.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)  # Log in the user
            return redirect(url_for('welcome'))  # Redirect to welcome page
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))  # Redirect back to login page

    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('index.html')

@app.route("/welcome")
@login_required
def welcome():
        return render_template("welcome.html", name=current_user.name)


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
    
if __name__ == '__main__':
    app.run(debug=True)