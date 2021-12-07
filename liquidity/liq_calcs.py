import math
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter, DayLocator
import matplotlib.ticker as ticker 
import matplotlib.animation as animation

TICKERS = ['lev', 'arvl','dole','irnt','negg','opad','spce','spir','tmc', 'skin', 'googl','aapl','nvda','ptra','aprn','gsm','cifr','dna','rcon','trit']

IV_30 = [75.9, 76.46, 66.12, 230.81,117.25,123.45,75.01,124,188.64,63.28,31.58,29.56,38.32,117.43,142.31,98.81,123.26,115.02,145.66,111.54]
HV_30 = [57.7,48.61, 30.54, 235.81,70.3,211.25,60.63,172.95,190.18,66.81,19.48,21.97,37.08,68.05,137.38,100.28,137.95,104.38,67.45,44.48]

def get_lix(ticker):
	df = pd.read_csv('{}_daily.csv'.format(ticker.lower()))  
	df = df[df['open'].notna()]
	# turns it into datetime
	df['timestamp'] =  pd.to_datetime(df['timestamp'], infer_datetime_format=True)
	df.index = df['timestamp']
	df['volume_lag1']=df['volume'].shift(1)
	df['close_lag1']=df['close'].shift(1)
	df['high_lag1']=df['high'].shift(1)
	df['low_lag1']=df['low'].shift(1)

	df['lix_{}'.format(ticker.lower())] = np.log((df['volume_lag1']*df['close_lag1'])/(df['high_lag1']-df['low_lag1']))
	return df[['lix_{}'.format(ticker.lower())]]  

def generate_LIX_means():
	dfs = [get_lix(x) for x in TICKERS ]
	df = pd.concat(dfs,axis=1)
	#df.plot()
	#plt.show()

	means = [df['lix_{}'.format(t)].mean() for t in TICKERS]
	return means
abool = False
holder = 90
def generate_animation(means,special_ticker):
	# imgmagick:https://stackoverflow.com/questions/44624479/how-to-use-imagemagick-with-xquartz
	# https://osxdaily.com/2012/12/02/x11-mac-os-x-xquartz/
	# https://stackoverflow.com/questions/43180357/how-to-rotate-a-3d-plot-in-python-or-as-a-animation-rotate-3-d-view-using-mou
	# https://stackoverflow.com/questions/18344934/animate-a-rotating-3d-graph-in-matplotlibhttps://stackoverflow.com/questions/18344934/animate-a-rotating-3d-graph-in-matplotlib
	fig = plt.figure()
	ax = fig.add_subplot(projection='3d')

	#ax.scatter(IV_30,HV_30, means)
	#plt.xlabel("IV_30/HV_30")
	#plt.ylabel("LIX Index")

	ax.set_xlabel('IV30',size=9,color='purple')
	ax.set_ylabel('HV30',size=9,color='purple')
	ax.set_zlabel('LIX',size=9,color='purple')


	for i in range(len(TICKERS)):
		if TICKERS[i]==special_ticker.lower():
			ax.scatter(IV_30[i],HV_30[i] ,means[i],color='red',alpha=0.5) 
			ax.text(IV_30[i],HV_30[i] ,means[i],TICKERS[i],size=8)
		else:
			ax.scatter(IV_30[i],HV_30[i] ,means[i],color='blue',alpha=0.4) 
			ax.text(IV_30[i],HV_30[i] ,means[i],TICKERS[i],size=7)

	plt.grid(True)


	

	def animate_fancy(i):
		global abool
		global holder 
		
		if holder==0:
			holder +=1
		if holder >90:
			holder-=1

		
		ax.view_init(elev=math.sin(math.pi*((i)/360))*12, azim=holder)


		#ax.view_init(elev=max(12,(i+.1)/15), azim=i)
		return fig,


	#rot_animation = animation.FuncAnimation(fig, rotate, frames=np.arange(0,362,2),interval=100)
	anim = animation.FuncAnimation(fig, animate_fancy, 
	                               frames=360, interval=70, blit=True)

	anim.save('lix_animated.gif', dpi=100, writer='imagemagick')
	print('Finished gif saved under lix_animated.gif')


def generate_plot(means,special_ticker):

	#fig, ax = plt.subplots()
	fig = plt.figure()
	ax = fig.add_subplot(projection='3d')

	#ax.scatter(IV_30,HV_30, means)
	#plt.xlabel("IV_30/HV_30")
	#plt.ylabel("LIX Index")

	ax.set_xlabel('IV30',size=9,color='purple')
	ax.set_ylabel('HV30',size=9,color='purple')
	ax.set_zlabel('LIX',size=9,color='purple')


	for i in range(len(TICKERS)):
		if TICKERS[i]==special_ticker.lower():
			ax.scatter(IV_30[i],HV_30[i] ,means[i],color='red',alpha=0.5) 
			ax.text(IV_30[i],HV_30[i] ,means[i],TICKERS[i],size=7)
		else:
			ax.scatter(IV_30[i],HV_30[i] ,means[i],color='blue',alpha=0.4) 
			ax.text(IV_30[i],HV_30[i] ,means[i],TICKERS[i],size=7)

	plt.grid(True)
	ax.view_init(azim=45+15+15+15+15+15+15,elev=15)
	plt.savefig('lix_static.jpeg', bbox_inches='tight',dpi=1200)
	#plt.show()
	print('Finished jpeg saved under lix_static.jpeg')


def main(special_ticker):
	means = generate_LIX_means()
	print('Generating static plot')
	generate_plot(means,special_ticker)

	print('Generating static animation')
	generate_animation(means,special_ticker)

if __name__ == '__main__':
	main('trit')


