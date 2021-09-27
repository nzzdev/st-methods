{\rtf1\ansi\ansicpg1252\cocoartf2580
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww17440\viewh19400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import yfinance as yf\
import pandas as pd\
from datetime import date, datetime, timedelta\
import json\
import os\
import sys\
\
\
if __name__ == \'82__main__\'91:\
	try:\
		# add parent directory to path so helpers file can be referenced\
		sys.path.append(os.path.dirname((os.path.dirname(__file__))))\
		from helpers import *\
\
		# set working directory, change if necessary\
		os.chdir(os.path.dirname(__file__))\
\
		tickers = ["3333.HK"] #Subtitute for the tickers you want\
		df = yf.download(tickers,  start = "2021-01-04" , end = date.today() + timedelta(days = 1))\
		q = df[['Close']].round(2)\
		update_chart(id=\'82https://q.st.nzz.ch/editor/chart/0c12cfcee36676f241145bcc4b82095b', data=q)\
\
		download(tickers,  start = date.today() - timedelta(days = 1), end = date.today() + timedelta(days = 1), interval = "1m")\
		df.index = df.index.tz_localize(None)\
		q2 = df[['Close']].round(2).to_clipboard()\
		update_chart(id=\'82https://q.st.nzz.ch/editor/chart/588c5ac3ed81d1c4d5db6c104132125d', data=q2)\
	except:\
		raise\
}