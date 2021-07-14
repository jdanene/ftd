# Import the client
from tda import auth, client
import json
import os
from dotenv import load_dotenv
from .api_utilities import ApiManager,get_root_dir
import logging
import time 
from datetime import datetime, timedelta


load_dotenv()  # take environment variables from .env.

#https://github.com/alexgolec/tda-api
#https://tda-api.readthedocs.io/en/stable/
#https://medium.com/swlh/printing-money-with-td-ameritrades-api-a5cccf6a538c


#Fixme: https://developer.tdameritrade.com/content/simple-auth-local-apps
#https://developer.tdameritrade.com/content/getting-started
#https://www.reddit.com/r/algotrading/comments/c81vzq/td_ameritrade_api_access_2019_guide/



REDIRECT_URI = "http://localhost"
PATH_TO_CREDENTIALS_FILE = os.path.join(os.path.join(get_root_dir()),"token.pickle")
API_KEY = "{}@AMER.OAUTHAP".format(os.getenv("TD_AMERI_APIKEY"))

epoch = datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
	return (dt - epoch).total_seconds() * 1000.0

class TdAmeritrade:

	# static variable
	api_manager = ApiManager(timeout_threshold=60, request_threshold=120)

	def __init__(self):
		self.redirect_uri = REDIRECT_URI
		self.credential_file = PATH_TO_CREDENTIALS_FILE
		self.api_key = API_KEY
		# Get throttled request more than 120 times per minute
		self.client = self.__activate_td()

	def __activate_td(self):
		try:
			c = auth.client_from_token_file(self.credential_file, self.api_key)
			return c
		except FileNotFoundError:
			from selenium import webdriver
			with webdriver.Chrome() as driver:
				c = auth.client_from_login_flow(
					driver, self.api_key, self.redirect_uri, self.credential_file)
				return c


	def _retry_request(self,ticker,r):
		print("Api error retrying in {} seconds for {}".format(69,ticker))
		time.sleep(69)
		self.has_options(ticker)

	def y_retry_request(self,ticker,nDays,r):
		#r.raise_for_status()
		print("Api error retrying in {} seconds for {}".format(69,ticker))
		time.sleep(69)
		self.get_nTrading_Days(ticker,nDays)

	def get_nTrading_Days(self,ticker, nDays):
		d = datetime.today() - timedelta(days=nDays)

		#r = self.client.get_price_history(ticker.upper(),
		#frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
		#frequency=client.Client.PriceHistory.Frequency.DAILY,
		#start_datetime=datetime.today(),
		#end_datetime=d
		#)

		self.api_manager.wait_or_go()

		
	
		#time.sleep(self.api_manager.get_timeout()/10)

		success = False
		sleep_time = 5
		first_time = True
		while not success:
			if not first_time:
				print("Api error retrying in {} seconds for {}".format(sleep_time,ticker))
				time.sleep(sleep_time)

			try:
				r = self.client.get_price_history(ticker,
				period_type=client.Client.PriceHistory.PeriodType.YEAR,
				frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
				frequency=client.Client.PriceHistory.Frequency.DAILY,
				start_datetime = d,
				end_datetime = datetime.today()
				)	
				success = (r.status_code == 200)
			except:
				continue
			
			
			if not first_time:
				sleep_time= sleep_time*1.5

			first_time = False
		#assert r.status_code == 200, self.y_retry_request(ticker,nDays,r)
		return r.json()

	def change_since_nDays(self,ticker, nDays):
		
		data = self.get_nTrading_Days(ticker, nDays)
		if data["empty"] == False:
			start = data["candles"][0]
			end = data["candles"][-1]
			
			change = (float(end["close"])-float(start["close"]))/float(start["close"])*100
			startd = datetime.utcfromtimestamp(start["datetime"]/1000).strftime('%Y-%m-%d')
			return change
		else:
			return 0


	def has_options(self, ticker):
		self.api_manager.wait_or_go()#make sure we are not sending too many req at once
		r = self.client.get_option_chain(ticker.upper(),
			contract_type = client.Client.Options.ContractType.CALL,
			strike_count = 1,
			include_quotes=False,
			option_type=client.Client.Options.Type.STANDARD)
		assert r.status_code == 200, self._retry_request(ticker,r)


		#print(r.json())
		return float(r.json()['numberOfContracts'])>0
		#print(r.json()['numberOfContracts'])
		#print(json.dumps(r.json(), indent=4))




