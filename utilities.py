
from constants import MEME_STOCKS
from GetFloat import Ticker
import logging
from tqdm import tqdm
import pandas as pd
import time
from collections import deque
import glob
import numpy as np 
from enum import Enum
import os 
from pathlib import Path


NYSE_CSV = "nyselist_1625204791785.csv"
NASDAQ_CSV = "nasdaqlist_1625204865858.csv"
# https://stockmarketmba.com/listofmostheavilyshortedstocks.php
SHORTED_CSV = "shorted_list_stock.csv"

RAW_DATA_DIR = os.path.join("raw_data","fails_data")




class DataOptions(Enum):
    ALL = 1
    SHORTED_ONLY = 2
    CACHED_ONLY = 3

default_option = DataOptions.ALL

class Database:

	def __init__(self):
		self.logger = logging.getLogger(__class__.__name__)
		self.logger.setLevel(logging.DEBUG)


		# get ftd data
		self.df = self.__get_ftd_data()
		
		#add new col
		self.df["Float"] = np.nan
		#self.df['FTD/Float'] = self.df['QUANTITY (FAILS)'] 
		#self.df['STD_fails'] = self.df['QUANTITY (FAILS)'] 
		#self.df['MEAN_fails'] = self.df['QUANTITY (FAILS)'] 

		self.logger.debug("Finished getting FTD data")

	def __get_ftd_data(self):
		self.logger.debug("Getting FTD data")
		frames = []
		for file in self.__find_files():
			print(file)
			df = pd.read_csv(file, delimiter = "|",error_bad_lines=False, encoding= 'unicode_escape')
			frames.append(df)

		return pd.concat(frames)
		
	def __find_files(self):
		dir_ = os.path.join(os.popen("git rev-parse --show-toplevel").read()[:-1],RAW_DATA_DIR)
		return [os.path.join(dir_,file) for file in os.listdir(dir_) if file.endswith(".txt")]


	def __setup_full_symbols(self):
		all_symbols = self.__get_symbols()
		return {x.replace(" ", "").upper() for x in  all_symbols.union(set(MEME_STOCKS.keys())) }

	def __setup_shorted_symbols(self):
		all_symbols = self.__get_symbols()
		all_symbols = all_symbols.intersection(self._get_exchange_tickers(SHORTED_CSV))
		return {x.replace(" ", "").upper() for x in  all_symbols.union(set(MEME_STOCKS.keys()))}

	def setup(self, data_option = default_option, exclude_drug_companies = True, timeout =7):
		float_getter = Ticker()

		if data_option == DataOptions.SHORTED_ONLY:
			all_symbols = self.__setup_shorted_symbols()
		else:
			all_symbols = self.__setup_full_symbols()

		
		self.logger.debug("Getting shares_float inputing statistics based on this in db")
		assert len(all_symbols)< 8000, "Too many tickers {}".format(len(all_symbols))
		
		count = 0
		for sym in tqdm(all_symbols):
			print(sym)
			if len(sym)>5 or sym=='RILYO': # nasdaq stocks length less than 5
				continue 

			if sym not in MEME_STOCKS:
				#api call to get the float - 500 limit
			
					
				shares_float = float_getter.get_shares_float(sym,exclude_drug_companies=exclude_drug_companies, is_cached_only= (data_option==DataOptions.CACHED_ONLY))


				if shares_float.data:
					self.__update_stats(sym,shares_float.data)
					#sleep if not cached
					if not shares_float.was_cached:
						time.sleep(timeout)

					count+=1
				else:
					pass
			else:
				self.__update_stats(sym,MEME_STOCKS[sym])
				count+=1

		print("Finished, {} stocks currently in dataframe for your analysis".format(count))
		

		#self.df['FTD/Float'] = df['QUANTITY (FAILS)']/df['Float']

	def __get_symbols(self):
		nyse_symbols = self._get_exchange_tickers(NYSE_CSV)
		nasdaq_symbols = self._get_exchange_tickers(NASDAQ_CSV)
		exxchange_symbols = nyse_symbols.union(nasdaq_symbols)

		#nasadaq max string len is 5
		return {str(x).upper() for x in set(self.df['SYMBOL']) if len(str(x))<=5}.intersection(exxchange_symbols)


	def _get_exchange_tickers(self,file):
		ticks = set(pd.read_csv(file).iloc[:,0])
		return {x.replace(" ", "")  for x in ticks if x.isalpha() }


	def __update_stats(self,sym,shares_float):
		print(shares_float)
		#df.loc[df['SYMBOL'] == sym, 'Float'] = shares_float


		#old = np.array(self.df.loc[self.df['SYMBOL'] == sym, 'Float'])
		#new = np.array([float(shares_float) for i in range(len(old))])
		
		self.df.loc[self.df['SYMBOL'] == sym, 'Float'] = shares_float





#ftd_data = Database()
#ftd_data.setup(shorted_only=True)

#df = ftd_data.df[ftd_data.df['SYMBOL'] == 'AA']



