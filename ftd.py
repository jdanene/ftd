from ftd.utilities import Database, DataOptions 

import pandas as pd
import os
import glob
import numpy as np 

import matplotlib.pyplot as plt

import matplotlib as mpl
import matplotlib.ticker as ticker 
from pylab import figure, show, legend, ylabel
import random 
from collections import namedtuple
from enum import Enum
import re



DEFAULT_OPTION = DataOptions.CACHED_ONLY
DEFAULT_TIMEOUT = 17
DEAULT_COLORS  = ['rosybrown','tab:blue','tab:green','turquoise','tab:olive','tab:orange', 'tab:purple','greenyellow','mediumvioletred','tab:pink','black','tab:red' ]

ColorSize = namedtuple("ColorSize", "color size")


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
	def __init__(self,df):

		self.df = df

		# Drop NA's and create our statistic
		self.df = self.df.dropna()
		self.df['SETTLEMENT DATE'] = pd.to_datetime(self.df['SETTLEMENT DATE'],format="%Y%m%d")
		self.df = self.df.sort_values(['SYMBOL','SETTLEMENT DATE'],ascending=True)
		self.df['FTD/Float'] = self.df['QUANTITY (FAILS)'] /self.df['Float']
		self.df['FTD/Float'] = self.df['FTD/Float']*100

		self.offenders = ["UWMC","WISH","AMC","GME","EXPR", "MRIN","ARVL","SPRT","EYES","PUBM","RKT","SENS","NEGG"]
		self.maxers = list(self.df.sort_values('FTD/Float', ascending=False).drop_duplicates(['SYMBOL'])['SYMBOL'])

	def __get_graph_tickers(self,graphTickersOption):
		if graphTickersOption =="ALL":
			return self.maxers 
		elif "_" in graphTickersOption or ("Top" in graphTickersOption and "Exclude" in graphTickersOption):
	
			#ExcludeTop4_Top12
			start = int(re.findall('\d+',graphTickersOption )[0])
			end = int(re.findall('\d+',graphTickersOption )[1])+1
			print(self.maxers[start:end])
			return self.maxers[start:end]
		elif "Top" in graphTickersOption:
			end = int(re.findall('\d+',graphTickersOption )[0])
			return self.maxers[:end] 
		elif graphTickersOption.startswith('Exclude'):
			return self.maxers[int(re.findall('\d+',graphTickersOption )[0])+1:]

		else:
			return self.maxers 

	def ticker_ranking(self,symbol):
		return self.maxers.index(symbol.upper())


	def __get_graph_label(self,symbol):
		float_ = list(round(analyze.df[analyze.df["SYMBOL"] ==symbol]['Float'].head(1)/1000000,2))[0]
		return "{}: {}m".format(symbol,str(float_))


	def graph(self,graphTickersOption = "ALL", title = None):
		df = self.df
		colorsize_handler = GraphColors()
		#plot it
		mpl.rcParams['xtick.labelsize'] = 5
		mpl.rcParams['ytick.labelsize'] = 5

		tick_spacing = 6
		fig, ax = plt.subplots(1,1)

		plt.xticks(rotation=90)
		symbol_in_q = 'FTD/Float'

		tick_list =self.__get_graph_tickers(graphTickersOption)
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
		ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
		ax.yaxis.grid(linewidth=1, alpha=.2)

		fig.suptitle('Failure-to-deliver as a percent of float: 01/2020 - 06/15/2021')

		plt.ylabel('FTD as percent of Float')
		plt.legend(loc="upper left", bbox_to_anchor=(1,1), prop={'size': 4})
		
		if title:
			plt.savefig(title+".eps", format='eps', dpi=1000)
		else:
			plt.show()


ftd_data = Database()
ftd_data.setup(data_option=DataOptions.ALL, exclude_drug_companies = True, timeout=.1)



analyze = Analyse(ftd_data.df)

analyze.df.sort_values(['SYMBOL','FTD/Float'],ascending=True)[analyze.df["SYMBOL"] =="AEI"]
analyze.ticker_ranking('DTSS')
x = analyze.df[analyze.df["SYMBOL"] =='DLO']
x = analyze.df.sort_values(['FTD/Float','SETTLEMENT DATE'],ascending=True)
x[['SETTLEMENT DATE','QUANTITY (FAILS)']] 





def graphMe(aInt, title):
	analyze.graph(str(aInt)+"_"+str(aInt+11), title=None)

analyze.graph("0_72")

analyze.graph(title='maingraph')
graphMe(0, 'graph0')
graphMe(12,'graph1')
graphMe(24,'graph2')
graphMe(24+12,'graph3')
graphMe(48,'graph4')
graphMe(60,'graph5')

graphMe(60+12,'graph5')
graphMe(60+12+12,'graph5')
graphMe(60+12+12+12,'graph5')
graphMe(60+12+12+12+12,'graph5')




list(round(analyze.df[analyze.df["SYMBOL"] =='VJET']['QUANTITY (FAILS)'].head(1)/1000000,2))[0]


