#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 18:26:58 2022

@author: florianseliger
"""

import pandas as pd
from datetime import datetime as dt, timedelta
import fnmatch
import os

from helpers import *
# Set Working Directory
os.chdir(os.path.dirname(__file__))

### Preismonitor

today = dt.today()
past = today - timedelta(days = 28)

week_day = today.isocalendar()[2]

# get starting date (Monday) for the respective week
start_date = today - timedelta(days=week_day-1) 

# Prints the list of dates in a current week
dates = [str((start_date + timedelta(days=i)).date()) for i in range(7)]



food_drinks = ['drinks', 'sweet', 'provision', 'meat', 'vegi', 'milk', 'bread']

df_t = pd.DataFrame()
for i in food_drinks:
    try:
        df_ = pd.read_excel(f'./output/' + i + '_coop_' + today.strftime('%Y-%m-%d') + '.xlsx')
        #df_ = pd.read_excel('/Users/florianseliger/Documents/GitHub/st-methods/bots/crawl_ch/output/' + i + '_coop_' + today.strftime('%Y-%m-%d') + '.xlsx')
        df_t = pd.concat([df_t, df_], ignore_index = True)
    except:
        for j in dates:
            try:
                df_ = pd.read_excel(f'./output/' + i + '_coop_' + j + '.xlsx')
                #df_ = pd.read_excel('/Users/florianseliger/Documents/GitHub/st-methods/bots/crawl_ch/output/' + i + '_coop_' + j + '.xlsx')
                df_t = pd.concat([df_t, df_], ignore_index = True)
            except:
                continue
            break
        

        
        
df_t = df_t.dropna(subset = ['price']).reset_index(drop = True)
     

# exclude "Aktionen" and clean
df_t = df_t[~df_t['productAriaLabel'].str.contains('Aktion')]
df_t['title'] = df_t['title'].str.replace('\xa0', '')
df_t['title'] = df_t['title'].str.replace('&amp;', '&')

# only Prix Garantie
df_t = df_t[df_t['title'].str.contains('Prix Garantie')].copy()


# data from one month ago
week_day = past.isocalendar()[2]

# get starting date (Monday) for the respective week
start_date = past - timedelta(days=week_day-1) 

# Prints the list of dates in a current week
dates = [str((start_date + timedelta(days=i)).date()) for i in range(7)]


food_drinks = ['drinks', 'sweet', 'provision', 'meat', 'vegi', 'milk', 'bread']

df_y = pd.DataFrame()
for i in food_drinks:
    try:
        df_ = pd.read_excel(f'./output/' + i + '_coop_' + past.strftime('%Y-%m-%d') + '.xlsx')
        #df_ = pd.read_excel('/Users/florianseliger/Documents/GitHub/st-methods/bots/crawl_ch/output/' + i + '_coop_' + past.strftime('%Y-%m-%d') + '.xlsx')
        df_y = pd.concat([df_y, df_], ignore_index = True)
    except:
        for j in dates:
            try:
                df_ = pd.read_excel(f'./output/' + i + '_coop_' + j + '.xlsx')
                #df_ = pd.read_excel('/Users/florianseliger/Documents/GitHub/st-methods/bots/crawl_ch/output/' + i + '_coop_' + j + '.xlsx')
                df_y = pd.concat([df_y, df_], ignore_index = True)
            except:
                continue
            break
        
df_y = df_y.dropna(subset = ['price']).reset_index(drop = True)

# exclude "Aktionen" and clean
df_y = df_y[~df_y['productAriaLabel'].str.contains('Aktion')]
df_y['title'] = df_y['title'].str.replace('\xa0', '')
df_y['title'] = df_y['title'].str.replace('&amp;', '&')

# only Prix Garantie
df_y = df_y[df_y['title'].str.contains('Prix Garantie')].copy()

df_t = df_t[['id', 'title', 'price', 'priceContextAmount']].copy()
df_y = df_y[['id', 'title', 'price', 'priceContextAmount']].copy()
df_t.rename({'price': 'Neuer Preis'}, axis = 1, inplace = True)
df_y.rename({'price': 'Alter Preis'}, axis = 1, inplace = True)

df_t_y = df_t.merge(df_y, on = ['id', 'title', 'priceContextAmount'])
df_t_y.drop_duplicates(inplace = True)

df_t_y['Differenz'] = df_t_y['Neuer Preis'] - df_t_y['Alter Preis']
df_t_y['perc_change'] = df_t_y['Differenz']*100/df_t_y['Alter Preis']
df_t_y['perc_change'] = df_t_y['perc_change'].round(1)
df_t_y['Differenz'] = df_t_y['Differenz'].round(1)
df_t_y = df_t_y[df_t_y['Differenz'] != 0]

#df_t_y.loc[df_t_y['Differenz'] > 0, ''] = '↑' 
#df_t_y.loc[df_t_y['Differenz'] < 0, ''] = '↓' 


df_t_y['title'] = df_t_y['title'].str.replace(' ca.', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Prix Garantie ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Betty Bossi ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Naturaplan ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Naturafarm ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' fettreduziert', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' Fettreduziert', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Delikatess-', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Delikatess ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Feiner ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Feine ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Hauchzarter ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Hauchzartes ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Saftige ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' fein', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' grob', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Arabica-Robusta-Mischung', '', regex = False)

# title fixes

bulkpacks = {'Apfelsaft': 'Apfelsaft 6l', 'Multivitaminsaft': 'Multivitaminsaft 6l', 'Orangensaft': 'Orangensaft 6l', 'Orangennektar': 'Orangennektar 9l', 
             'Hamburger': 'Hamburger 1kg', 'Chicken Nuggets': 'Chicken Nuggets 1kg', 'Cevapcici für Pfanne und Grill': 'Cevapcici 1kg', 'Hähnchenschenkel natur': 'Hähnchenschenkel natur 1kg', 
             'Sahnejoghurt nach griechischer Art': 'Sahnejoghurt griechische Art 1kg', 'Basmati Reis': 'Basmati Reis 1kg', 'Parboiled Spitzenreis Langkornreis': 'Parboiled Langkornreis 1kg', 
             'Blumenkohl': 'Blumenkohl 1kg', 'Rosenkohl': 'Rosenkohl 1kg', 'Brechbohnen': 'Brechbohnen 1kg', 'Weizenmehl Type': 'Weizenmehl'
            }

df_t_y['title'] = df_t_y['title'].astype(
    str).str.replace(r'\s\d.*', r'', regex=True)
df_t_y['title'] = df_t_y['title'].astype(
    str).str.replace(r'\smit\s.*', r'', regex=True)
df_t_y['title'] = df_t_y['title'].astype(
    str).str.replace(' ca.', '', regex=False)

# Fix for large quantities
df_t_y['title'] = df_t_y['title'].astype(str).replace(bulkpacks)

df_t_y.sort_values(by = ['Differenz'], inplace = True, ascending = False)

df_t_y.rename(columns = {'perc_change': ''}, inplace = True)
df_t_y = df_t_y[['', 'title', 'Alter Preis', 'Neuer Preis']].copy()
df_t_y.rename({'title': ''}, axis = 1, inplace = True)


notes = 'Stand: ' + today.strftime('%d. %m. %Y')

update_chart(id = '8676bad64564b4740f74b6d5d0757a95',
                 data = df_t_y, notes=notes)

