import pandas as pd
import json
import requests
from urllib.request import urlopen
from datetime import datetime as dt
import os

from helpers import *
pd.options.mode.chained_assignment = None

# 00 Preparations

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# set date
q_date = 'Stand: '+ dt.now().strftime("%-d. %-m. %Y")

# 01 Futures

futures_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'Referer': 'https://www.eex.com/'
}

# set up urls per country
ids = [('ch', 'FC'), ('fr', 'F7'), ('de', 'DE')]

base = 'https://webservice-eex.gvsi.com/query/json/getDaily/close/offexchtradevolumeeex/onexchtradevolumeeex/tradedatetimegmt/?priceSymbol=%22%2FE.'
middle = 'BQF23%22&chartstartdate=2021%2F07%2F07&chartstopdate='
stopdate = str(dt.today().year) + '%2F' + str(dt.today().strftime('%m')) + '%2F'+ str(dt.today().strftime('%d'))
end = '&dailybarinterval=Days&aggregatepriceselection=First'

future_urls = [(base + country[1] + middle + stopdate + end, country[0]) for country in ids]

def read_data_futures(url, country):
    r = requests.get(url, headers=futures_headers)
    data = r.json()
    
    df =pd.DataFrame(data['results']['items'])
    df['date'] = pd.to_datetime(df['tradedatetimegmt'], format='%m/%d/%Y %I:%M:%S %p')
    df.drop('tradedatetimegmt', axis=1, inplace=True)

    df = df[['date', 'close']]
    df = df.rename(columns={'close': 'close_'+country})
    return df

df_lst_futures = []
for url in future_urls: 
    #print(url)
    df_lst_futures.append(read_data_futures(url[0], url[1]))

futures_df =  df_lst_futures[0].merge( df_lst_futures[1])
futures_df = futures_df.merge(df_lst_futures[2])

futures_df = futures_df.rename(columns ={'close_ch':'Schweiz', 'close_fr': 'Frankreich', 'close_de':'Deutschland'})
futures_df['date'] = pd.to_datetime(futures_df['date'])


# to q
futures_q_id = 'de091de1c8d4f5042323dbd9e08c9548'

update_chart(id=futures_q_id, 
            data=futures_df,
            notes = q_date)

#futures_df.to_csv('test_futures.csv')


# 02 Spotmarket

spotmarket_base = 'https://www.energy-charts.info/charts/price_spot_market/data/ch/year_'
spotmarket_urls = [spotmarket_base+ str(i) + '.json' for i in range(2020, 2023)]

def read_json(url, selection):
    response = urlopen(url)
    data_json = json.loads(response.read())
    
    timestamps = data_json[0]['xAxisValues'] 
    datetimes = [dt.fromtimestamp(stamp/1000).strftime('%Y-%m-%d %H:%M')  for stamp in timestamps]
    
    #als jsons noch alle gleich waren
    #prices = data_json[4]['data']
    
    # find element containing our prices
    for elem in data_json:
        try:
            if 'Day Ahead Auktion' in elem['name']['de']:
                prices = elem['data']
        except:
            if 'Day Ahead Auktion' in elem['name'][0]['de']:
                prices = elem['data']
    
    if selection == 'dates':
        return datetimes
    if selection == 'prices':
        return prices

multi_year_dates = []
multi_year_prices = []


for market_url in spotmarket_urls:
    multi_year_dates = multi_year_dates +read_json(market_url, 'dates')
    multi_year_prices = multi_year_prices +read_json(market_url, 'prices')

spotmarket_df = pd.DataFrame({'date': multi_year_dates, 'price':multi_year_prices})
spotmarket_df['date'] = pd.to_datetime(spotmarket_df['date'])

# calculate day means
spotmarket_df_day = spotmarket_df.groupby(spotmarket_df.date.dt.date).mean().reset_index()
spotmarket_df_day = spotmarket_df_day.round(2)

spot_market_q_id = '046c2f2cc67578f60cc5c36ce55d27ae'

update_chart(id=spot_market_q_id, 
            data=spotmarket_df_day,
            notes = q_date)

#spotmarket_df.to_csv('test_spotmarket.csv')


# 03 Atomstrom Frankreich

akw_base = 'https://www.energy-charts.info/charts/energy/data/fr/week_'
akw_urls = [akw_base+ str(i) + '.json' for i in range(2019, 2023)]

def read_json_akw(url, selection):
    response = urlopen(url)
    data_json = json.loads(response.read())
    
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
        return timestamps
    if selection == 'volume':
        return volume

akw_dates = []
akw_volume = []
akw_year = []

for url in akw_urls:
    akw_dates = akw_dates +read_json_akw(url, 'dates')
    akw_volume = akw_volume +read_json_akw(url, 'volume')
    akw_year = akw_year + len(read_json_akw(url, 'dates')) * [url[-9:-5]]

akw_df = pd.DataFrame({'date': akw_dates,'year':akw_year, 'volume':akw_volume})

akw_df = akw_df.iloc[:-1]

# to waterfall-layout

akw_df_wide = akw_df.pivot(index='date', columns='year', values='volume').reset_index()

akw_df_wide['q_date'] = '2000-W' + akw_df_wide['date'].astype(str)
akw_df_wide = akw_df_wide[['q_date','2019','2020','2021','2022']]

akw_q_id = '4d6b0595264016839099c06df6bdd6af'

update_chart(id=akw_q_id, 
            data=akw_df_wide,
            notes = q_date)

#akw_df_wide.to_csv('test_akw.csv')
