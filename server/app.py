import logging
from db import db, init_app, Customer, InvestmentSecurity, InvestmentHolding, InvestmentTransaction, InvestmentView, BankAccount, PlaidItem
from flask import Flask, request, redirect, url_for, render_template, flash, request, jsonify, abort, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from functions import stock_analysis
from twilio_api import send_message
from threading import Thread
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.investments_transactions_get_request_options import InvestmentsTransactionsGetRequestOptions
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.api import plaid_api
import logging
import os
import datetime as dt
from datetime import datetime, timedelta
import json
import time
import plaid
import stripe

qa = stock_analysis
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='../client', template_folder='../client/html')
app.secret_key = os.environ.get("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL")

init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

#Setting up the Logger:
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

# Configure Plaid API
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
# Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# password: pass_good)
# Use `development` to test with live users and credentials and `production`
# to go live
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

# Configure Stripe API
stripe.api_key = "sk_test_51NrlkKCp04lVZoC1b8GqGpTbToP3ql8zMDzSpoD6GdvCJ8Y3YCfk6MtKmkQFt86vEdHUDPOXG5uH3PURm4qqQ1jJ00XOcyAgm6"
STRIPE_ENDPOINT_SECRET = os.environ.get('STRIPE_ENDPOINT_SECRET')

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'development':
    host = plaid.Environment.Development

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = plaid.Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

# We store the access_token in memory - in production, store it in a secure
# persistent data store.
access_token = None
# The payment_id is only relevant for the UK Payment Initiation product.
# We store the payment_id in memory - in production, store it in a secure
# persistent data store.
payment_id = None
# The transfer_id is only relevant for Transfer ACH product.
# We store the transfer_id in memory - in production, store it in a secure
# persistent data store.
transfer_id = None

item_id = None


def update_investment_view_from_holding(holding: InvestmentHolding):
    # Find the related InvestmentSecurity and BankAccount records
    security = InvestmentSecurity.query.filter_by(security_id=holding.security_id).first()
    bank_account = BankAccount.query.filter_by(user_id=holding.user_id).first()

    # Find existing InvestmentView record or create a new one
    investment_view = InvestmentView.query.filter_by(
        user_id=holding.user_id, 
        account_id=holding.account_id, 
        security_id=holding.security_id
    ).first()

    if investment_view is None:
        investment_view = InvestmentView()
        db.session.add(investment_view)

    # Update the InvestmentView record
    investment_view.user_id = holding.user_id
    investment_view.account_id = holding.account_id
    investment_view.security_id = holding.security_id
    investment_view.quantity = holding.quantity
    investment_view.institution_price = holding.institution_price
    investment_view.institution_price_currency = holding.institution_price_currency
    investment_view.institution_value = holding.institution_value
    investment_view.institution_value_currency = holding.institution_value_currency
    investment_view.cost_basis = holding.cost_basis
    investment_view.name = security.name if security else None
    investment_view.type = security.type if security else None
    investment_view.ticker_symbol = security.ticker_symbol if security else None
    investment_view.account_name = bank_account.account_name if bank_account else None
    investment_view.account_mask = bank_account.account_mask if bank_account else None
    investment_view.account_subtype = bank_account.account_subtype if bank_account else None

    db.session.commit()

def update_investment_view_from_security(security: InvestmentSecurity):
    # Find all InvestmentHolding and BankAccount records related to this security
    holdings = InvestmentHolding.query.filter_by(security_id=security.security_id).all()
    bank_accounts = {bank_account.user_id: bank_account for bank_account in BankAccount.query.all()}

    for holding in holdings:
        # Find existing InvestmentView record or create a new one
        investment_view = InvestmentView.query.filter_by(
            user_id=holding.user_id, 
            account_id=holding.account_id, 
            security_id=holding.security_id
        ).first()

        if investment_view is None:
            investment_view = InvestmentView()
            db.session.add(investment_view)

        # Update the InvestmentView record
        bank_account = bank_accounts.get(holding.user_id)
        investment_view.name = security.name
        investment_view.type = security.type
        investment_view.ticker_symbol = security.ticker_symbol
        investment_view.account_name = bank_account.account_name if bank_account else None
        investment_view.account_mask = bank_account.account_mask if bank_account else None
        investment_view.account_subtype = bank_account.account_subtype if bank_account else None

        db.session.commit()
    
def update_investment_view_from_bank_account(bank_account: BankAccount):
    # Find all InvestmentHolding and InvestmentSecurity records related to this bank account
    holdings = InvestmentHolding.query.filter_by(user_id=bank_account.user_id).all()
    securities = {security.security_id: security for security in InvestmentSecurity.query.all()}

    for holding in holdings:
        # Find existing InvestmentView record or create a new one
        investment_view = InvestmentView.query.filter_by(
            user_id=holding.user_id, 
            account_id=holding.account_id, 
            security_id=holding.security_id
        ).first()

        if investment_view is None:
            investment_view = InvestmentView()
            db.session.add(investment_view)

        # Update the InvestmentView record
        security = securities.get(holding.security_id)
        investment_view.account_name = bank_account.account_name
        investment_view.account_mask = bank_account.account_mask
        investment_view.account_subtype = bank_account.account_subtype
        investment_view.name = security.name if security else None
        investment_view.type = security.type if security else None
        investment_view.ticker_symbol = security.ticker_symbol if security else None

        db.session.commit()


def update_account_info(user_id):
    with current_app.test_request_context():
        # Mock current_user to be the user defined by user_id
        
        user = Customer.query.get(user_id)
        login_user(user)

        # Calling your routes to update data
        get_accounts()
        get_holdings()
        get_investments_transactions()

        # Updating the PlaidItem last_updated field
        plaid_item = PlaidItem.query.filter_by(user_id=user_id).first()
        if plaid_item:  # Check if plaid_item is not None before updating it
            plaid_item.last_updated = datetime.utcnow()
            db.session.commit()


# Flask Routes
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
            new_user = Customer(name=name, email=email)
            new_user.set_password(password) 

            # Set the subscription end date to 7 days from now
            new_user.subscription_end_date = datetime.utcnow() + timedelta(days=7)

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

        if user:
            if user.check_password(password):
                if user.in_trial_period() or user.is_premium:
                    login_user(user)  # Log in the user with active trial or subscription
                    
                    # Fetch the latest data from Plaid for the user
                    update_account_info(user.id)

                    return redirect(url_for('chat'))  # Redirect to chat page
                else:
                    return redirect(url_for('subscribe_page'))  # Redirect to subscription page
            else:
                flash('Invalid email or password')
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('home.html')

@app.route('/subscribe')
def subscribe_page():
    return render_template('subscribe.html')

@app.route("/chat", strict_slashes=False)
@login_required
def chat():
    # Calculate the number of days left in the trial period
    trial_period_days = 7  # Adjust this value as per your trial period duration
    trial_end_date = current_user.subscription_start_date + timedelta(days=trial_period_days)
    days_left = (trial_end_date - datetime.utcnow()).days

    # Check if the trial period has ended
    if days_left < 0:
        days_left = 0

    # Determine if the user is a premium user
    is_premium_user = current_user.is_premium

    # If the user does not have access, redirect them to the subscription page
    if not is_premium_user and days_left <= 0:
        return redirect(url_for('subscribe_page'))

    # If the user has access (either through an active trial or a subscription), allow them to access the chat
    return render_template("chat.html", name=current_user.name, days_left=days_left, is_premium_user=is_premium_user)

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

@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            products=products,
            client_name="GregAI",
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            )
        )
        if PLAID_REDIRECT_URI!=None:
            request['redirect_uri']=PLAID_REDIRECT_URI
    # create link token
        response = client.link_token_create(request)
        return jsonify(response.to_dict())
    except plaid.ApiException as e:
        return json.loads(e.body), 500

# Route to exchange public_token for an access_token
@app.route('/api/set_access_token', methods=['POST'])
def get_access_token():
    # global access_token
    # global item_id
    # global transfer_id
    public_token = request.json['public_token']

    # Get user_id from the session or other authentication mechanism
    user_id = current_user.get_id()

    if not user_id:
        return jsonify({'error': 'User not authenticated'}), 403

    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']
        
        # Find existing PlaidItem or create a new one
        plaid_item = PlaidItem.query.filter_by(user_id=user_id, item_id=item_id).first()
        if plaid_item:
            # Update existing PlaidItem
            plaid_item.access_token = access_token
        else:
            # Create a new PlaidItem
            plaid_item = PlaidItem(
                user_id=user_id,
                access_token=access_token,
                item_id=item_id,
                last_updated=datetime.utcnow()
            )
            db.session.add(plaid_item)

        # Commit the changes to the database
        db.session.commit()

        return jsonify(exchange_response.to_dict())

    except plaid.ApiException as e:
        return json.loads(e.body), 500
    

# Retrieve high-level information about an Item
# https://plaid.com/docs/#retrieve-item

@app.route('/api/item', methods=['GET'])
def item():
    try:
        request = ItemGetRequest(access_token=access_token)
        response = client.item_get(request)
        request = InstitutionsGetByIdRequest(
            institution_id=response['item']['institution_id'],
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES))
        )
        institution_response = client.institutions_get_by_id(request)
        pretty_print_response(response.to_dict())
        pretty_print_response(institution_response.to_dict())
        return jsonify({'error': None, 'item': response.to_dict()[
            'item'], 'institution': institution_response.to_dict()['institution']})
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

def pretty_print_response(response):
  print(json.dumps(response, indent=2, sort_keys=True, default=str))

def format_error(e):
    response = json.loads(e.body)
    return {'error': {'status_code': e.status, 'display_message':
                      response['error_message'], 'error_code': response['error_code'], 'error_type': response['error_type']}}


# Retrieve an Item's accounts
# https://plaid.com/docs/#accounts

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        # Retrieve the access_token for the current user
        plaid_item = PlaidItem.query.filter_by(user_id=current_user.id).first()
        if not plaid_item:
            return jsonify({'error': 'PlaidItem not found for the current user'}), 404
        
        access_token = plaid_item.access_token
        request = AccountsGetRequest(
            access_token=access_token
        )
        response = client.accounts_get(request)
        app.logger.info(f"Accounts Data: {response.to_dict()}")

        accounts = response['accounts']
        for account in accounts:
            # Check if the account already exists for the current user
            existing_account = BankAccount.query.filter_by(user_id=current_user.id, 
                                                           account_name=account['name'], 
                                                           account_mask=account['mask']).first()
            
            if not existing_account:
                # If not, create a new BankAccount object
                # Ensure that 'type' is of string type
                bank_account_type = str(account['type']) if hasattr(account, 'type') else None
                bank_account_subtype = str(account['subtype']) if hasattr(account, 'subtype') else None

                new_account = BankAccount(
                    user_id=current_user.id,
                    account_id=account['account_id'],
                    account_name=account['name'],
                    account_mask=account['mask'],
                    account_type=bank_account_type,
                    account_subtype=bank_account_subtype,
                    available_balance=account['balances']['available'],
                    current_balance=account['balances']['current'],
                    currency_code=account['balances']['iso_currency_code']
                )
                try:
                    db.session.add(new_account)
                    db.session.commit()
                    update_investment_view_from_bank_account(new_account)
                except Exception as e:
                    print(f"Error saving bank account: {e}")
                    db.session.rollback()
            else:
                # If exists, update the account details if needed
                existing_account.account_type = account['type']
                existing_account.account_subtype = account['subtype']
            
        
        
        return jsonify(response.to_dict())
        
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)
    except Exception as e:
        db.session.rollback()  # Roll back any changes in case of errors
        return jsonify({'error': str(e), 'accounts': None})

# Retrieve investment holdings data for an Item
# https://plaid.com/docs/#investments

@app.route('/api/holdings', methods=['GET'])
def get_holdings():
    plaid_item = PlaidItem.query.filter_by(user_id=current_user.id).first()
    if not plaid_item:
        return jsonify({'error': 'PlaidItem not found for the current user'}), 404

    access_token = plaid_item.access_token

    try:
        request = InvestmentsHoldingsGetRequest(access_token=access_token)
        response = client.investments_holdings_get(request)

        # Sync Investment Securities
        securities = response['securities']
        for security in securities:
            existing_security = InvestmentSecurity.query.filter_by(security_id=security['security_id'], user_id=current_user.id).first()
            if not existing_security:
                new_security = InvestmentSecurity(
                    user_id=current_user.id,
                    security_id=security['security_id'],
                    name=security['name'],
                    type=security['type'],
                    ticker_symbol=security.get('ticker_symbol', None),  # Using get() in case 'ticker_symbol' isn't present in the API response
                    iso_currency_code=security['iso_currency_code'],
                    close_price=security['close_price'],
                    close_price_as_of=security['close_price_as_of'],
                    unofficial_currency_code=security.get('unofficial_currency_code', None)  # Using get() for the same reason
                )
                db.session.add(new_security)
                update_investment_view_from_security(new_security)

        # Sync Investment Holdings
        holdings = response['holdings']
        for holding in holdings:
            existing_holding = InvestmentHolding.query.filter_by(account_id=holding['account_id'], security_id=holding['security_id'], user_id=current_user.id).first()
            if not existing_holding:
                new_holding = InvestmentHolding(
                    user_id=current_user.id,
                    account_id=holding['account_id'],
                    security_id=holding['security_id'],
                    quantity=holding['quantity'],
                    institution_price=holding['institution_price'],
                    institution_price_currency=holding.get('institution_price_currency', holding['iso_currency_code']), # Assuming the main currency is the default
                    institution_value=holding['institution_value'],
                    institution_value_currency=holding.get('institution_value_currency', holding['iso_currency_code']), # Same assumption
                    cost_basis=holding['cost_basis'],
                    cost_basis_currency=holding.get('cost_basis_currency', holding['iso_currency_code']), # Same assumption
                    iso_currency_code=holding['iso_currency_code'],
                    unofficial_currency_code=holding.get('unofficial_currency_code', None),  # Using get() for potential missing values
                )
                db.session.add(new_holding)
                update_investment_view_from_holding(new_holding)

        db.session.commit()
        return jsonify(response.to_dict())
    
    except plaid.ApiException as e:
        error_response = format_error(e)
        logger.error(f"Plaid API Exception: {error_response}")
        return jsonify(error_response)
    except Exception as e:
        db.session.rollback()
        logger.error(f"General Exception: {str(e)}")
        return jsonify({'error': str(e), 'holdings': None})
    
# Retrieve Investment Transactions for an Item
# https://plaid.com/docs/#investments


@app.route('/api/investments_transactions', methods=['GET'])
def get_investments_transactions():
    # Pull transactions for the last 30 days
    start_date = (dt.datetime.now() - dt.timedelta(days=(30)))
    end_date = dt.datetime.now()

    # Retrieve the access_token for the current user
    plaid_item = PlaidItem.query.filter_by(user_id=current_user.id).first()
    if not plaid_item:
        return jsonify({'error': 'PlaidItem not found for the current user'}), 404
    
    

    access_token = plaid_item.access_token
    app.logger.info(f'Access token retrieved: {access_token}')

    try:
        options = InvestmentsTransactionsGetRequestOptions()
        request = InvestmentsTransactionsGetRequest(
            access_token=access_token,
            start_date=start_date.date(),
            end_date=end_date.date(),
            options=options
        )
        response = client.investments_transactions_get(request)
        for transaction in response.investment_transactions:
            # Check if the transaction already exists in the database, else create a new one
            existing_transaction = InvestmentTransaction.query.filter_by(investment_transaction_id=transaction.investment_transaction_id, user_id=current_user.id).first()
            if not existing_transaction:
                # Ensure that 'type' is of string type
                transaction_type = str(transaction['type']) if hasattr(transaction, 'type') else None
                transaction_subtype = str(transaction['subtype']) if hasattr(transaction, 'subtype') else None
                
                new_transaction = InvestmentTransaction(
                    user_id=current_user.id,
                    account_id=transaction['account_id'],
                    security_id=transaction['security_id'],
                    investment_transaction_id=transaction['investment_transaction_id'],
                    amount=transaction['amount'],
                    date=transaction['date'],
                    name=transaction['name'],
                    quantity=transaction['quantity'],
                    institution_value=transaction['institution_value'] if hasattr(transaction, 'institution_value') else None,
                    institution_value_currency=transaction['institution_value_currency'] if hasattr(transaction, 'institution_value_currency') else None,
                    subtype = transaction_subtype,
                    cancel_transaction_id=transaction['cancel_transaction_id'] if hasattr(transaction, 'cancel_transaction_id') else None,
                    iso_currency_code=transaction['iso_currency_code'],
                    fees=transaction['fees'],
                    price=transaction['price'],
                    type=transaction_type,
                    unofficial_currency_code=transaction['unofficial_currency_code'] if hasattr(transaction, 'unofficial_currency_code') else None
                )
                db.session.add(new_transaction)

        db.session.commit()
        return jsonify({'error': None, 'investments_transactions': response.to_dict()})
    except plaid.ApiException as e:
        error_response = format_error(e)
        return jsonify(error_response)

#API endpoint to return the account names of the user
@app.route('/api/user_accounts', methods=['GET'])
def get_user_accounts():
    try:
        user_accounts = BankAccount.query.filter_by(user_id=current_user.id).all()
        account_names = [account.account_name for account in user_accounts]
        return jsonify(accounts=account_names)
        
    except Exception as e:
        return jsonify({'error': str(e)})

#API endpoint to return the LLM answer
@app.route('/api/conversation', methods=['POST'])
def get_chatbot_response():
    if current_user.is_authenticated:
        user_id = current_user.get_id()
    else:
        user_id = None  # or handle unauthenticated users as you see fit

    message = request.json["input"]
    chathistory = request.json["messagehistory"]
    response = stock_analysis(message, chathistory, user_id)

    return jsonify({"response": response})


@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    YOUR_DOMAIN = "http://127.0.0.1:5000"
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1Ns2oFCp04lVZoC1gtpHUkXA', 
            'quantity': 1,
        }],
        mode='subscription',
        success_url=YOUR_DOMAIN + "/success/",
        cancel_url=YOUR_DOMAIN + "/cancel/",
        client_reference_id=current_user.id,  # Pass the current user ID as a reference
    )
    return jsonify({
        'id': checkout_session.id
    })

@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        logging.error("Invalid payload")
        abort(400)
    except stripe.error.SignatureVerificationError as e:
        logging.error("Invalid signature")
        abort(400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Get the user and update their subscription status
        customer_id = session.get('client_reference_id')
        user = Customer.query.get(customer_id)
        if user:
            logging.info("User retrieved: %s", user.email)
            
            user.is_premium = True

            # Fetch the subscription details from Stripe to get the end date
            subscription_id = session.get('subscription')  # Get the subscription ID from the session object
            if subscription_id:
                logging.info("Subscription ID retrieved from session: %s", subscription_id)
                subscription = stripe.Subscription.retrieve(subscription_id)  # Retrieve the subscription details from Stripe

                # Set the subscription end date based on the subscription details from Stripe
                user.subscription_end_date = datetime.fromtimestamp(subscription['current_period_end'])

                try:
                    db.session.commit()
                    db.session.refresh(user)
                    logging.info("User subscription details updated: %s", user.email)
                except Exception as e:
                    db.session.rollback()
                    logging.error("Failed to update user subscription status: %s", str(e))
            else:
                logging.error("No subscription ID found in session data")
        else:
            logging.error("No user found for customer ID: %s", customer_id)

    return '', 200


@app.route('/success/')
def success():
    return render_template('success.html')

@app.route('/cancel/')
def cancel():
    return "Payment was cancelled."





if __name__ == '__main__':
    app.run(debug=True)