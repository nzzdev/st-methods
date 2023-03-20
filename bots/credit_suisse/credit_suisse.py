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

from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))


# SIX
#df = pd.read_json('https://www.six-group.com/fqs/charts.json?select=ValorId&where=ValorId=CH0012138530CHF4&netting=2&fromdate=20230316&todate=20230316')


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


notes = 'Die Grafik wird wochentags ab 9.15 Uhr alle 30 Minuten aktualisiert.'

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


df_4 = df_4.rename(columns = {'CSGN.SW': 'Credit Suisse', 'BNP.PA': 'BNP Paribas', 'UBSG.SW': 'UBS', 'DBK.DE': 'Deutsche Bank', 'GLE.PA': 'Société Générale', 'UCG.MI': 'UniCredit'})

df_4 = df_4[['Credit Suisse', 'BNP Paribas', 'UBS', 'Deutsche Bank',  'UniCredit']]

df_4 = df_4.reset_index()

update_chart(id = '7b974a9aaf4217d71f83fde19d517265', data = df_4)


df_4 = yf.download(tickers,  period = "1mo", interval = "1d")

df_4 = df_4['Close']

for i in tickers:
    x = df_4[i].head(1)
    df_4[i] = df_4[i]*100/x.values


df_4 = df_4.rename(columns = {'CSGN.SW': 'Credit Suisse', 'BNP.PA': 'BNP Paribas', 'UBSG.SW': 'UBS', 'DBK.DE': 'Deutsche Bank', 'GLE.PA': 'Société Générale', 'UCG.MI': 'UniCredit'})

df_4 = df_4[['Credit Suisse', 'BNP Paribas', 'UBS', 'Deutsche Bank',  'UniCredit']]

df_4 = df_4.reset_index()

update_chart(id = '7b974a9aaf4217d71f83fde19d59687a', data = df_4)
