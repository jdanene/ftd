
from constants import MEME_STOCKS
from GetFloat import Ticker
import logging
from tqdm import tqdm
import pandas as pd
import time
from collections import deque

NYSE_CSV = "nyselist_1625204791785.csv"
NASDAQ_CSV = "nasdaqlist_1625204865858.csv"





class Database:

	def __init__(self):
		self.logger = logging.getLogger(__class__.__name__)
		self.logger.setLevel(logging.DEBUG)

		self.logger.debug("Getting FTD data")
		frames = []
		for file in glob.glob("*.txt"):
			print(file)
			df = pd.read_csv(file, delimiter = "|",error_bad_lines=False)
			frames.append(df)

		self.df = pd.concat(frames)
		
		#add new col
		self.df['FTD/Float'] = self.df['QUANTITY (FAILS)'] 
		self.df['STD_fails'] = self.df['QUANTITY (FAILS)'] 
		self.df['MEAN_fails'] = self.df['QUANTITY (FAILS)'] 


		self.logger.debug("Finished getting FTD data")


	def setup(self):
		float_getter = Ticker()
		all_symbols = {str(x) for x in set(self.df['SYMBOL']) if len(str(x))<=5}
		
		self.logger.debug("Getting shares_float inputing statistics based on this in db")
		# get ftd/float

		# 5 request per a minutes
		time.sleep(5)
		api_hits = 0
		time_first_hit=0
		for sym in tqdm(all_symbols):
			if len(sym)>5: # nasdaq stocks length less than 5
				continue 

			if sym not in MEME_STOCKS:
				#api call to get the float - 500 limit
			
					
				shares_float = float_getter.get_shares_float(sym)

				if shares_float:
					self.__update_stats(sym,shares_float)
					time.sleep(2)
				else:
					self.logger.warning('{} could not be found'.format(sym))
			else:
				self.__update_stats(sym,MEME_STOCKS[sym])



	def __get_symbols(self):
		nyse_symbols = self.__get_exchange_tickers(NYSE_CSV)
		nasdaq_symbols = self.__get_exchange_tickers(NASDAQ_CSV)
		exxchange_symbols = nyse_symbols.union(nasdaq_symbols)

		#nasadaq max string len is 5
		return {str(x).upper() for x in set(self.df['SYMBOL']) if len(str(x))<=5}.intersection(exxchange_symbols)


	def __get_exchange_tickers(self,file):
		ticks = set(pd.read_csv(file).iloc[:,0])
		return {x.replace(" ", "")  for x in ticks if x.isalpha() }


	def __update_stats(self,sym,shares_float):
		old = np.array(self.df[self.df["SYMBOL"] == sym]['FTD/Float'])
		new = np.array(self.df[self.df["SYMBOL"] == sym]['FTD/Float'].div(shares_float))*100
		self.df.loc[self.df['SYMBOL'] == sym, 'FTD/Float'] = self.df.loc[self.df['SYMBOL'] == sym, 'FTD/Float'].replace(old,new)

		old = np.array(self.df.loc[self.df['SYMBOL'] == sym, 'STD_fails'])
		new = np.array(self.df.loc[self.df['SYMBOL'] == sym, 'FTD/Float'].rolling(30).std())
		self.df.loc[self.df['SYMBOL'] == sym, 'STD_fails'] = self.df.loc[self.df['SYMBOL'] == sym, 'STD_fails'].replace(old,new)

		old = np.array(self.df.loc[self.df['SYMBOL'] == sym, 'MEAN_fails'])
		new = np.array(self.df.loc[self.df['SYMBOL'] == sym, 'FTD/Float'].rolling(20).sum())
		self.df.loc[self.df['SYMBOL'] == sym, 'MEAN_fails'] = self.df.loc[self.df['SYMBOL'] == sym, 'MEAN_fails'].replace(old,new)


ftd_data = Database()
ftd_data.setup()
