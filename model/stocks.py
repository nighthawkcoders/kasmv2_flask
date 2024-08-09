from random import randrange
from datetime import date
import os, base64
import json

from flask_login import UserMixin

from __init__ import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

#from model.user import User

class TableStock(db.Model):
    __tablename__ = 'table_stocks'
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
            return TableStock.query.filter(TableStock._symbol == stock).value(TableStock._sheesh)
        except Exception as e:
            return {"error": "No such stock exists"},500
    # returns stock id: refered in many to many table: User_Transaction_Stocks
    def get_stockid(self,symbol):
        try:
            return TableStock.query.filter(TableStock._symbol == symbol).value(TableStock.id)
        except Exception as e:
            return {"error": "No such stock exists"},500
    def updatequantity(self,body,isbuy):
        if isbuy == True:
            quantity = body.get("quantity")
            symbol = body.get("symbol")
            currentquantity = TableStock.query.filter(TableStock._symbol == symbol).value(TableStock._quantity)
            newquantity = currentquantity - quantity
            idnum = TableStock.query.filter(TableStock._symbol==symbol).value(TableStock.id)
            x= TableStock.query.get(idnum)
            print("this is x" + str(x))
            x.update(quantity = newquantity)
            return print("updated quanity")
    def updatestockprice(self,body = None,isloop = None,latest_price = None,stock = None, topstock = None):
    #symbol = body.get('symbol')
    # updates stock price 
        if topstock == True:
            return TableStock.query.offset(0).limit(26).all()
        if isloop == False:
            return TableStock.query.all()
        elif isloop == True:
            stock.sheesh = latest_price
            price = stock.sheesh
            db.session.commit()
            return price
        
    def read(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "company": self.company,
            "quantity": self.quantity,
            "sheesh": self.sheesh,
        }
class StockUser(db.Model):
    __tablename__ = 'stock_users'
    id = db.Column(db.Integer, primary_key=True)
    _uid = db.Column(db.String(255), db.ForeignKey('users._uid', ondelete='CASCADE'), nullable=False)
    _stockmoney = db.Column(db.Integer, nullable=False)
    _accountdate = db.Column(db.Date)

    # creates a one to many relatio with transaction table
    transactions = db.relationship('StockTransaction', lazy='subquery', backref=db.backref('stock_users', lazy=True))
    #
    # 
    # users = db.relationship("User", backref=db.backref("stockuser", single_parent=True), lazy=True)

    def __init__(self, uid, stockmoney):
        self._uid = uid
        self._stockmoney = stockmoney
        self._accountdate = date.today()

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def user_id(self, uid):
        self._uid = uid

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
            "uid": self.uid,
            "stockmoney": self.stockmoney,
            "accountdate": self._accountdate,
        }
    # returns balance of user 
    def get_balance(self,body):
        try:
            uid = body.get("uid")
            return StockUser.query.filter(StockUser._uid == uid).value(StockUser._stockmoney)
        except Exception as e:
                return {"error": "Can't find user in StockUser table. Possible fix: Run /initilize first to log user in StockUser table"},500
    # return user id in the StockUser table
    def get_userid(self,uid):
        try:
            return StockUser.query.filter(StockUser._uid == uid).value(StockUser.id)
        except Exception as e:
                return {"error": "Can't find user in StockUser table. Possible fix: Run /initilize first to log user in StockUser table"},500
    
    def updatebal(self,body,val):
        uid = body.get("uid")
        bal =  StockUser.get_balance(self,body)
        newbal = bal - val
        userid = StockUser.query.filter(StockUser._uid == uid).value(StockUser.id)
        x = StockUser.query.get(userid)
        print("this is second x" + str(x))
        x.stockmoney = newbal
        db.session.commit()
        return print("account balance updated")
    
    def check_expire(self, body):
        uid = body.get("uid")
        accountdate = StockUser.query.filter(StockUser._uid == uid).value(StockUser._accountdate)
        
        if accountdate is not None:
            # Convert accountdate to datetime object
            account_datetime = datetime.combine(accountdate, datetime.min.time())
            
            # Add 6 weeks to the accountdate
            expire_date = account_datetime + timedelta(weeks=6)
            
            # Get the current date and time
            current_datetime = datetime.now()
            
            # Check if the account has expired
            if current_datetime > expire_date:
                return True  # Account has expired
            else:
                return False  # Account is still valid
        else:
            # Handle the case where accountdate is None
            return None  # or raise an exception or handle appropriately
class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'

    id = db.Column(db.Integer, primary_key=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('stock_users.id', ondelete='CASCADE'), nullable=False)
    _transaction_type = db.Column(db.String(255), nullable=False)
    _quantity = db.Column(db.Integer, nullable=False)
    _transaction_date = db.Column(db.Date, nullable=False)
    stock_transaction = db.relationship(
        "UserTransactionStock",
        backref=db.backref("stock_transactions", cascade="all, delete-orphan", single_parent=True, overlaps="stock_transaction,transaction"),
        uselist=False
    )
    #user_transaction_stocks = db.relationship("User_Transaction_Stocks", backref=db.backref("stock_transactions", cascade="all, delete-orphan"))

    #user_transaction_stocks = db.relationship("User_Transaction_Stocks", cascade='all, delete', backref='transaction', lazy=True, overlaps="transaction_userstock,transaction")

    def __init__(self, user_id, transaction_type, quantity, transaction_date):
        self._user_id = user_id
        self._transaction_type = transaction_type
        self._quantity = quantity
        self._transaction_date = transaction_date

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
    def createlog_initialbuy(self, body):
        uid = body.get("uid")
        quantity = body.get("quantity")
        transactiontype = 'buy'     
        try:
            # Query the user with the given uid
            user = StockUser.query.filter_by(_uid=uid).first()

            # Get the current date
            current_date = date.today()

            # Subtract one year from the current date by adjusting the year attribute
            new_date = current_date.replace(year=current_date.year - 1)

            # Create a new StockTransaction object
            stock_user = StockTransaction(
                user_id=user.id,
                transaction_type=transactiontype,
                transaction_date=new_date,
                quantity=quantity
            )

            # Add the new transaction to the database session
            db.session.add(stock_user)

            # Commit the transaction to the database
            db.session.commit()

            # Return the id of the newly created transaction
            return stock_user.id
    
        except Exception as e:
            # Return an error message if an exception occurs
            return {"error": f"account has not been autocreated for {uid}, error: {str(e)}"}
        
    def createlog_buy(self,body):
        uid = body.get('uid')
        quantity = body.get('quantity')
        transactiontype = 'buy'
        try:
            user = StockUser.query.filter_by(_uid = uid).first()
            stock_user = StockTransaction(user_id=user.id, transaction_type=transactiontype, transaction_date=date.today(),quantity=quantity)
            db.session.add(stock_user)
            db.session.commit()
            return stock_user.id
        except Exception as e:
            return {"error": "account has not been autocreated for stock game. Run /initilize first to log user in StockUser table"},500
            
        
        
# Many to many intermedetary table
class UserTransactionStock(db.Model):
    __tablename__ = 'user_transaction_stocks'
    _user_id = db.Column(db.Integer, db.ForeignKey('stock_users.id'), primary_key=True, nullable=False)
    _transaction_id = db.Column(db.Integer, db.ForeignKey('stock_transactions.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    _stock_id = db.Column(db.Integer, db.ForeignKey('table_stocks.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    _quantity = db.Column(db.Integer, nullable=False)
    _price_per_stock = db.Column(db.Float, nullable=False)
    _transaction_amount = db.Column(db.Integer, nullable=False)
    _transaction_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    stock = db.relationship(
        "TableStock",
        backref=db.backref("user_transaction_stocks", cascade="all, delete-orphan", single_parent=True, overlaps="stock_transaction,stock")
    )
    user = db.relationship(
        "StockUser",
        backref=db.backref("user_transaction_stocks", cascade="all, delete-orphan", single_parent=True, overlaps="stock_transaction,stockuser")
    )

    def __init__(self, user_id, transaction_id, stock_id, quantity, price_per_stock,transaction_amount,transaction_time):
        self._user_id = user_id
        self._transaction_id = transaction_id
        self._stock_id = stock_id
        self._quantity = quantity
        self._price_per_stock = price_per_stock
        self._transaction_amount = transaction_amount
        self._transaction_time = transaction_time
    def __repr__(self):
        return f'<UserTransactionStock {self._user_id} {self._transaction_id} {self._stock_id}>'
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
        transaction = StockTransaction.query.filter_by(id=transactionid).first()
        uid = body.get("uid")
        symbol = body.get("symbol")
        quantity = body.get("quantity")
        if transaction:
            found = transaction.stock_transaction is not None
            if not found:
                userid = StockUser.get_userid(self,uid)
                stockid = TableStock.get_stockid(self,symbol)
                stockprice = TableStock.get_price(self,body)
                stock_transaction = UserTransactionStock(user_id=userid,transaction_id=transaction.id, stock_id=stockid, quantity=quantity,price_per_stock=stockprice,transaction_amount= value,transaction_time= date.today())
                db.session.add(stock_transaction)
                db.session.commit()
            else:
                print("error: transaction log has not been created yet")\
                    
    def multilog_buy_initial(self,body,value,transactionid):
        transaction = StockTransaction.query.filter_by(id=transactionid).first()
        uid = body.get("uid")
        symbol = body.get("symbol")
        quantity = body.get("quantity")
        if transaction:
            found = transaction.stock_transaction is not None
            if not found:
                user = StockUser.query.filter_by(_uid=uid).first()
            # Get the current date
                current_date = date.today()
            # Subtract one year from the current date by adjusting the year attribute
                new_date = current_date.replace(year=current_date.year - 1)
                userid = StockUser.get_userid(self,uid)
                stockid = TableStock.get_stockid(self,symbol)
                stockprice = TableStock.get_price(self,body)
                stock_transaction = UserTransactionStock(user_id=userid,transaction_id=transaction.id, stock_id=stockid, quantity=quantity,price_per_stock=stockprice,transaction_amount= value,transaction_time= new_date)
                db.session.add(stock_transaction)
                db.session.commit()
            else:
                print("error: transaction log has not been created yet")
    def check_tax(self,body):
        symbol = body.get("symbol")
        quantity = body.get("quantity")
        uid = body.get("uid")
        stockid = TableStock.get_stockid(self,symbol)
        userid = StockUser.get_userid(self,uid)
        one_year_ago = datetime.now() - timedelta(days=365)
        try:
            s = list(UserTransactionStock.query.filter_by(_stock_id = stockid, _user_id = userid).all())
            buy_list = []
            sell_list = []
            one_year_list = []
            less_one_year_list = []
            
            for i in s:
                transactionid = i.transaction_id
                transaction_type = StockTransaction.query.filter(StockTransaction.id == transactionid).value(StockTransaction._transaction_type)
                if transaction_type == 'buy':
                    buy_list.append(i)
                else:
                    sell_list.append(i)
            for j in buy_list:
                time = j._transaction_time
                if time <= one_year_ago:
                    one_year_list.append(j)
                else:
                    less_one_year_list.append(j)
                print(str(one_year_list))
                    
                print(str(time))
        except Exception as e:
            return {e}
    def check_stock_quantity(self,body):
        symbol = body.get("symbol")
        uid = body.get("uid")
        stockid = TableStock.get_stockid(self,symbol)
        userid = StockUser.get_userid(self,uid)
        try:
            s = list(UserTransactionStock.query.filter_by(_stock_id = stockid, _user_id = userid).all())
            buy_list = []
            sell_list = []
            num_buy = 0
            num_sell = 0
            for i in s:
                transactionid = i.transaction_id
                transaction_type = StockTransaction.query.filter(StockTransaction.id == transactionid).value(StockTransaction._transaction_type)
                if transaction_type == 'buy':
                    buy_list.append(i)
                    print(buy_list)
                    num_buy += i.quantity
                else:
                    sell_list.append(i)
                    num_sell += i.quantity
            
            return num_buy - num_sell
        except Exception as e:
            return {e}
    
