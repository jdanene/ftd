from datetime import datetime
# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay
import boto3
import csv
import urllib.request
import io
from tqdm import tqdm
import pandas as pd 
import numpy as np
from collections import namedtuple
from boto3 import client
from dotenv import load_dotenv
from functools import reduce

load_dotenv()  # take environment variables from .env.

BUCKET_NAME = "shortsqueeze"
BASE_PATH_NYSE = "sho_list_nyse"
BASE_PATH_NASDAQ = "sho_list"

TIMEOUT_TRESHOLD = 100
REQUEST_THRESHOLD = 75 


class BuildDb:
	def __init__(self):
		self.client =  boto3.client('s3')

		#folders on s3 with data of interest
		self.prefix_folders=["sho_list_nyse","sho_list"]

	@staticmethod
	def get_data(text_data):
		data = pd.read_csv(text_data, sep = '|')
		date = str(int(data.iloc[[-1]]['Symbol']))[:8]
		date = datetime.strptime(date, '%Y%m%d')
		data.drop(data.tail(1).index,inplace=True) # drop last n rows
		data = data[['Symbol']]
		data['timestamp']=date
		return data

	def build_from_s3(self):
		all_df = []
		for p in self.prefix_folders:
			all_df+= self.get_from_s3_prefix(p)
		df = pd.concat(all_df)
		return df

	def get_from_s3_prefix(self,prefix =BASE_PATH_NASDAQ ):
		df_list = []
		client = self.client

		paginator = client.get_paginator('list_objects_v2')
		result = paginator.paginate(Bucket=BUCKET_NAME,Prefix=prefix)
		for page in result:
			if "Contents" in page:
				for key in page[ "Contents" ]:
					keyString = key[ "Key" ]
					if ".txt" in keyString:
						print(keyString)
						obj = client.get_object(Bucket= BUCKET_NAME, Key= keyString) 
						df_list.append(BuildDb.get_data(obj['Body']))

		return df_list

def build_price_data(ticker_list):
	dfs = []
	for t in tqdm(ticker_list):
		try:
			v = GetPriceData.getdata(t)
			if not v.empty:
				dfs.append(GetPriceData.getdata(t))
			else:
				print('FAIL {}'.format(t))
		except Exception as e:
			print(str(e))
			print('FAIL {}'.format(t))
			continue 
	return pd.concat(dfs)


builddb = BuildDb()

# Gets sho list data
df = builddb.build_from_s3()
df['is_sho']=1
tickers = set(df['Symbol'])

#Gets price history
price_df = build_price_data(tickers)

# save it (takes 2hrs)
price_df.to_parquet('picehistory.parquet', engine='fastparquet')
price_df = pd.read_parquet('picehistory.parquet',engine='fastparquet')
# merge
df_final =  pd.merge(df,price_df,on=['Symbol','timestamp'],how='outer')
# replace nan with zero
df_final['is_sho'].fillna(0, inplace=True)
# take non nan values with price
df_final = df_final[df_final['open'].notna()]

df_final.sort_values(['Symbol','timestamp'],ascending=True, inplace=True)
tickers = set(df_final['Symbol'])
df_final['sho_count'] = 0

# counts the shit 
for t in tickers:
	value = [0]
	sho_array = df_final[df_final['Symbol']==t]['is_sho']
	for i in  sho_array:
		if i ==1:
			newval = value[-1]+1
		else:
			newval = 0
		value.append(newval)
	value = value[1:]
	df_final.loc[df_final['Symbol'] == t, 'sho_count'] = value


# filter for date
df_final = df_final[(df_final['timestamp']<=datetime.strptime("2021-07-30", '%Y-%m-%d'))]


# shift price up by one
# https://stackoverflow.com/questions/57391305/shifting-timeseries-data-using-per-group-using-shift-and-groupby-results-in
df_final['prev_close'] = df_final.groupby(['Symbol'])['close'].shift()

#percent change of high and prev close
df_final['candle_cover']=(df_final['high'] - df_final['prev_close'])/df_final['prev_close']

# lag the price by one
df_final['candle_cover_next_day'] = df_final.groupby(['Symbol'])['candle_cover'].shift(-1)


df_final[(df_final['Symbol']=='SPCE') ][['timestamp','sho_count']].to_csv("SPCE.csv")



df_regression = df_final[(df_final['sho_count']>=13)]
df_regression = df_regression[(df_regression['timestamp']>datetime.strptime("2021-05-01", '%Y-%m-%d'))]

df_regression = df_regression[df_regression['candle_cover_next_day'].notna()]
df_regression = df_regression[df_regression['candle_cover'].notna()]
Y = df_regression["candle_cover_next_day"]
X = df_regression[["sho_count","volume"]]

model = sm.OLS(Y, X).fit() ## sm.OLS(output, input)
predictions = model.predict(X)
model.summary()


