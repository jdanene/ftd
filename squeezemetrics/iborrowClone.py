from ftplib import FTP
import pandas as pd 
import csv 
from datetime import datetime,timedelta
import awswrangler as wr
import numpy as np 
from pyarrow import table
import sqlite3
import atexit
import tentaclio
from sheetsApi import append_row_to_gsheet
from time import sleep, time
from recordclass import recordclass
import pickle
from pathlib import Path
from collections import namedtuple
import threading 
from interactiveBrokers import App
from structures import StockId

#only takes top 3



#######################################################
#######################################################
#######################################################
def createTable(table_name):
	return """
	CREATE TABLE if not exists {}(
     TIMESTAMP timestamp, 
     SYMBOL text, 
     ISIN text, 
     REBATERATE real,
     FEERATE real, 
     AVAILABLE integer, 
     PRIMARY KEY (SYMBOL, TIMESTAMP)) 
	""".format(table_name)


#StockId = recordclass("StockId", "ticker gsheet last_seen")


class IBorrowDesk:
	DB_NAME = "borrow.db"
	TABLE_NAME= "iborrow_data"
	ENDPOINT="ftp3.interactivebrokers.com"
	FTP_FILE = "usa.txt"
	SHEET_NAME="sprt_ibkr_live"

	def __init__(self, poll_freq = 30):
		
		self.ids ={
		1:StockId('DNA','dna_ibkr_live',[],time(),False),
		2:StockId('SKIN','skin_ibkr_live',[],time(),False),
		3:StockId('DOLE','dole_ibkr_live',[],time(),False),
		4:StockId('APRN','aprn_ibkr_live',[],time(),False),
		6:StockId('GENI','geni_ibkr_live',[],time(),False),
		7:StockId('RCON','rcon_ibkr_live',[],time(),False),
		8:StockId('PTRA','ptra_ibkr_live',[],time(),False),
		9:StockId('BFI','bfi_ibkr_live',[],time(),False),
		10:StockId('CIFR','cifr_ibkr_live',[],time(),False),
		11:StockId('TRIT','trit_ibkr_live',[],time(),False),
		12:StockId('BTCM','btcm_ibkr_live',[],time(),False),
		13:StockId('BKKT','bkkt_ibkr_live',[],time(),False),
		14:StockId('RDBX','rdbx_ibkr_live',[],time(),False),
		19:StockId('BRPM','brpm_ibkr_live',[],time(),False),
		16:StockId('GROM','grom_ibkr_live',[],time(),False),
		21:StockId('SPIR','spir_ibkr_live',[],time(),False),
		18:StockId('BGFV','bgfv_ibkr_live',[],time(),False),
		19:StockId('APPH','apph_ibkr_live',[],time(),False),
		15:StockId('PUBM','pubm_ibkr_live',[],time(),False),
		17:StockId('AUR','aur_ibkr_live',[],time(),False),




		}
		# setup thread ibkr updates  sprt for most recent data
		self.ibkr_live_app = App(self.ids)
		self.ibkr_live_app_thread = threading.Thread(target=self.ibkr_live_app.run, daemon=True)


		# get the saved bookmarks from pickle
		for k,v in self.ids.items():
			v.last_seen = self._get_bookmark(v)
			print("LASTSEEN:",v.ticker,v.last_seen)

		# a lock for the thing that saves snapshots
		self.id_lock = threading.Lock()

		self.poll_freq= poll_freq
		# connect to sql lie
		self.conn = sqlite3.connect(self.DB_NAME) # or use :memory: to put it in RAM
		self.cursor = self.conn.cursor()

		# create table if it exists
		self.cursor.execute(createTable(self.TABLE_NAME))

		# load the table
		self.df = pd.read_sql("select * from {}".format(self.TABLE_NAME), self.conn)  
		#print(self.df)
		#cleanup 
		atexit.register(self.__cleanup)

		self.timestamp = None
		self.stop = False


	def __get_all_bookmarks(self):
		for k,v in self.ids.items():
			v.last_seen = self._get_bookmark(v)

	def __cleanup(self):
		# close connection
		self.conn.close()
		self.cursor.close() 
		#update in the background
		self._background_update()
		# shutdown ibkr loop
		self.ibkr_live_app.kill()

		#unlock 
		try:
			self.id_lock.release()
		except RuntimeError as e:
			print(e)


	def _background_update(self):
		"""
		saves bookmark to disk on load so we have a place
		"""
		#self.id_lock.acquire()
		for k,v in self.ids.items():
			#print(v.last_seen)
			self._save_bookmark(v)
		#self.id_lock.release()

	def _save_bookmark(self, stockId):
		#print('[Updating bookmark]')
		with open('{}bookmark.pickle'.format(stockId.ticker), 'wb') as handle:
			pickle.dump(stockId.last_seen, handle, protocol=pickle.HIGHEST_PROTOCOL)


	def _get_bookmark(self, stockId):
		fpath = '{}bookmark.pickle'.format(stockId.ticker)

		my_file = Path(fpath)
		if my_file.is_file():
			try:
				with open('{}bookmark.pickle'.format(stockId.ticker), 'rb') as handle:
					return pickle.load(handle)
			except EOFError:
				return []
		else:
			return []


	def run(self):
		#start deamon
		try:
			self.ibkr_live_app_thread.start()

			while self.stop ==False: 
				self.update_data()
				sleep(self.poll_freq)

		finally:
			self.ibkr_live_app.kill()




	def _get_ftp_data(self):
		'''
			Gets file and returns a dataframe 
			Columns: ['SYMBOL', 'CUR', 'NAME', 'CON', 'ISIN', 'REBATERATE', 'FEERATE','AVAILABLE']
		'''
		with tentaclio.open("ftp://shortstock:@ftp3.interactivebrokers.com/usa.txt") as f:
			print('Gettin FTP')	
			# get loan data
			df_ = pd.read_csv(f, delimiter = "|", skiprows=[0])#, encoding= 'unicode_escape')
			df_ = df_.iloc[: , :-1]
			df_ = df_.rename(columns={'#SYM': 'SYMBOL'})
			df_ = df_.head(-1)
			
			# get time stamp
			f.seek(0)
			reader = csv.reader(f,delimiter="|")
			row1 = next(reader) 
			# add timestamp to data reorganize columns
			timestamp= datetime.strptime('{} {}'.format(row1[1],row1[2]), '%Y.%m.%d %H:%M:%S') - timedelta(hours=3)
			df_['TIMESTAMP'] = timestamp 
			df_['TIMESTAMP'] = pd.to_numeric(df_['TIMESTAMP'])
			df_ = df_[['TIMESTAMP','SYMBOL','ISIN','REBATERATE','FEERATE','AVAILABLE']]
			return df_,timestamp

	def update_data(self):
		# get data from ftp
		new_data, timestamp = self._get_ftp_data()
		old_data = self.df 

		# merge the shit, want to skip the first column which is datetime (this will always be diff)
		self.df = old_data.merge(new_data,how="outer", on=new_data.columns[1:].tolist())
		self.df['TIMESTAMP']=np.where(self.df['TIMESTAMP_x'].isna(),self.df['TIMESTAMP_y'],self.df['TIMESTAMP_x'])
		
		self.df = self.df[['TIMESTAMP','SYMBOL','ISIN','REBATERATE','FEERATE','AVAILABLE']]
		self.df.sort_values(by=['TIMESTAMP','SYMBOL'], ascending=True, inplace=True)

		#save the shit
		self.save_data()

		#check if new
		self.check_if_update(timestamp)


	def is_same(self,data1, stockId):
		#print('het')
		data_last_seen = self._get_bookmark(stockId)
		if data_last_seen == []:
			stockId.last_seen = data1
			return False 
		if data1[3]!=data_last_seen[3] or data1[4]!=data_last_seen[4] or data1[5]!=data_last_seen[5]:
			stockId.last_seen = data1
			return False
		else:
			return True



	def get_time_stamp(self, pandas_format_unix):
		'''pandas messes with shit'''
		return datetime.utcfromtimestamp(int(float(pandas_format_unix))/1000000000)

	def check_if_update(self,timestamp):
		'''
		writes to a spreadsheet if the data has updated. 
		'''
		#print(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
		if timestamp!=self.timestamp:
			self.timestamp=timestamp
			print(timestamp.strftime('%Y-%m-%d %H:%M:%S'))

		# get lock for self.ids.items()
		#self.id_lock.acquire()
		for k,v in self.ids.items():
			# get the latest data for the ticker `k`


			if not self.df.loc[(self.df['SYMBOL'] ==v.ticker)].empty: 
				last_two_datapoints = self.df.loc[(self.df['SYMBOL'] ==v.ticker)].tail(1)

				# put the latest data into a list
				data_new = last_two_datapoints.iloc[0].tolist()
				#print("STOCK:",v.ticker)
				#print("new:",data_new)
				#print("old:",self._get_bookmark(v))

							# first entry is time need to format it
				#print("Is same ", v.ticker,  self.is_same(data_new,v))
				if not self.is_same(data_new,v) :
					data_new[0]=self.get_time_stamp(data_new[0]).strftime('%Y-%m-%d %H:%M:%S')
					print("[{}] New update for: {} ".format(timestamp.strftime('%Y-%m-%d %H:%M:%S'),v.ticker))
					print("NEW DATA: ",data_new)
					# save to sheets
					append_row_to_gsheet(data_new ,v.gsheet)

					#save bookmark if datais different. 
					self._save_bookmark(v)



		self.__get_all_bookmarks()
			#print(v.last_seen)

		# release lock for self.ids.items()
		#self.id_lock.release()

		# run code to update in the background
		#x = threading.Thread(target=self._background_update, daemon=True)
		#x.start()


	def save_data(self):
		self.df.to_sql(self.TABLE_NAME, con=self.conn,if_exists='replace',index=False,index_label=['SYMBOL','TIMESTAMP'])



while True:

	try:

		iborrowdesk = IBorrowDesk()
			#iborrowdesk.update_data()
		iborrowdesk.run()
	except Exception as e: 
		print("I failed")
		print(e)
		continue











