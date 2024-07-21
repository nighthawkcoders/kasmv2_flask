from random import randrange
from datetime import date
import os, base64
import json

from flask_login import UserMixin

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
#from model.user import User

class Stocks(db.Model):
    __tablename__ = 'stocks'
    id = db.Column(db.Integer, primary_key=True)
    _symbol = db.Column(db.String(255), unique=False, nullable=False)
    _company = db.Column(db.String(255), unique=False, nullable=False)
    _quantity = db.Column(db.Integer, unique=False, nullable=False)
    _sheesh = db.Column(db.Integer, unique=False, nullable=False)

    def __init__(self, symbol, company, quantity, sheesh):
        self._symbol = symbol
        self._company = company
        self._quantity = quantity
        self._sheesh = sheesh

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol

    @property
    def company(self):
        return self._company

    @company.setter
    def company(self, company):
        self._company = company

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity

    @property
    def sheesh(self):
        return self._sheesh

    @sheesh.setter
    def sheesh(self, sheesh):
        self._sheesh = sheesh

    def __str__(self):
        return json.dumps(self.read())

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.remove()
            return None

    def update(self, symbol="", company="", quantity=None):
        if len(symbol) > 0:
            self.symbol = symbol
        if len(company) > 0:
            self.company = company
        if quantity is not None and isinstance(quantity, int) and quantity > 0:
            self.quantity = quantity
        db.session.commit()
        return self
    # gets price of stock
    def get_price(self,body):
        stock = body.get("symbol")
        try:
            return Stocks.query.filter(Stocks._symbol == stock).value(Stocks._sheesh)
        except Exception as e:
            return {"error": "No such stock exists"},500
    # returns stock id: refered in many to many table: User_Transaction_Stocks
    def get_stockid(self,symbol):
        try:
            return Stocks.query.filter(Stocks._symbol == symbol).value(Stocks.id)
        except Exception as e:
            return {"error": "No such stock exists"},500
    def read(self):
        return {
            "id": self.stock_id,
            "symbol": self.symbol,
            "company": self.company,
            "quantity": self.quantity,
            "sheesh": self.sheesh,
        }
class StockUser(db.Model):
    __tablename__ = 'stockuser'
    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.String(255), db.ForeignKey('users._uid', ondelete='CASCADE'), nullable=False)
    _stockmoney = db.Column(db.Integer, nullable=False)
    _accountdate = db.Column(db.Date)

    # creates a one to many relatio with transaction table
    transactions = db.relationship('Transactions', lazy='subquery', backref=db.backref('stockuser', lazy=True))
    #
    # 
    # users = db.relationship("User", backref=db.backref("stockuser", single_parent=True), lazy=True)

    def __init__(self, user_id, stockmoney, accountdate):
        self._user_id = user_id
        self._stockmoney = stockmoney
        self._accountdate = date.today()

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        self._user_id = user_id

    @property
    def stockmoney(self):
        return self._stockmoney

    @stockmoney.setter
    def stockmoney(self, stockmoney):
        self._stockmoney = stockmoney

    @property
    def dob(self):
        return self._dob.strftime('%m-%d-%Y')

    @dob.setter
    def dob(self, dob):
        self._dob = dob

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.remove()
            return None

    def update(self, stockmoney=None):
        if stockmoney is not None and isinstance(stockmoney, int) and stockmoney > 0:
            self.stockmoney = stockmoney
        db.session.commit()
        return self
    
    def read(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "stockmoney": self.stockmoney,
            "accountdate": self._accountdate,
        }
    # returns balance of user 
    def get_balance(self,body):
        try:
            uid = body.get("uid")
            return StockUser.query.filter(StockUser._user_id == uid).value(StockUser._stockmoney)
        except Exception as e:
                return {"error": "Can't find user in StockUser table. Possible fix: Run /initilize first to log user in StockUser table"},500
    # return user id in the StockUser table
    def get_userid(self,uid):
        try:
            return StockUser.query.filter(StockUser._user_id == uid).value(StockUser.id)
        except Exception as e:
                return {"error": "Can't find user in StockUser table. Possible fix: Run /initilize first to log user in StockUser table"},500
class Transactions(db.Model):
    __tablename__ = 'stock_transactions'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('stockuser.id', ondelete='CASCADE'), nullable=False)
    _transaction_type = db.Column(db.String(255), nullable=False)
    _quantity = db.Column(db.Integer, nullable=False)
    _transaction_date = db.Column(db.Date, nullable=False)
    stock_transaction = db.relationship("User_Transaction_Stocks", backref=db.backref("stock_transactions", cascade="all, delete-orphan", single_parent=True, overlaps="user_transaction_stocks,transaction"),uselist=False)

    #user_transaction_stocks = db.relationship("User_Transaction_Stocks", backref=db.backref("stock_transactions", cascade="all, delete-orphan"))

    #user_transaction_stocks = db.relationship("User_Transaction_Stocks", cascade='all, delete', backref='transaction', lazy=True, overlaps="transaction_userstock,transaction")

    def __init__(self, user_id, transaction_type, quantity, transaction_date):
        self._user_id = user_id
        self._transaction_type = transaction_type
        self._quantity = quantity
        self._transaction_date = date.today()

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        self._user_id = user_id

    @property
    def transaction_type(self):
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, transaction_type):
        self._transaction_type = transaction_type

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity

    def __str__(self):
        return json.dumps(self.read())

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.remove()
            return None

    def update(self, user_id="", transaction_type="", quantity=""):
        if len(user_id) > 0:
            self.user_id = user_id
        if len(transaction_type) > 0:
            self.transaction_type = transaction_type
        if len(quantity) > 0:
            self.quantity = quantity
        db.session.commit()
        return self

    def read(self):
        return {
            "id": self.transaction_id,
            "user_id": self.user_id,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "transaction_date": self._transaction_date
        }
    # creates buy log in transaction table
    def createlog_buy(self,body):
        uid = body.get('uid')
        quantity = body.get('quantity')
        transactiontype = 'buy'
        try:
            user = StockUser.query.filter_by(_user_id = uid).first()
            stock_user = Transactions(user_id=user.id, transaction_type=transactiontype, transaction_date=date.today(),quantity=quantity)
            db.session.add(stock_user)
            db.session.commit()
            return stock_user.id
        except Exception as e:
            return {"error": "account has not been autocreated for stock game. Run /initilize first to log user in StockUser table"},500
            
        
        
# Many to many intermedetary table
class User_Transaction_Stocks(db.Model):
    __tablename__ = 'user_transaction_stocks'
    _user_id = db.Column(db.Integer, db.ForeignKey('stockuser.id'), primary_key=True, nullable=False)
    _transaction_id = db.Column(db.Integer, db.ForeignKey('stock_transactions.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    _stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    _quantity = db.Column(db.Integer, nullable=False)
    _price_per_stock = db.Column(db.Float, nullable=False)
    _transaction_amount = db.Column(db.Integer, nullable=False)
    _transaction_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    stock = db.relationship("Stocks", backref=db.backref("user_transaction_stocks", cascade="all, delete-orphan", single_parent=True,overlaps="user_transaction_stocks,stock"))
    user = db.relationship("StockUser", backref=db.backref("user_transaction_stocks", cascade="all, delete-orphan", single_parent=True, overlaps="user_transaction_stocks,stockuser"))

    def __init__(self, user_id, transaction_id, stock_id, quantity, price_per_stock,transaction_amount):
        self._user_id = user_id
        self._transaction_id = transaction_id
        self._stock_id = stock_id
        self._quantity = quantity
        self._price_per_stock = price_per_stock
        self._transaction_amount = transaction_amount

    def __repr__(self):
        return f'<User_Transaction_Stocks {self._user_id} {self._transaction_id} {self._stock_id}>'
    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        self._user_id = user_id
    
    @property
    def transaction_id(self):
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        self._transaction_id = transaction_id
        
    @property
    def stock_id(self):
        return self._stock_id

    @stock_id.setter
    def stock_id(self, _stock_id):
        self._stock_id = _stock_id
        
    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        self._quantity = quantity
        
    @property
    def price_per_stock(self):
        return self._price_per_stock

    @price_per_stock.setter
    def price_per_stock(self, price_per_stock):
        self._price_per_stock = price_per_stock
        
    @property
    def transaction_amount(self):
        return self._transaction_amount

    @transaction_amount.setter
    def transaction_amount(self, transaction_amount):
        self._transaction_amount = transaction_amount
        
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.remove()
            return None

    def update(self, user_id="", transaction_id="", stock_id="", quantity="", price_per_stock="", transaction_amount=""):
        if len(user_id) > 0:
            self._user_id = user_id
        if len(transaction_id) > 0:
            self._transaction_id = transaction_id
        if len(stock_id) > 0:
            self._stock_id = stock_id
        if len(quantity) > 0:
            self._quantity = quantity
        if len(price_per_stock) > 0:
            self._price_per_stock = price_per_stock
        if len(transaction_amount) > 0:
            self._transaction_amount = transaction_amount
        db.session.commit()
        return self

    def read(self):
        return {
            "user_id": self._user_id,
            "transaction_id": self._transaction_id,
            "stock_id": self._stock_id,
            "quantity": self._quantity,
            "price_per_stock": self._price_per_stock,
            "transaction_amount": self._transaction_amount,
            "transaction_time": self._transaction_time
        }
    # creates log in this table
    def multilog_buy(self,body,value,transactionid):
        transaction = Transactions.query.filter_by(id=transactionid).first()
        uid = body.get("uid")
        symbol = body.get("symbol")
        quantity = body.get("quantity")
        if transaction:
            found = transaction.stock_transaction is not None
            if not found:
                userid = StockUser.get_userid(self,uid)
                stockid = Stocks.get_stockid(self,symbol)
                stockprice = Stocks.get_price(self,body)
                stock_transaction = User_Transaction_Stocks(user_id=userid,transaction_id=transaction.id, stock_id=stockid, quantity=quantity,price_per_stock=stockprice,transaction_amount= value)
                db.session.add(stock_transaction)
                db.session.commit()
            else:
                print("error: transaction log has not been created yet")
