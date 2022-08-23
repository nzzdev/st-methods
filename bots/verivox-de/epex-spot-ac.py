import pandas as pd
import json
from datetime import datetime as dt
import os
from user_agent import generate_user_agent

if __name__ == '__main__':
    try:

        from helpers import *

        # set Working Directory
        os.chdir(os.path.dirname(__file__))

        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        spotmarket_base = 'https://www.energy-charts.info/charts/price_spot_market/data/de/year_'
        spotmarket_urls = [spotmarket_base +
                           str(i) + '.json' for i in range(2020, 2023)]

        def read_json(url, selection):
            response = download_data(url, headers=fheaders)
            json_file = response.text
            data_json = json.loads(json_file)

            timestamps = data_json[0]['xAxisValues']
            datetimes = [dt.fromtimestamp(
                stamp/1000).strftime('%Y-%m-%d %H:%M') for stamp in timestamps]

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
            multi_year_dates = multi_year_dates + \
                read_json(market_url, 'dates')
            multi_year_prices = multi_year_prices + \
                read_json(market_url, 'prices')

        df = pd.DataFrame(
            {'date': multi_year_dates, 'price': multi_year_prices})
        df['date'] = pd.to_datetime(df['date'])

        # calculate day means
        df_day = df.groupby(
            df.date.dt.date).mean().reset_index()
        df_day['price'] = df_day['price'].rolling(window=7).mean().dropna()
        df_day['price'] = df_day['price'].round(0)

        # get date
        # df_day = df_day.drop(df_day.tail(1).index)
        q_date = df_day['date'].iloc[-1]
        notes_chart = 'Stand: ' + q_date.strftime("%-d. %-m. %Y")

        # drop index and unused dates
        df_day = df_day.set_index('date')
        df_day.index = pd.to_datetime(df_day.index)
        df_day = df_day['2021-01-01': q_date]
        df_day['price'] = df_day['price'].astype(int)

        # run Q function
        update_chart(id='90005812afc9964bbfe4f952f51d6a57',
                     notes=notes_chart, data=df_day)
    except:
        raise
