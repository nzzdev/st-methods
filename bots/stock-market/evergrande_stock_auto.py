import yfinance as yf
import pandas as pd
from datetime import date, datetime, timedelta
import json
import os
import sys



from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))

tickers = ["3333.HK"] #Subtitute for the tickers you want
df = yf.download(tickers,  start = "2021-01-04" , end = date.today() + timedelta(days = 1))
q = df[['Close']].round(2)

update_chart(id= '0c12cfcee36676f241145bcc4b82095b', data=q)

download(tickers,  start = date.today() - timedelta(days = 1), end = date.today() + timedelta(days = 1), interval = "1m")
df.index = df.index.tz_localize(None)
q2 = df[['Close']].round(2).to_clipboard()

update_chart(id= '588c5ac3ed81d1c4d5db6c104132125d', data=q2)
