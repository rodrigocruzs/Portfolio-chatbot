from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from flask_login import UserMixin
from flask import current_app
import bcrypt

db = SQLAlchemy()
migrate = Migrate()

def init_app(app):
    """Initialize the database."""
    db.init_app(app)
    migrate.init_app(app, db)


# Define the User model for Flask-Login
class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Fields for subscription management
    subscription_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)
    subscription_end_date = db.Column(db.DateTime, default=datetime.utcnow)

    bank_accounts = db.relationship('BankAccount', backref='customer', lazy=True)
    plaid_items = db.relationship('PlaidItem', backref='customer', lazy=True)
    investment_holdings = db.relationship('InvestmentHolding', backref='customer', lazy=True)
    investment_transactions = db.relationship('InvestmentTransaction', backref='customer', lazy=True)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    # Method to check if the user is in the trial period
    def in_trial_period(self):
        trial_period_days = 7
        trial_end_date = self.subscription_start_date + timedelta(days=trial_period_days)
        return datetime.utcnow() < trial_end_date

    # Method to check if the user has access (either through trial or premium subscription)
    def has_access(self):
        # Check if the user has an active premium subscription
        if self.is_premium:
            return True
        
        # Check if the user is within the subscription end date
        if datetime.utcnow() < self.subscription_end_date:
            return True

        # Check if the user is within the trial period
        trial_period_days = 7  # Adjust this value as per your trial period duration
        trial_end_date = self.subscription_start_date + timedelta(days=trial_period_days)
        return datetime.utcnow() < trial_end_date
    
class UserQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, ForeignKey('customer.id'), nullable=False, index=True)  # Foreign Key to refer to the customer table
    question = db.Column(db.String, nullable=False, index=True)  # Column to store the question
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Column to store the timestamp of when the question was asked

    def __repr__(self):
        return f'<UserQuestion {self.question}>'

# Store the details of the bank accounts linked via Plaid
class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    account_id = db.Column(db.String(255), unique=True)  # For account_id

    account_name = db.Column(db.String(255))  # Can map to "name" or "official_name"
    
    account_mask = db.Column(db.String(255))  # Maps to "mask"
    account_type = db.Column(db.String(255))  # Maps to "type"
    account_subtype = db.Column(db.String(255))  # Maps to "subtype"
    
    available_balance = db.Column(db.Float)  # Maps to "balances.available"
    current_balance = db.Column(db.Float)  # Maps to "balances.current"
    currency_code = db.Column(db.String(10))  # Maps to "balances.iso_currency_code"

# store the access tokens and any other Plaid-specific information.
class PlaidItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    item_id = db.Column(db.String(255), nullable=True)  # Item ID from Plaid's response
    last_updated = db.Column(db.DateTime, nullable=True)

    # Balances
    available_balance = db.Column(db.Float, nullable=True)
    current_balance = db.Column(db.Float)
    iso_currency_code = db.Column(db.String(10))
    limit = db.Column(db.Float, nullable=True)
    unofficial_currency_code = db.Column(db.String(10), nullable=True)

class InvestmentSecurity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    security_id = db.Column(db.String(255), nullable=False, unique=True)  # Unique ID of the security
    name = db.Column(db.String(255))  # Name of the security
    type = db.Column(db.String(50))  # Type of the security e.g. 'derivative'
    ticker_symbol = db.Column(db.String(50))  # Ticker symbol if available
    iso_currency_code = db.Column(db.String(10))
    close_price = db.Column(db.Float)
    close_price_as_of = db.Column(db.Date)
    unofficial_currency_code = db.Column(db.String(10))
    holdings = relationship("InvestmentHolding", back_populates="security")


class InvestmentHolding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    account_id = db.Column(db.String(255), nullable=False)  # Plaid's account_id
    security_id = db.Column(db.String(255), db.ForeignKey('investment_security.security_id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    institution_price = db.Column(db.Float)  # Price of the security from the institution
    institution_price_currency = db.Column(db.String(10))  # Currency of the price
    institution_value = db.Column(db.Float)  # Total value of the holding from the institution
    institution_value_currency = db.Column(db.String(10))  # Currency of the value
    cost_basis = db.Column(db.Float)  # Cost basis of the security
    cost_basis_currency = db.Column(db.String(10))  # Currency of the cost basis
    iso_currency_code = db.Column(db.String(10))
    unofficial_currency_code = db.Column(db.String(10))
    security = relationship("InvestmentSecurity", back_populates="holdings")


class InvestmentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    account_id = db.Column(db.String(255), nullable=False)  # Plaid's account_id
    security_id = db.Column(db.String(255))  # Plaid's security_id
    investment_transaction_id = db.Column(db.String(255), nullable=False)  # Plaid's transaction_id (This is unique per transaction, good for checking duplicates)
    amount = db.Column(db.Float)
    fees = db.Column(db.Float)
    date = db.Column(db.Date)
    price = db.Column(db.Float)  # The price of the security at which this transaction occurred.
    name = db.Column(db.String(255))  # Name of the security or investment
    quantity = db.Column(db.Float)  # Quantity of the security involved in the transaction
    institution_value = db.Column(db.Float)  # Value of the transaction from the institution
    institution_value_currency = db.Column(db.String(10))  # Currency of the value
    subtype = db.Column(db.String(50), nullable=True)  # Subtype of the transaction e.g. 'buy' or 'sell'
    cancel_transaction_id = db.Column(db.String(255))  # If the transaction is a cancellation, the ID of the original transaction
    iso_currency_code = db.Column(db.String(10))
    type = db.Column(db.String(50))  # Type of the transaction e.g. 'cash'
    unofficial_currency_code = db.Column(db.String(10), nullable=True)


class InvestmentView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('customer.id'))
    account_id = db.Column(db.String(255))
    security_id = db.Column(db.String(255))
    quantity = db.Column(db.Float)
    institution_price = db.Column(db.Float)
    institution_price_currency = db.Column(db.String(10))
    institution_value = db.Column(db.Float)
    institution_value_currency = db.Column(db.String(10))
    cost_basis = db.Column(db.Float)
    name = db.Column(db.String(255))
    type = db.Column(db.String(50))
    ticker_symbol = db.Column(db.String(50))
    account_name = db.Column(db.String(255))
    account_mask = db.Column(db.String(255))
    account_subtype = db.Column(db.String(255))


def save_user_question(user_id_param, user_input):
    with current_app.app_context():
        print(db)
        new_question = UserQuestion(user_id=user_id_param, question=user_input)
        db.session.add(new_question)
        db.session.commit()


class StockFinancialData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker_symbol = db.Column(db.String(50), nullable=False, unique=True)
    company_name = db.Column(db.String(255), nullable=False)
    stock_exchange = db.Column(db.String(50), nullable=False)
    sector = db.Column(db.String(50), nullable=False)
    
    dividend_yield = db.Column(db.Float, nullable=True) 
    trailing_pe_ratio = db.Column(db.Float, nullable=True) 
    forward_pe_ratio = db.Column(db.Float, nullable=True) 
    market_cap = db.Column(db.BigInteger, nullable=True)
    fifty_two_week_low = db.Column(db.Float, nullable=True)
    fifty_two_week_high = db.Column(db.Float, nullable=True)
    enterprise_to_revenue_ratio = db.Column(db.Float, nullable=True) 
    enterprise_to_ebitda_ratio = db.Column(db.Float, nullable=True) 

    net_income_margin = db.Column(db.BigInteger, nullable=True) 
    ebitda = db.Column(db.BigInteger, nullable=True) 
    ebitda_margin = db.Column(db.Float, nullable=True)  
    total_revenue = db.Column(db.BigInteger, nullable=True) 
    return_on_equity = db.Column(db.Float, nullable=True)
    
    free_cash_flow = db.Column(db.BigInteger, nullable=True)
    earnings_growth = db.Column(db.Float, nullable=True) 
    revenue_growth = db.Column(db.Float, nullable=True) 
    gross_margin = db.Column(db.Float, nullable=True)
    operating_margin = db.Column(db.Float, nullable=True)
    

