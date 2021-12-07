import time 
from collections import deque 
import os
import logging
from dotenv import load_dotenv
import urllib.request
import io 
from datetime import datetime

load_dotenv()  # take environment variables from .env.
API_KEY = os.getenv("ALPHA_ADV_APIKEY")

def get_root_dir():
	return os.popen("git rev-parse --show-toplevel").read()[:-1]
	
class ApiManager:
	'''
	Free api can send 500 req per a day
	can send 5 req every 1min

	If the request fails i think it doesnt cound against u
	need to update to add this cuz this will take long
	'''
	def __init__(self, timeout_threshold, request_threshold):
		self.TIMEOUT_TRESHOLD = timeout_threshold
		self.REQUEST_THRESHOLD = request_threshold
		self.buffer = deque(maxlen=self.REQUEST_THRESHOLD)
		self.logger = logging.getLogger(__class__.__name__)
		self.logger.setLevel(logging.DEBUG)

	def get_timeout(self):
		t = self.TIMEOUT_TRESHOLD/float(self.REQUEST_THRESHOLD)
		if t<1:
			return t
		else:
			return 0

	def wait_or_go(self):
		if len(self.buffer)<self.REQUEST_THRESHOLD:
			self.buffer.append(time.time())
		elif time.time() - self.buffer[0]<self.TIMEOUT_TRESHOLD:
			sleep_time = self.TIMEOUT_TRESHOLD- ( time.time() - self.buffer[0] )
			
			print('Sent {} request within the last {} seconds, threshold for API is amount is {} seconds, so need to wait {} seconds '\
				.format(self.REQUEST_THRESHOLD,-1*(sleep_time-self.TIMEOUT_TRESHOLD),\
					self.TIMEOUT_TRESHOLD, sleep_time ))

			time.sleep(sleep_time+.13)
			self.buffer.append(time.time())
		else:
			self.buffer.append(time.time())

	def rewind(self):
		self.buffer.pop()


class GetPriceData:
	TIMEOUT_TRESHOLD = 100
	REQUEST_THRESHOLD = 75 
	api_manager = ApiManager(TIMEOUT_TRESHOLD,REQUEST_THRESHOLD)
	FILTER_DATE = datetime.strptime("2018-01-02", '%Y-%m-%d')

	@staticmethod
	def getdata(ticker):
		ticker = ticker.upper()

		GetPriceData.api_manager.wait_or_go()#make sure we are not sending too many req at once

		end_point ="https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}&outputsize=full&datatype=csv".format(ticker, API_KEY)

		header = ["timestamp"	,"open"	,"high"	,"low"	,"close","volume"]
		with urllib.request.urlopen(end_point) as url:
			f = io.BytesIO(url.read())
			data = pd.read_csv(f)
			try:
			
				data.columns = header

				data['timestamp'] =  pd.to_datetime(data['timestamp'], format='%Y-%m-%d')
				data['Symbol'] = ticker
				data = data[(data['timestamp']>=FILTER_DATE)]
				return data
			except Exception as e:
				print(str(e))
				print(data.columns)
				return pd.DataFrame()



