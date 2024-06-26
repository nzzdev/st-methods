#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 17:52:11 2023

@author: florianseliger
"""


import yfinance as yf
from datetime import date, timedelta
import os
import pandas as pd

import json
from urllib.request import urlopen

from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))




# Credit Suisse

tickers = ["CSGN.SW"]  
df_1 = yf.download(tickers,  period = "1y", interval = "1d")
df_1 = df_1['Close'].to_frame().dropna().reset_index(level = 0)

notes = 'Für den laufenden Tag wird der aktuelle Kurs angezeigt (Intraday).'

update_chart(id='9039ce8be0b7e1650165751c47d993d4',
                 data=df_1, notes = notes)


df_1 = yf.download(tickers,  period = "1mo", interval = "1d")
df_1 = df_1['Close'].to_frame().dropna().reset_index(level = 0)

update_chart(id='15f38f200afda5632efee1ff19b0d7c2',
                 data=df_1, notes = notes)


date_today = date.today()

#date_yesterday = date.today() - timedelta(1)

close = df_1[(df_1['Date'] != df_1['Date'].max().strftime('%Y-%m-%d'))]
close = close[(close['Date'] == close['Date'].max().strftime('%Y-%m-%d'))]

df_2 = yf.download(tickers,  period = "1d", interval = "1m")
df_2 = df_2['Close'].to_frame().dropna().reset_index(level = 0)
df_2 = df_2.rename(columns = {'Datetime': 'Date'})

#yesterday = date_yesterday.strftime('%d.%m.%Y')
last = close['Date'].dt.strftime("%d. %m. %Y")

df_2['Date'] = df_2['Date'].astype(str)

df_2['Date'] = df_2['Date'].str.slice(start = 0, stop = 19)

df_2 = df_2.rename(columns = {'Close': 'Aktueller Kurs'})

#df_2['Schlusskurs am ' + last] = close.Close

df_2.fillna(method='ffill', inplace=True)


notes = 'Die Grafik wird wochentags ab 9.30 Uhr alle 30 Minuten aktualisiert.'

update_chart(id = '0e4679180159fe79f9fd140fe620b4e3', data = df_2, notes = notes)


df_3 = yf.download(tickers,  period = "16y", interval = "1d")
df_3 = df_3['Close'].rolling(7).mean().dropna().reset_index(level = 0)

update_chart(id = '0e4679180159fe79f9fd140fe63e3945', data = df_3)




# UBS

tickers = ["UBSG.SW"]  
df_1 = yf.download(tickers,  period = "1y", interval = "1d")
df_1 = df_1['Close'].to_frame().dropna().reset_index(level = 0)

notes = 'Für den laufenden Tag wird der aktuelle Kurs angezeigt (Intraday).'

update_chart(id='ed07cc2c8f03f75c601766ce21985353',
              data=df_1, notes = notes)


df_1 = yf.download(tickers,  period = "1mo", interval = "1d")
df_1 = df_1['Close'].to_frame().dropna().reset_index(level = 0)

update_chart(id='ed07cc2c8f03f75c601766ce21a68d20',
              data=df_1, notes = notes)





# Bankenvergleich
tickers = ["CSGN.SW", "BNP.PA", "UBSG.SW", "DBK.DE", "GLE.PA", "UCG.MI"]  # Subtitute for the tickers you want
df_4 = yf.download(tickers,  period = "1y", interval = "1d")

df_4 = df_4['Close']

for i in tickers:
    x = df_4[i].head(1)
    df_4[i] = df_4[i]*100/x.values


df_4 = df_4.rename(columns = {'CSGN.SW': 'Credit Suisse', 'BNP.PA': 'BNP Paribas', 'UBSG.SW': 'UBS', 'DBK.DE': 'Deutsche Bank', 'GLE.PA': 'Société Générale', 'UCG.MI': 'Unicredit'})

df_4 = df_4[['Credit Suisse', 'BNP Paribas', 'UBS', 'Deutsche Bank',  'Unicredit']]

df_4 = df_4.reset_index()

update_chart(id = '7b974a9aaf4217d71f83fde19d517265', data = df_4)


df_4_ = yf.download(tickers,  period = "1mo", interval = "1d")

df_4_ = df_4_['Close']

for i in tickers:
    x = df_4_[i].head(1)
    df_4_[i] = df_4_[i]*100/x.values


df_4_ = df_4_.rename(columns = {'CSGN.SW': 'Credit Suisse', 'BNP.PA': 'BNP Paribas', 'UBSG.SW': 'UBS', 'DBK.DE': 'Deutsche Bank', 'GLE.PA': 'Société Générale', 'UCG.MI': 'Unicredit'})

df_4_ = df_4_[['Credit Suisse', 'BNP Paribas', 'UBS', 'Deutsche Bank',  'Unicredit']]

df_4_ = df_4_.reset_index()

update_chart(id = '7b974a9aaf4217d71f83fde19d59687a', data = df_4_)



# SMI & DAX

url = 'https://www.six-group.com/fqs/charts.json?select=ValorId&where=ValorId=CH0009980894CHF9&netting=2&fromdate=' + date_today.strftime('%Y%m%d') + '&todate=' + date_today.strftime('%Y%m%d') 

response = urlopen(url)
d = json.loads(response.read())

d_dict = d['valors'][0]['data']

df = pd.DataFrame(d_dict)

df['Date'] = pd.to_datetime(df['Date'], format = '%Y%m%d') 
df = df[['Date', 'Close']].tail(1)

smi = pd.read_csv('https://www.six-group.com/exchanges/downloads/indexdata/hsmi.csv', sep = ';', skiprows = 4)
smi['DATE'] = pd.to_datetime(smi['DATE'], format = '%d.%m.%Y')
smi.sort_values(by = 'DATE', ascending = True, inplace = True)
smi = smi[['DATE', 'Close']]
smi = smi[smi['DATE'] >= '2022-01-01']

smi.rename(columns={smi.columns[0]: 'Date'}, inplace=True)

smi = pd.concat([smi, df])

update_chart(id='1dda540238574eac80e865faa0dc2348', data=smi)


#first = date_today.replace(day=1)
#last_month = first - timedelta(days=1)




#dax = df['Close']['^GDAXI'][df.index >=
        #                    '2022-01-01'].to_frame().dropna().reset_index(level=0)
#dax.index = dax.index.strftime('%Y-%m-%d')
#update_chart(id='a78c9d9de3230aea314700dc582d873d', data=dax)


# Country Garden

tickers = ["2007.HK"]  
df_5 = yf.download(tickers,  period = "1mo", interval = "1d")
df_5 = df_5['Close'].to_frame().dropna().reset_index(level = 0)

notes = 'Für den laufenden Tag wird der aktuelle Kurs angezeigt (Intraday).'

update_chart(id='bc8cbef1bec81fe4197d1ebeb4d25691',
                 data=df_5, notes = notes)

