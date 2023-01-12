"""
  Update 3. Januar 2023 @simonhuwiler
  - Jahr 2023 hinzugefügt, mit Check, ob es existiert.
  - Woche 53 entfernt. Die ist gleich wie Woche 0 des nächsten Jahres. Da in der ersten Woche des Januars jedoch nicht abgeschlossen, sind plötzlich unvollständige Daten drin.

"""

import pandas as pd
import json
import requests
import requests
from datetime import datetime as dt
import os

from helpers import *
pd.options.mode.chained_assignment = None

# 00 Preparations

# 01 Futures
def get_futures():
    #futures_headers = {
     #   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
      #  'Referer': 'https://www.eex.com/'
    #}

    # set up urls per country
    #ids = [('ch', 'FC'), ('fr', 'F7'), ('de', 'DE')]

    #base = 'https://webservice-eex.gvsi.com/query/json/getDaily/close/offexchtradevolumeeex/onexchtradevolumeeex/tradedatetimegmt/?priceSymbol=%22%2FE.'
    #middle = 'BQF23%22&chartstartdate=2021%2F07%2F07&chartstopdate='

    #stopdate = str(dt.today().year) + '%2F' + str(dt.today().strftime('%m')) + '%2F'+ str(dt.today().strftime('%d'))
    #end = '&dailybarinterval=Days&aggregatepriceselection=First'

    #future_urls = [(base + country[1] + middle + stopdate + end, country[0]) for country in ids]

    #def read_data_futures(url, country):
     #   r = requests.get(url, headers=futures_headers)
      #  data = r.json()
        
       # df = pd.DataFrame(data['results']['items'])
        #df['date'] = pd.to_datetime(df['tradedatetimegmt'], format='%m/%d/%Y %I:%M:%S %p')
        #df.drop('tradedatetimegmt', axis=1, inplace=True)

        #df = df[['date', 'close']]
        #df = df.rename(columns={'close': 'close_'+country})
        #return df

    #df_lst_futures = []
    #for url in future_urls: 
        #print(url)
     #   df_lst_futures.append(read_data_futures(url[0], url[1]))

    #futures_df =  df_lst_futures[0].merge( df_lst_futures[1])
    #futures_df = futures_df.merge(df_lst_futures[2])

    #futures_df = futures_df.rename(columns ={'close_ch':'Schweiz', 'close_fr': 'Frankreich', 'close_de':'Deutschland'})
    #futures_df['date'] = pd.to_datetime(futures_df['date'])
    
    #futures_df['Schweiz'] = futures_df['Schweiz'].round(1)
    #futures_df['Deutschland'] = futures_df['Deutschland'].round(1)
    #futures_df['Frankreich'] = futures_df['Frankreich'].round(1)

    #return futures_df

    market_id = '5980775'

    url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getHistoricalChartDataAsJson=&marketId=' + market_id + '&historicalSpan=3'
    resp = requests.get(url)
    json_file = resp.text
    full_data = json.loads(json_file)

    # create dataframe and format date column
    futures_df = pd.DataFrame(full_data['bars'], columns=['Datum', 'Preis'])
    futures_df['Datum'] = pd.to_datetime(df['Datum'])
    futures_df.set_index('Datum', inplace=True)
    futures_df = df['Preis'][df.index >= '2022-01-01'].to_frame().dropna()
    futures_df = futures_df.reset_index(level=0)
    
    return futures_df


# 02 Spotmarket
def get_spotmarket():
    
    spotmarket_df_day = pd.read_json('https://www.energiedashboard.admin.ch/api/preise/strom-boerse')

    #spotmarket_base = 'https://www.energy-charts.info/charts/price_spot_market/data/ch/year_'
    #spotmarket_urls = [spotmarket_base+ str(i) + '.json' for i in range(2020, 2024)]

    #def read_json(url, selection):
        #response = requests.get(url)

        # Jahr 2023 Stand 3. Januar 2023 noch nicht aufgeschaltet. Deshalb hier Check, ob existiert
        #if response.status_code == 404:
         #   print("🤬 API-Down oder nicht aufgeschaltet. URL:")
          #  print(url)
           # return []
        
        #data_json = response.json()
        
        #timestamps = data_json[0]['xAxisValues'] 
        #datetimes = [dt.fromtimestamp(stamp/1000).strftime('%Y-%m-%d %H:%M')  for stamp in timestamps]
        
        #als jsons noch alle gleich waren
        #prices = data_json[4]['data']
        
        # find element containing our prices
        #for elem in data_json:
         #   try:
          #      if 'Day Ahead Auktion' in elem['name']['de']:
           #         prices = elem['data']
            #except:
             #   if 'Day Ahead Auktion' in elem['name'][0]['de']:
              #      prices = elem['data']
        
        #if selection == 'dates':
         #   return datetimes
        #if selection == 'prices':
         #   return prices

    #multi_year_dates = []
    #multi_year_prices = []


    #for market_url in spotmarket_urls:
     #   multi_year_dates = multi_year_dates + read_json(market_url, 'dates')
      #  multi_year_prices = multi_year_prices + read_json(market_url, 'prices')

    #spotmarket_df = pd.DataFrame({'date': multi_year_dates, 'price':multi_year_prices})
    #spotmarket_df['date'] = pd.to_datetime(spotmarket_df['date'])

    # calculate day means
    #spotmarket_df_day = spotmarket_df.groupby(spotmarket_df.date.dt.date).mean().reset_index()
    #spotmarket_df_day = spotmarket_df_day.round(2)
    #spotmarket_df_day = spotmarket_df_day.dropna()

    return spotmarket_df_day



# 03 Atomstrom Frankreich
def get_atomstrom_frankreich():
    #akw_base = 'https://www.energy-charts.info/charts/energy/data/fr/week_'
    #akw_urls = [akw_base+ str(i) + '.json' for i in range(2019, 2024)]

    #def read_json_akw(url, selection):
     #   response = requests.get(url)
      #  data_json = response.json()
        
       # timestamps = data_json[0]['xAxisValues'] 
        
        # find element containing our data
        #for elem in data_json:
         #   try:
          #      if 'Kernenergie' in elem['name']['de']:
           #         volume = elem['data']
            #except:
             #   if 'Kernenergie' in elem['name'][0]['de']:
              #      volume = elem['data']
        
        #if selection == 'dates':
         #   return timestamps[0:52]
        #if selection == 'volume':
         #   return volume[0:52]

    #akw_dates = []
    #akw_volume = []
    #akw_year = []

    #for url in akw_urls:
     #   akw_dates = akw_dates + read_json_akw(url, 'dates')
      #  akw_volume = akw_volume +read_json_akw(url, 'volume')
       # akw_year = akw_year + len(read_json_akw(url, 'dates')) * [url[-9:-5]]

    #akw_df = pd.DataFrame({'date': akw_dates,'year':akw_year, 'volume':akw_volume})

    #akw_df = akw_df.iloc[:-1]

    # to waterfall-layout

    #akw_df_wide = akw_df.pivot(index='date', columns='year', values='volume').reset_index()

    #akw_df_wide['q_date'] = '2000-W' + akw_df_wide['date'].astype(str)

    #return akw_df_wide


    akw_base = 'https://www.energy-charts.info/charts/energy/data/fr/day_'
    akw_urls = [akw_base + str(i) + '.json' for i in range(2019, 2024)]

    def read_json_akw(url, selection):
        response = requests.get(url)
        data_json = response.json()
        
        timestamps = data_json[0]['xAxisValues'] 
        
        # find element containing our data
        for elem in data_json:
            try:
                if 'Kernenergie' in elem['name']['de']:
                    volume = elem['data']
            except:
                if 'Kernenergie' in elem['name'][0]['de']:
                    volume = elem['data']
        
        if selection == 'dates':
            return timestamps[0:365]
        if selection == 'volume':
            return volume[0:365]

    akw_dates = []
    akw_volume = []
    akw_year = []

    for url in akw_urls:
        akw_dates = akw_dates + read_json_akw(url, 'dates')
        akw_volume = akw_volume +read_json_akw(url, 'volume')
        akw_year = akw_year + len(read_json_akw(url, 'dates')) * [url[-9:-5]]

    akw_df = pd.DataFrame({'date': akw_dates,'year': akw_year, 'volume': akw_volume})

    akw_df = akw_df.iloc[:-1]

    akw_df['date'] = pd.to_datetime(akw_df['date'], format = '%d.%m.%Y')
    akw_df.set_index('date', inplace=True)
    akw_df['volume'] = akw_df['volume'].rolling(14).mean()
    akw_df.reset_index(inplace=True)

    akw_df = akw_df[pd.to_datetime(akw_df['date']) >= '2022-01-01']
    
    return akw_df_wide
