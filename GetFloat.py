import os
import requests
import sqlite3
from typing import overload
import json
import logging
import atexit
from collections import namedtuple

#https://docs.python.org/3/library/typing.html
#https://www.alphavantage.co/documentation/
API_KEY = "api.key"
DB_NAME = "cache.db"
STOCK_OVERVIEW_TABLE_NAME = "StockOverview"
STOCK_BANNED_TABLE_NAME = "StockBanned"

class ApiManager:
	'''
	Free api can send 500 req per a day
	can send 5 req every 1min

	If the request fails i think it doesnt cound against u
	need to update to add this cuz this will take long
	'''
	def __init__(self):
		self.TIMEOUT_TRESHOLD = 100
		self.REQUEST_THRESHOLD = 5
		self.buffer = deque(maxlen=self.REQUEST_THRESHOLD)
		self.logger = logging.getLogger(__class__.__name__)
		self.logger.setLevel(logging.DEBUG)

	def wait_or_go(self):
		if len(self.buffer)<self.REQUEST_THRESHOLD:
			self.buffer.append(time.time())
		elif time.time() - self.buffer[-1]<self.TIMEOUT_TRESHOLD:
			sleep_time = self.TIMEOUT_TRESHOLD- ( time.time() - self.buffer[-1] )
			
			self.logger.debug('Sent {} request within the last {} seconds, threshold for API is amount is {} seconds, so need to wait {} seconds '\
				.format(self.REQUEST_THRESHOLD,-1*(sleep_time-self.TIMEOUT_TRESHOLD),\
					self.TIMEOUT_TRESHOLD, sleep_time ))

			time.sleep(sleep_time)
			self.buffer.append(time.time())
		else:
			self.buffer.append(time.time())


#https://devopsheaven.com/sqlite/databases/json/python/api/2017/10/11/sqlite-json-data-python.html
#https://www.blog.pythonlibrary.org/2012/07/18/python-a-simple-step-by-step-sqlite-tutorial/
class Ticker:
	def __init__(self):
		# get api key
		self.key = ''
		with open("api.key","r") as key_file:
			self.key = key_file.readline()[:-1]

		# connect to sql lie
		self.conn = sqlite3.connect(DB_NAME) # or use :memory: to put it in RAM
		self.cursor = self.conn.cursor()

		# create table if it exists
		self.cursor.execute("CREATE TABLE if not exists {} (ticker varchar(6), data json)".format(STOCK_OVERVIEW_TABLE_NAME))
		self.cursor.execute("CREATE TABLE if not exists {} (ticker varchar(6))".format(STOCK_BANNED_TABLE_NAME))

		# set up logger
		self.logger = logging.getLogger(__class__.__name__)
		self.logger.setLevel(logging.DEBUG)

		#manages the api calls so don't hit the threshold
		self.api_manager = ApiManager()

		#close conn when done
		atexit.register(lambda: self.conn.close())



	def _add_data_to_banned_list(self,symbol):
		symbol = symbol.upper()
		try:

			self.cursor.execute("INSERT INTO {} VALUES (?)".format(STOCK_BANNED_TABLE_NAME),[symbol])
			self.conn.commit()
			self.logger.debug('Added {} to a banned list'.format(symbol))
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
		symbol = aDict['Symbol'].upper()

		try:
			self.cursor.execute("INSERT INTO {} VALUES (?, ?)".format(STOCK_OVERVIEW_TABLE_NAME),[symbol, json.dumps(aDict)])
			self.conn.commit()
		except:
			self.logger.error(aDict)
			raise Exception(aDict)


	def _get_data(self,symbol):
		"""
		Returns MarketData(data=None) if error
		"""

		# check if this is a garabge ticker
		if self._is_ticker_banned(symbol):
			self.logger.debug('{} is a banned symbol returning None'.format(symbol))
			return None

		# check if cache has the ticker
		data = self._get_data_from_cache(symbol)
		if data:
			return data 
		else:
		# check data from endpoint since its not here
			self.logger.debug('{} not in cache, querying Endpoint'.format(symbol))
			url = "https://www.alphavantage.co/query?function=OVERVIEW&symbol={0}&apikey={1}".format(symbol,self.key)
			self.api_manager.wait_or_go()#make sure we are not sending too many req at once
			r = requests.get(url)
			data = r.json()

			# if the endpoints hits 
			if data:
				self.logger.debug('{} adding to cache'.format(symbol))
				self._add_data_to_cache(data)
			else:
				self.logger.warning("Symbol {} could not be found. Typo? Added to garbage ticker list sorr".format(symbol))
				self._add_data_to_banned_list(symbol)

			return data


	def get_shares_float(self,symbol):
		#check cache to see if symbol exits
		data = self._get_data(symbol)
		if data:
			return int(data['SharesFloat'])


	def get_price_history(self,symbol, outputsize = "compact"):
		"""

		"""
		url = "https://www.alphavantage.co/query?function=OVERVIEW&symbol={0}&apikey={1}".format(symbol,self.key)
		r = requests.get(url)
		data = r.json()
		if data:
			return data["Time Series (Daily)"]




