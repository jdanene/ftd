import datetime
# BDay is business day, not birthday...
from pandas.tseries.offsets import BDay
import boto3
import csv
import urllib.request
import io
from tqdm import tqdm

BUCKET_NAME = "shortsqueeze"
BASE_PATH = "sho_list_nyse"





# https://stackoverflow.com/questions/40336918/how-to-write-a-file-or-data-to-an-s3-object-using-boto3


class S3:
	def __init__(self):
		self.s3 = boto3.resource('s3')

	@staticmethod
	def get_business_day(offset):
		return (datetime.datetime.today() - BDay(offset))

	@staticmethod
	def get_formatted_date(date_time):
		return date_time.strftime('%d-%B-%Y')

	def send_interval_to_s3(self,offset = 936):
		"""
		Today is Aug 4, 2022
		936 from now is 01/02/2018

		"""
		for i in tqdm(range(0,offset)):
			date_time = S3.get_business_day(i)
			formatted_date = S3.get_formatted_date(date_time)
			self.send_to_s3(formatted_date)

	def send_to_s3(self,formatted_date, bucket= BUCKET_NAME, base_path = BASE_PATH):
		end_point ="https://www.nyse.com/api/regulatory/threshold-securities/download?selectedDate={}&amp;market=".format(formatted_date)
		fname = 'nysesho_{}.txt'.format(formatted_date)
		path = '{}/{}'.format(base_path,fname)

		with urllib.request.urlopen(end_point) as url:
			f = io.BytesIO(url.read())
			self.s3.Object(bucket, path).put(Body=f)

sendData = S3()
sendData.send_interval_to_s3()

