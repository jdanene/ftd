import time 
from collections import deque 
import os
import logging
buffer_ = deque(maxlen=5)

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



