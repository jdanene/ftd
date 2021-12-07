from ftd.utilities import Database, DataOptions 
from dotenv import load_dotenv
import threading

import pandas as pd
import os
import glob
import numpy as np 

import matplotlib.pyplot as plt
from tqdm import tqdm

import matplotlib as mpl
import matplotlib.ticker as ticker 
from pylab import figure, show, legend, ylabel
import random 
from collections import namedtuple
from enum import Enum
import re
from ftd.api_access import TdAmeritrade

load_dotenv()  # take environment variables from .env.

DEFAULT_OPTION = DataOptions.CACHED_ONLY
DEFAULT_TIMEOUT = 17
DEAULT_COLORS  = ['rosybrown','tab:blue','tab:green','turquoise','tab:olive','tab:orange', 'tab:purple','greenyellow','mediumvioletred','tab:pink','black','tab:red' ]

ColorSize = namedtuple("ColorSize", "color size")

ROOT_PATH = os.popen("git rev-parse --show-toplevel").read()[:-1]
DATA_PATH = os.path.join(ROOT_PATH,"data","saved_dfs")

class GraphColors:
	def __init__(self):
		self.colors =  ['rosybrown','tab:blue','tab:green','turquoise','tab:olive','tab:orange', 'tab:purple','greenyellow','mediumvioletred','tab:pink','black','tab:red' ]
		self.colorSize_default = ColorSize('silver',.5)
	def get_color(self):
		if len(self.colors)>0:
			index = random.randint(0,len(self.colors)-1)
			size = random.uniform(.65, 1)

			color= self.colors[index]
			self.colors = self.colors[0:index]+self.colors[index+1:]
			return ColorSize(color,size)
		else:
			return self.colorSize_default


class Analyse:
	def __init__(self, df = pd.DataFrame()):
		if not df.empty:
			self.setup(df)
		


	def setup(self,df):
		"""
		Call this first
		"""

		
		# Drop NA's and create our statistic
		self.df = df[df['Float'].notna()]
		self.df['SETTLEMENT DATE'] = pd.to_datetime(self.df['SETTLEMENT DATE'],format="%Y%m%d")
		self.df = self.df.sort_values(['SYMBOL','SETTLEMENT DATE'],ascending=True)
		self.df['FTD/Float'] = self.df['QUANTITY (FAILS)'] /self.df['Float']
		self.df['FTD/Float'] = self.df['FTD/Float']*100
		self.df_optionable = self.df.copy()
		self.df_optionable= self.df_optionable[self.df_optionable["HasOptions"] ==True]

		self.offenders = ["UWMC","WISH","AMC","GME","EXPR", "MRIN","ARVL","SPRT","EYES","PUBM","RKT","SENS","NEGG"]
		self.maxers = list(self.df.sort_values('FTD/Float', ascending=False).drop_duplicates(['SYMBOL'])['SYMBOL'])
		self.maxers_optionable  = list(self.df_optionable .sort_values('FTD/Float', ascending=False).drop_duplicates(['SYMBOL'])['SYMBOL'])


	def load_df(self, fname):
		"""
		Or load saved data
		"""
		f = os.path.join(DATA_PATH,fname+".parquet")
		df = pd.read_parquet(f,engine='fastparquet')
		self.setup(df)
		print("Loaded df from {}".format(f))

	def __get_maxers(self,optionsOnly=False):
		if optionsOnly:
			return self.maxers_optionable
		else:
			return self.maxers 

	def __get_df(self,optionsOnly=False):
		if optionsOnly:
			print("options only df selected")
			return self.df_optionable
		else:
			return self.df 

	def __get_graph_tickers(self,graphTickersOption, optionsOnly=False):

		maxers = self.__get_maxers(optionsOnly) 

		if graphTickersOption =="ALL":
			return maxers 
		elif "_" in graphTickersOption or ("Top" in graphTickersOption and "Exclude" in graphTickersOption):
	
			#ExcludeTop4_Top12
			start = int(re.findall('\d+',graphTickersOption )[0])
			end = int(re.findall('\d+',graphTickersOption )[1])+1
			print(maxers[start:end])
			return maxers[start:end]
		elif "Top" in graphTickersOption:
			end = int(re.findall('\d+',graphTickersOption )[0])
			return maxers[:end] 
		elif graphTickersOption.startswith('Exclude'):
			return maxers[int(re.findall('\d+',graphTickersOption )[0])+1:]

		else:
			return maxers 

	def ticker_ranking(self,symbol,optionsOnly=False):
		maxers = self.__get_maxers(optionsOnly) 

		rank = maxers.index(symbol.upper())/len(maxers)
		return ("{}% Percentile".format(100-round(rank*100,2)), maxers.index(symbol.upper()))


	def __get_graph_label(self,symbol,optionsOnly=False):
		df = self.__get_df(optionsOnly)
		float_ = list(round(df[df["SYMBOL"] ==symbol]['Float'].head(1)/1000000,2))[0]
		return "{}: {}m".format(symbol,str(float_))

	def save_df(self, fname):
		self.df.to_parquet('{}.parquet'.format(os.path.join(DATA_PATH,fname)), engine='fastparquet')
		print("Saved to {}".format(os.path.join(DATA_PATH,fname)))


	def add_change_since_n_days(self, nDays):
		colname = "{}d_priceChange".format(nDays)
		print("New column name is: {}".format(colname))

		df = self.df.copy()
		df[colname] = 0
		td_connect = TdAmeritrade()
		for sym in tqdm(set(analyze.df["SYMBOL"])):
			perc_change = td_connect.change_since_nDays(sym, nDays)
			df.loc[df['SYMBOL'] == sym, colname] = perc_change

		return df


	def graphMe(self,aInt, title, axisY=10, optionsOnly=False):
		self.graph(str(aInt)+"_"+str(aInt+11), title=None,axisY=axisY,optionsOnly=optionsOnly)

	def graphTicker(self,symbol):
		axisY=10
		df = self.__get_df(False)

		colorsize_handler = GraphColors()
		#plot it
		mpl.rcParams['xtick.labelsize'] = 5
		mpl.rcParams['ytick.labelsize'] = 5

		tick_spacing = 6
		fig, ax = plt.subplots(1,1)
		plt.xticks(rotation=90)

		colorSize =  colorsize_handler.get_color()

		ax.set_xlabel('time (d)')
		ax.set_ylabel('FTD/Float')
		ax.plot(df[df["SYMBOL"] == symbol]['SETTLEMENT DATE'],df[df["SYMBOL"] == symbol]['FTD/Float'],label=self.__get_graph_label(symbol),linewidth=colorSize.size, color=colorSize.color)


		ax2 = ax.twinx()
		ax2.set_ylabel('Price')
		colorSize =  colorsize_handler.get_color()
		c = colorSize.color
		ax2.plot(df[df["SYMBOL"] == symbol]['SETTLEMENT DATE'],df[df["SYMBOL"] == symbol]['PRICE'],label=self.__get_graph_label(symbol),linewidth=colorSize.size, color=colorSize.color)
		ax2.tick_params(axis='y',color=c )
		ax2.yaxis.set_major_locator(ticker.MultipleLocator(4))

		ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
		ax.yaxis.set_major_formatter(ticker.PercentFormatter())
		ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
		ax.yaxis.grid(linewidth=1, alpha=.2)
		plt.legend(loc="upper left", bbox_to_anchor=(1,1), prop={'size': 4})
		fig.tight_layout()
		plt.show()




	def graph(self,graphTickersOption = "ALL", title = None, axisY=10,optionsOnly=False):
		df = self.__get_df(optionsOnly)

		colorsize_handler = GraphColors()
		#plot it
		mpl.rcParams['xtick.labelsize'] = 5
		mpl.rcParams['ytick.labelsize'] = 5

		tick_spacing = 6
		fig, ax = plt.subplots(1,1)

		plt.xticks(rotation=90)
		symbol_in_q = 'FTD/Float'

		tick_list =self.__get_graph_tickers(graphTickersOption,optionsOnly)
		i = 0
		for i in range(len(tick_list)):
			colorSize =  colorsize_handler.get_color()

			if i == 0:
				ax.plot(df[df["SYMBOL"] == tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] == tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i == 1:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i == 2:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i == 3:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)
			elif i == 4:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i == 5:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i == 6:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i==7:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i == 8:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)

			elif i == 9:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)
			elif i == 10:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)
			elif i == 11:
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=colorSize.size, color=colorSize.color)
			else :
				ax.plot(df[df["SYMBOL"] ==tick_list[i]]['SETTLEMENT DATE'],df[df["SYMBOL"] ==tick_list[i]][symbol_in_q],label=self.__get_graph_label(tick_list[i]),linewidth=.5, color=colorSize.color)


		ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
		ax.yaxis.set_major_formatter(ticker.PercentFormatter())
		ax.yaxis.set_major_locator(ticker.MultipleLocator(axisY))
		ax.yaxis.grid(linewidth=1, alpha=.2)


		add_text = ": OptionOnly" if optionsOnly else ""
		print(add_text)
		fig.suptitle('Failure-to-deliver as a percent of float: 01/2020 - 06/15/2021 {}'.format(add_text))

		plt.ylabel('FTD as percent of Float')
		plt.legend(loc="upper left", bbox_to_anchor=(1,1), prop={'size': 4})
		
		if title:
			plt.savefig(title+".eps", format='eps', dpi=1000)
		else:
			plt.show()


df = pd.read_pickle('08_20_2020.pickle')
# Get Database
ftd_data = Database()
ftd_data.setup(data_option=DataOptions.ALL, exclude_drug_companies = True)
# Prepare fo analysis

analyze = Analyse(ftd_data.df)
analyze.save_df("09_21_2020")
df_10pc_increase = analyze.add_change_since_n_days(35)

analyze = Analyse()
analyze.load_df("08_20_2020")
analyze.

analyze = Analyse(df)
analyze.ticker_ranking('AYRO')
df_5day_increase = analyze.add_change_since_n_days(5)
df_5day_increase_filter = df_5day_increase[df_5day_increase["{}d_priceChange".format(5)] >= 1]
analyze = Analyse(df_5day_increase_filter)


analyze = Analyse(df_2day_increase_filter)
analyze.ticker_ranking('FUSE')
analyze.ticker_ranking('TMC')
analyze.ticker_ranking('IRNT')

# Does increasdrd in volume signal something
df_10pc_increase_filter = df_10pc_increase[df_10pc_increase["{}d_priceChange".format(35)] >= 10]
df_5pc_increase_filter = df_10pc_increase[df_10pc_increase["{}d_priceChange".format(35)] >= 5]



df_10pc_increase.to_pickle('7_14_21__35dIncrease.pickle')

analyze_10pc_35day = Analyse(df_10pc_increase_filter)
analyze.graphMe(0, 'graph0',1,optionsOnly=True)
analyze.graphMe(0, None,1,optionsOnly=True)
analyze.graphMe(12, None,optionsOnly=True)
analyze.graphMe(738-4, 'graph0',.5,optionsOnly=False)
analyze.graphMe(24+12, 'graph0',1,optionsOnly=False)

analyze.graph()

analyze.graphMe(24, 'graph0',1,optionsOnly=True)
analyze.graphMe(24+12*2,'graph4',1,optionsOnly=True)
analyze.graphMe(24+12*3,'graph5',1,optionsOnly=True)


analyze_5pc_35day = Analyse(df_5pc_increase_filter)
analyze_5pc_35day.graphMe(1, 'graph0',optionsOnly=False)
analyze_5pc_35day.graphMe(12, 'graph0',1,optionsOnly=True)
analyze_5pc_35day.graphMe(12, 'graph0',1,optionsOnly=True)
analyze_5pc_35day.graphMe(24+12, 'graph0',1,optionsOnly=True)
analyze_5pc_35day.graphMe(24+12*2,'graph4',1,optionsOnly=True)
analyze_5pc_35day.graphMe(24+12*3,'graph5',1,optionsOnly=True)



analyze.save_df("07_13_2021")

analyze.ticker_ranking('GENI',True)
analyze.ticker_ranking('GENI',False)

set(analyze.df["SYMBOL"])

analyze.graph("0_72")
analyze.graph(title='maingraph')
analyze.graphMe(2, 'graph0',optionsOnly=False)
analyze.graphMe(12,'graph1',optionsOnly=True)
analyze.graphMe(24,'graph2',optionsOnly=True)
analyze.graphMe(24+12,'graph3',optionsOnly=True)
analyze.graphMe(24+12*2,'graph4',optionsOnly=True)
analyze.graphMe(24+12*6,'graph5',1,optionsOnly=True)

c = TdAmeritrade()
c.change_since_nDays('PEI',35)
3.17 2.2001
one month increase

analyze.graphMe(60+12,'graph5',5)
analyze.graphMe(60+12+12,'graph5',4)
analyze.graphMe(60+12+12+12,'graph5',4)
analyze.graphMe(60+12+12+12+12,'graph5',4)

analyze.graphMe(60+12+12+12+12+12,'graph5',4)
analyze.graphMe(60+12+12+12+12+12+12,'graph5',4)
analyze.graphMe(60+12+12+12+12+12+12+12,'graph5',4)
analyze.graphMe(60+12+12+12+12+12+12+12+12,'graph5',4)
analyze.graphMe(60+12+12+12+12+12+12+12+12+12,'graph5',4)
analyze.graphMe(60+12+12+12+12+12+12+12+12+12+12,'graph5',3)
analyze.graphMe(60+12+12+12+12+12+12+12+12+12+12+12,'graph5',3)
analyze.graphMe(60+12+12+12+12+12+12+12+12+12+12+12+12,'graph5',3)
analyze.graphMe(60+12+12+12+12+12+12+12+12+12+12+12+12+12,'graph5',3)





analyze.df.sort_values(['SYMBOL','FTD/Float'],ascending=True)[analyze.df["SYMBOL"] =="AEI"]
analyze.ticker_ranking('ATOS')
x = analyze.df[analyze.df["SYMBOL"] =='PEI']
x = analyze.df.sort_values(['FTD/Float','SETTLEMENT DATE'],ascending=True)
x[['SETTLEMENT DATE','QUANTITY (FAILS)']] 

analyze.ticker_ranking('BODY')

analyze.ticker_ranking('CTIB',False)


df_10pc_increase_filter[df_10pc_increase_filter["SYMBOL"] =='PEI']["35d_priceChange"]     

list(round(analyze.df[analyze.df["SYMBOL"] =='VJET']['QUANTITY (FAILS)'].head(1)/1000000,2))[0]


