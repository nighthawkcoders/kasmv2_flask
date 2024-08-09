import json, jwt
from flask import Blueprint, request, jsonify, current_app, Response, g
from flask_restful import Api, Resource # used for REST API building
from datetime import datetime
import requests
from api.jwt_authorize import token_required
from model.user import User
from model.stocks import StockUser,StockTransaction,TableStock, UserTransactionStock

stock_api = Blueprint('stock_api', __name__,
                   url_prefix='/stock')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(stock_api)
""" For this code to work, first you would need to bulk update the stock table by using the data in the csv file: stocks_table_exp.csv. 
Then the first thing to run is _initilize_user to create a new user in the StockUser table. 
A possible post request of postman:{"uid":"niko","quantity":10,"symbol": "AAPL"}.
All db change are found in the model/user.py file"""
class StockAPI:
    # used to create a user log to stockuser table
    # Supposed to be called when user first starts
    class _Singleupdata(Resource):
        def post(self):
            #updates stock price:
            body = request.get_json()
            symbol = body.get("symbol")
            isloop = False
            api_key = 'xAxPbodLC12nNCwa5gHiK6YZVQecllPA'  # Replace with your FMP API key
            url = f'https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}'
            stocks = TableStock.updatestockprice(self,body,isloop)
            response = requests.get(url)
            for stock in stocks:
                if stock.symbol == symbol:
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data:  # Check if the list is not empty
                            latest_price = data[0].get('price')
                            # Use .get() to avoid KeyError
                            if latest_price is not None:
                                print("this is stock:" + str(stock))
                                isloop = True
                                price = TableStock.updatestockprice(self,body,isloop,latest_price,stock)
                                print(f"Updated price for {symbol} to {latest_price}")
                            else:
                                print(f"Price data not found for {symbol}")
                        else:
                            print(f"Empty data for {symbol}")
                    else:
                        print(f"Failed to fetch data for {symbol}. Status code: {response.status_code}")
                    print("this is new price" +  str(price))
                    data = jsonify(str(price))
                    print("this is data" + str(data))
            return data         
    class _initilize_user(Resource):
        @token_required()
        def get(self):
            """Reads the stockuser table for logggend in user"""
            current_user = g.current_user
            stock_user = current_user.read_stockuser()
            if stock_user:
                return jsonify(stock_user)
            else:
                return {'message': f'No stock account for {current_user.name} found'}, 404
        
        @token_required()
        def put(self):
            """Creates a new stockuser account for logged in user"""
            current_user = g.current_user
            current_user.add_stockuser()
            return jsonify(current_user.read_stockuser()) 
        
        def post(self):
            body = request.get_json()
            uid = body.get('uid')
            u = User.add_stockuser(self,uid)
            if u == True:
                return jsonify("Account has been created")
            else:
                return jsonify("Account already exists or something has gone wrong")
    # not final,  used to test if major db changes work
    # contains no logic for project yet
    class _initial_stockbuy(Resource):
        def post(self):
            body = request.get_json()
            body = request.get_json()
            userbal = StockUser.get_balance(self,body)
            stockval = TableStock.get_price(self,body)
            quantity = body.get("quantity")
            isbuy = True
            transactionval = quantity * stockval
            if userbal >= transactionval:
                # update user bal
                StockUser.updatebal(self,body,transactionval)
                # create stocktransacotin log
                u=StockTransaction.createlog_initialbuy(self,body)
                UserTransactionStock.multilog_buy_initial(self,body = body,value = transactionval,transactionid=u)
                # update stock quantity
                TableStock.updatequantity(self,body,isbuy)
                return jsonify("Transaction successful")
            else:
                return jsonify({'error': 'Insufficient funds'}), 400
            
            
    class _tranaction_buy(Resource):
        def post(self):
            body = request.get_json()
            userbal = StockUser.get_balance(self,body)
            stockval = TableStock.get_price(self,body)
            quantity = body.get("quantity")
            isbuy = True
            transactionval = quantity * stockval
            if userbal >= transactionval:
                # update user bal
                StockUser.updatebal(self,body,transactionval)
                # create stocktransacotin log
                u=StockTransaction.createlog_buy(self,body)
                UserTransactionStock.multilog_buy(self,body = body,value = transactionval,transactionid=u)
                # update stock quantity
                TableStock.updatequantity(self,body,isbuy)
                return jsonify("Transaction successful")
            else:
                return jsonify({'error': 'Insufficient funds'}), 400
    class _transaction_sell(Resource):
        def post(self):
            body = request.get_json()
            quantity = body.get("quantity")
            symbol = body.get("symbol")
            avaliable_quantity = UserTransactionStock.check_stock_quantity(self,body)
            if avaliable_quantity >= quantity :
                UserTransactionStock.check_tax(self,body)
            else:
                return jsonify({'error':'No stock to sell'}), 400
    class _Account_expirary(Resource):
        def post(self):
            body= request.get_json()
            accountdate = StockUser.check_expire(self,body)
            print(f"this is accountdate: {accountdate}")
            return jsonify(accountdate)

                
                
                
            

    
    api.add_resource(_initilize_user, '/initialize')
    api.add_resource(_tranaction_buy, '/buy')
    api.add_resource(_transaction_sell, '/sell')
    api.add_resource(_Account_expirary, '/expire')
    api.add_resource(_initial_stockbuy, '/initialbuy')
    api.add_resource(_Singleupdata,'/singleupdate')

