from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from seleniumrequests import Chrome
from sheetsApi import append_row_to_gsheet
from datetime import datetime
import sqlite3
import time
import random 
from dotenv import load_dotenv
import os
from collections import namedtuple

load_dotenv() 

#c+k = f+p 
#call price + strike price = future price + put price
#f=c+k-p
#f=1.44+9-2.25
#f=.05+9-.15

def find_ids(driver):
	ids = driver.find_elements_by_xpath('//*[@id]')
	for ii in ids:
		#print ii.tag_name
		print(ii.get_attribute("id"))    # id name as string



COLUMNS = ["date", "returned_shares", "new_loans_shares",  "change_shares", "c2b_avg","c2b_max","c2b_min","on_loan_market_open", "change_pc", "on_loan_after_intraday_change","ratio_of_prevoius","SI_estimated_last_close","SI_estimated_now","SI_estimated_now_as_ff","si_intraday_data_day","si_intraday_data_from"]
DB_NAME = "sprt_sqeeze.db"
TABLE_NAME = "squeezemetrics"
TABLE_PUBM= "pubm_squeezemetrics"
TABLE_BBIG= "bbig_squeezemetrics"
TABLE_MRIN= "MRIN_squeezemetrics"
TABLE_SKIN= "skin_squeezemetrics"
TABLE_DNA= "dna_squeezemetrics"
TABLE_GENI= "geni_squeezemetrics"
TABLE_RCON= "rcon_squeezemetrics"
TABLE_DOLE= "dole_squeezemetrics"
TABLE_APRN= "aprn_squeezemetrics"
TABLE_PTRA= "ptra_squeezemetrics"
TABLE_BFI= "bfi_squeezemetrics"
TABLE_CIFR= "cifr_squeezemetrics"
TABLE_TRIT= "trit_squeezemetrics"
TABLE_BTCM= "btcm_squeezemetrics"
TABLE_BKKT= "bkkt_squeezemetrics"
TABLE_APPH= "apph_squeezemetrics"

TABLE_GROM= "grom_squeezemetrics"
TABLE_BGFV= "BGFV_squeezemetrics"
TABLE_SPIR= "SPIR_squeezemetrics"
TABLE_AUR= "aur_squeezemetrics"


261673

USERNAME = os.getenv("ORTEX_USERNAME")
PW = os.getenv("ORTEX_PW")

StockId = namedtuple("StockId", "ticker gsheet ortex_id table_name")


def createTable(table_name):
	return """
	CREATE TABLE if not exists {}(
	date timestamp PRIMARY KEY, 
     returned_shares integer, 
     new_loans_shares integer, 
     change_shares real, 
     c2b_avg real,
     c2b_max real, 
     c2b_min real, 
     on_loan_market_open integer, 
     change_pc real,
     on_loan_after_intraday_change integer,
     ratio_of_prevoius real, 
     SI_estimated_last_close real, 
     SI_estimated_now real,
     SI_estimated_now_as_ff real,
     si_intraday_data_day real,
     si_intraday_data_from real) 
	""".format(table_name)


def login():
	driver.find_element_by_id("id_password").send_keys(PW)
	driver.find_element_by_id("id_username").send_keys(USERNAME)
	driver.find_element_by_class_name("form-group").submit()



    
class OrtexScraper:

	def __init__(self):
		# connect to sql lie
		self.conn = sqlite3.connect(DB_NAME) # or use :memory: to put it in RAM
		self.cursor = self.conn.cursor()

		# create table if it exists
		self.cursor.execute(createTable(TABLE_DNA))
		self.cursor.execute(createTable(TABLE_DOLE))
		self.cursor.execute(createTable(TABLE_SKIN))
		self.cursor.execute(createTable(TABLE_RCON))
		self.cursor.execute(createTable(TABLE_GENI))
		self.cursor.execute(createTable(TABLE_APRN))
		self.cursor.execute(createTable(TABLE_PTRA))
		self.cursor.execute(createTable(TABLE_BFI))
		self.cursor.execute(createTable(TABLE_CIFR))
		self.cursor.execute(createTable(TABLE_TRIT))
		self.cursor.execute(createTable(TABLE_BTCM))
		self.cursor.execute(createTable(TABLE_BKKT))
		self.cursor.execute(createTable(TABLE_GROM))
		self.cursor.execute(createTable(TABLE_BGFV))
		self.cursor.execute(createTable(TABLE_SPIR))
		self.cursor.execute(createTable(TABLE_PUBM))
		self.cursor.execute(createTable(TABLE_APPH))
		
		self.cursor.execute(createTable(TABLE_AUR))


		self.ids ={
		'DNA':StockId('DNA','ortex_dna','258758',TABLE_DNA),
		'DOLE':StockId('DOLE','ortex_dole','254410',TABLE_DOLE),
		'SKIN':StockId('SKIN','skin_live','229403',TABLE_SKIN),
		'APRN':StockId('APRN','ortex_aprn','39550',TABLE_APRN),
		'RCON':StockId('RCON','ortex_rcon','51292',TABLE_RCON),
		'GENI':StockId('GENI','geni_live','227823',TABLE_GENI),
		'PTRA':StockId('PTRA','ortex_ptra','243261',TABLE_PTRA),
		'BFI':StockId('BFI','ortex_bfi','211181',TABLE_BFI),
		'CIFR':StockId('CIFR','ortex_cifr','257777',TABLE_CIFR),
		'TRIT':StockId('TRIT','ortex_trit','204513',TABLE_TRIT),
		'BTCM':StockId('BTCM','ortex_btcm','227782',TABLE_BTCM),
		'BKKT':StockId('BKKT','ortex_bkkt','260518',TABLE_BKKT),
		'GROM':StockId('BKKT','ortex_grom','245504',TABLE_GROM),
		'BGFV':StockId('BGFV','ortex_bgfv','26193',TABLE_BGFV),
		'SPIR':StockId('SPIR','ortex_spir','256003',TABLE_SPIR),
		'PUBM':StockId('PUBM','live_pubm','210322',TABLE_PUBM),
		'APPH':StockId('APPH','apph_live_ortex','220140',TABLE_APPH),
		'AUR':StockId('AUR','aur_live_ortex','261673',TABLE_AUR)







		}


		#driver
		self.driver = Chrome()

		self.hasloggedin=False
		
	def login(self):
		self.driver.get('https://www.ortex.com/login')
		self.driver.find_element_by_id("id_password").send_keys(PW)
		self.driver.find_element_by_id("id_username").send_keys(USERNAME)
		self.driver.find_element_by_class_name("form-group").submit()

	def save_to_gSheets(self,data_list,gsheet):
		## appends to google sheet
		append_row_to_gsheet(data_list,gsheet)

		# add to cache
	def _save_to_cache(self,data_list,table_name):
		genqs = ["?" for i in data_list]
		genqs =','.join(genqs)
		try:
			self.cursor.execute("INSERT INTO {} VALUES ({})".format(table_name,genqs),data_list)
			self.conn.commit()
		except Exception as e:
			print(str(e))
			raise Exception('Failed to add to cache'.format(data))


	def _get_data_from_cache(self,table_name):
		self.cursor.execute("SELECT * FROM {} ORDER BY {} DESC LIMIT 1".format(table_name,'date'))
		data = self.cursor.fetchone()
		if data:
			return data

	def _is_same(self,data_list1, data_list2):
		for x,y in zip(data_list1[1:],data_list2[1:]):
			if x!=y:
				return False
		return True

	def _data_to_list(self,time, data):
		#add date first
		return_list = [time]

		#now iterate over the rest
		for k in COLUMNS[1:]:
			try:
				return_list.append(data[k])
			except:
				return_list.append(None)
		return return_list

	def main(self):
		self.login()
		self.check_for_update()
		factor = 1
		while True:
			print("delaly [{},{}]".format(5*factor, 12.5*(factor/2)))
			delay= 25+random.uniform(5, 12.5)
			print("delay actual {}".format(delay))
			time.sleep(delay)
			try:
				is_same_bool = self.check_for_update()
			except Exception as e:
				print(str(e))
				print("logging in again")
				self.login()
				is_same_bool =True

			if is_same_bool:
				factor*=1.1
			else:
				factor=1


	def check_for_update(self):

		for k,v in self.ids.items():
			self._check_for_update(v)


	def _check_for_update(self, stockId):
		ortex_id = stockId.ortex_id
		ticker = stockId.ticker
		gsheet = stockId.gsheet
		table_name = stockId.table_name

		print(stockId)
		response = self.driver.request('GET', 'https://www.ortex.com/API/shorts_intraday/{}'.format(ortex_id))
		if response.status_code == 200:
			data = response.json()
		else:
			Exception(response.json())

		time = datetime.now()

		# get data
		data_list = self._data_to_list(time, data)

		#check if in cache
		data_tuple_last_seen = self._get_data_from_cache(table_name)

		# check if same
		is_same_bool=False
		if data_tuple_last_seen is not None:
			is_same_bool= self._is_same(data_list,data_tuple_last_seen)

		if not is_same_bool:
			# convert to google format
			data_list[0]= data_list[0].strftime('%m/%d/%Y %H:%M:%S')
			
			# save to gsheets:
			self.save_to_gSheets(data_list, gsheet)
			
			# convert to sqlite format
			data_list[0]=time 

			#save to cache
			self._save_to_cache(data_list,table_name)

		return is_same_bool


while True:
	try:
		scraper = OrtexScraper()
		scraper.main()
	except Exception as e:
		print(e)
		print('It broke')


