import os
import requests
import sqlite3
from typing import overload
import json
import logging
import atexit
from collections import namedtuple
from urllib import parse
from requests.models import PreparedRequest
from dotenv import load_dotenv
from .api_utilities import ApiManager,get_root_dir

load_dotenv()  # take environment variables from .env.


#https://docs.python.org/3/library/typing.html
#https://www.alphavantage.co/documentation/

API_KEY = os.getenv("ALPHA_ADV_APIKEY")
print('alphavantage API Key {}'.format(API_KEY))
DATA_PATH = os.path.join(get_root_dir(),"data")
DB_NAME = os.path.join(DATA_PATH,"cache.db")
STOCK_OVERVIEW_TABLE_NAME = "StockOverview"
STOCK_BANNED_TABLE_NAME = "StockBanned"
ENDPOINT = "https://www.alphavantage.co/query"
TIMEOUT_TRESHOLD = 100
REQUEST_THRESHOLD = 75 



SharesFloat = namedtuple("SharesFloat", "was_cached data")

MarketData = namedtuple("SharesFloat", ["was_cached","data"])



#https://devopsheaven.com/sqlite/databases/json/python/api/2017/10/11/sqlite-json-data-python.html
#https://www.blog.pythonlibrary.org/2012/07/18/python-a-simple-step-by-step-sqlite-tutorial/
class Ticker:

	# static var
	#manages the api calls so don't hit the threshold
	api_manager = ApiManager(TIMEOUT_TRESHOLD,REQUEST_THRESHOLD)

	def __init__(self):
		# get api key
		self.key = os.getenv("ALPHA_ADV_APIKEY")
		assert  self.key!=None, "Missing alphavantage api key"
		# connect to sql lie
		self.conn = sqlite3.connect(DB_NAME) # or use :memory: to put it in RAM
		self.cursor = self.conn.cursor()

		# create table if it exists
		self.cursor.execute("CREATE TABLE if not exists {} (ticker varchar(6), data json)".format(STOCK_OVERVIEW_TABLE_NAME))
		self.cursor.execute("CREATE TABLE if not exists {} (ticker varchar(6))".format(STOCK_BANNED_TABLE_NAME))

		# set up logger
		self.logger = logging.getLogger(__class__.__name__)
		self.logger.setLevel(logging.DEBUG)



		self.tpc_session = requests.session()

		#close conn when done
		atexit.register(self.__cleanup)

	def __cleanup(self):
		self.conn.close()
		self.tpc_session.keep_alive = False
		self.tpc_session.close()

	def _add_data_to_banned_list(self,symbol):
		symbol = symbol.upper()
		try:

			self.cursor.execute("INSERT INTO {} VALUES (?)".format(STOCK_BANNED_TABLE_NAME),[symbol])
			self.conn.commit()
			print('Added {} to a banned list'.format(symbol))
		except:
			self.logger.error('Failed to add {} to a banned list'.format(symbol))
			raise Exception('Failed to add {} to a banned list'.format(symbol))

	def _is_ticker_banned(self,symbol):
		symbol = symbol.upper()

		self.cursor.execute("SELECT ticker FROM {} WHERE ticker = ?".format(STOCK_BANNED_TABLE_NAME),(symbol,))
		data = self.cursor.fetchone()
		if data:
			return True
		else:
			return False

		#cursor.execute("SELECT ticker FROM {}".format(STOCK_OVERVIEW_TABLE_NAME))
		#cursor.fetchall()

	def _get_data_from_cache(self,symbol):
		symbol = symbol.upper()
		self.cursor.execute("SELECT data FROM {} WHERE ticker = ?".format(STOCK_OVERVIEW_TABLE_NAME),(symbol,))
		data = self.cursor.fetchone()
		if data:
			return json.loads(data[0])

	def _add_data_to_cache(self,aDict):
		"""
		Takes in json
		"""

		#inconsistent api
		dict_ ={}
		for k,v in aDict.items():
			dict_[k.replace(" ", "") ]=v



		try:
			self.cursor.execute("INSERT INTO {} VALUES (?, ?)".format(STOCK_OVERVIEW_TABLE_NAME),[aDict['Symbol'], json.dumps(dict_)])
			self.conn.commit()
		except:
			self.logger.critical(dict_)
			raise Exception(dict_)


	def _get_data(self,symbol, is_cached_only = False):
		"""
		Returns MarketData(data=None) if error
		if is_cached_only==True
		- returns MarketData(true, data) if cached otherwise
		- MarketData(False, None)
		"""
		symbol = symbol.replace(" ", "").upper()
		# check if this is a garabge ticker
		if self._is_ticker_banned(symbol):
			print('{} is a banned symbol'.format(symbol))
			return MarketData(None, None)

		# check if cache has the ticker
		data = self._get_data_from_cache(symbol)
		if data:
			return MarketData(True, data) 
		elif is_cached_only:
			return MarketData(False, None) 
		else:
		# check data from endpoint since its not here
			print('{} not in cache, querying Endpoint'.format(symbol))
			url = "https://www.alphavantage.co/query?function=OVERVIEW&symbol={0}&apikey={1}".format(symbol,self.key)
			
			#prepare url
			params = parse.urlencode({'function':'OVERVIEW','symbol':symbol,'apikey':self.key})
			req = PreparedRequest()
			req.prepare_url(ENDPOINT, params)

			self.api_manager.wait_or_go()#make sure we are not sending too many req at once
			r = self.tpc_session.get(req.url)
			data = r.json()


			# if the endpoints hits 
			if data:
				print('{} added to cache'.format(symbol))
				try:
					self._add_data_to_cache(data)
					return MarketData(False, data) 

				except:
					print("Error with saving to cache: {} could not be found".format(req.url))
					self.api_manager.rewind()
					return MarketData(False, None) 

			else:
				self.logger.critical("Symbol {} could not be found".format(symbol))
				self._add_data_to_banned_list(symbol)
				self.api_manager.rewind()
				return MarketData(False, None) 



	def get_shares_float(self,symbol,is_cached_only = False, exclude_drug_companies=True ):
		#check cache to see if symbol exits
		market_data = self._get_data(symbol,is_cached_only)

		try:
			if market_data.data and market_data.data['SharesFloat']:
				if exclude_drug_companies:
					if  market_data.data['Industry'] and "PHARMA"  in market_data.data['Industry']:
						return SharesFloat(None,None)
					else:
						return SharesFloat(market_data.was_cached, float(market_data.data['SharesFloat']))

			else:
				return SharesFloat(None,None)
				
		except:
			self.logger.error(market_data.data)

			Exception(market_data.data)


	def get_price_history(self,symbol, outputsize = "compact"):
		"""

		"""
		url = "https://www.alphavantage.co/query?function=OVERVIEW&symbol={0}&apikey={1}".format(symbol,self.key)
		r = requests.get(url)
		data = r.json()
		if data:
			return data["Time Series (Daily)"]




