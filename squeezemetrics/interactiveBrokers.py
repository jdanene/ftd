from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.client import EClient
from ibapi.client import MarketDataTypeEnum
from ibapi.common import BarData
import datetime
import threading
import time
import atexit
from sheetsApi import append_row_to_gsheet
from ibapi.utils import iswrapper
from structures import StockId
import tentaclio

#https://algotrading101.com/learn/interactive-brokers-python-api-native-guide/


def get_sprt_data(data,ticker):
	#['TIMESTAMP','SYMBOL','ISIN','REBATERATE','FEERATE','AVAILABLE']
	return [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ticker,'','','',data]


#StockId = recordclass("StockId", "ticker gsheet last_seen")


SHORTABLE_SHARES_TICKID = 89


class App(EClient,EWrapper):
	#https://gist.github.com/wrighter/4df9177849cfe9fd4465099f5e86461e
	def __init__(self,stockIds:StockId = {}, marketDataTypeEnum:MarketDataTypeEnum = MarketDataTypeEnum.DELAYED):
		EWrapper.__init__(self)
		EClient.__init__(self, wrapper=self)

		self.stockIds = stockIds
		self.marketDataTypeEnum=marketDataTypeEnum
		self.connect("127.0.0.1", 7496, clientId=123)
		atexit.register(self.disconnect)
		self.time_heavy =time.time()

		# max freq to update: inseconds
		self.max_freq = 30
		self.is_empty_freq = 60*17 +30#if no update 

		#thread = threading.Thread(target=self.run, daemon=True)
		#thread.start()

		#
	
	def shares_still_available(self):

		for k,v in self.stockIds.items():
			if time.time() - v.ibkr_timeout >self.is_empty_freq:

				if  v.no_shares == False:
					print('No shares shares avail for {}: last seen '.format(v.ticker),str(time.time() - v.ibkr_timeout ))
					append_row_to_gsheet(get_sprt_data(0,v.ticker),v.gsheet) #assume after this threshold no shares avail to borrow
					v.ibkr_timeout = time.time()
					v.no_shares = True

	# 3 = delyayed
	# 1 = realtime
	@iswrapper
	def nextValidId(self, orderId:int):
		print("Setting nextValidOrderId: %d", orderId)
		self.nextValidOrderId = orderId
		self.start()

	@iswrapper
	def tickSize(self, tickerId, field, size):
		#check all for share availbliliy
		#self.shares_still_available() 

		if field == SHORTABLE_SHARES_TICKID:
			ticker = self.stockIds[tickerId].ticker
			wksheet= self.stockIds[tickerId].gsheet
			time_last_seen = self.stockIds[tickerId].ibkr_timeout

			#if size != self.lastSeen:
			data = get_sprt_data(size,ticker)

			
			print('[{}]'.format(data[0]),'Seconds since last seen for {}: '.format(ticker), str(time.time() - time_last_seen))

			# if we haven't updated in the max_freq to update, 
			# then update, and save the time stamp
			if time.time() - time_last_seen>self.max_freq:
				print('[{}]'.format(data[0]),'Number of shares avail for {}: '.format(ticker), str(size))
				append_row_to_gsheet(data,wksheet)
				self.stockIds[tickerId].ibkr_timeout = time.time()

				if self.stockIds[tickerId].no_shares:
					print('[{}]'.format(data[0]),'Shares just became avail for {}: '.format(ticker))
				self.stockIds[tickerId].no_shares = False






	def kill(self):
		self.disconnect()

	#@staticmethod
	#def build_contracts(StockIds_list):
	@iswrapper
	def error(self, reqId, errorCode, errorString):
		print("Error. Id: " , reqId, " Code: " , errorCode , " Msg: " , errorString)

	@iswrapper
	def start(self):
		queryTime = (datetime.datetime.today() - datetime.timedelta(days=0)).strftime("%Y%m%d %H:%M:%S")
		

		#request for each stock
		for k,v in self.stockIds.items():
			print(k,v.ticker)
			contract = Contract()
			contract.secType = "STK"
			contract.symbol = v.ticker
			contract.currency = "USD"
			contract.exchange = "SMART"
			#MarketDataTypeEnum.DELAYED
			#MarketDataTypeEnum.REALTIME 
			self.reqMarketDataType(self.marketDataTypeEnum )

			self.reqMktData(k, contract, "236", False, False, [])

		#https://www.quantstart.com/articles/connecting-to-the-interactive-brokers-native-python-api/
#a = App()MarketDataTypeEnum.REALTIME)
#a.run()

#app = EClient(MyWrapper())
#app.connect("127.0.0.1", 7496, clientId=123)
#app.run()  
#time.sleep(10) #Sleep interval to allow time for incoming price data
#app.disconnect()