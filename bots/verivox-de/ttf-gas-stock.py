import json
import pandas as pd
import os
from user_agent import generate_user_agent
import yfinance as yf
import numpy as np
from datetime import datetime

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *
        from market_ids import *

        # headers for ICE data
        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # download historical data from Yahoo
        df = yf.download('TTF=F', period='5y')
        df = df['Close'][df.index >= '2020-12-31'].to_frame().dropna()
        df.rename(columns={'Close': 'Kosten'}, inplace=True)
        df.index.rename('Datum', inplace=True)
        df['Kosten'] = df['Kosten'].round(2).astype(float)
        # drop last buggy value from Yahoo if current day
        today = datetime.today().strftime('%Y-%m-%d')
        if today == df.index[-1].strftime('%Y-%m-%d'):
            df.drop(df.tail(1).index, inplace=True)

        # get latest data from ICE (avoid errors with Yahoo Finance)
        url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getHistoricalChartDataAsJson=&marketId=' + \
            market_id + '&historicalSpan=1'
        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)
        df_ice = pd.DataFrame(full_data['bars'], columns=[
            'Datum', 'Kosten'])
        df_ice = df_ice.tail(1)
        df_ice['Datum'] = pd.to_datetime(df_ice['Datum'])
        df_ice['Datum'] = df_ice['Datum'].dt.strftime('%Y-%m-%d')
        df_ice['Datum'] = pd.to_datetime(df_ice['Datum'])
        df_ice.set_index('Datum', inplace=True)
        df_ice['Kosten'] = df_ice['Kosten'].round(
            2).astype(float)
        df = pd.concat([df, df_ice], axis=0)  # add value from ICE
        df = df[~df.index.duplicated(keep='last')]  # drop value from Yahoo
        df = df.sort_index()  # sort if older value is inserted due to wrong market ID

        # create chart with comparison
        dfold = pd.read_csv(
            './data/ttf-gas-stock-historical.tsv', sep='\t', index_col=None)
        year = datetime.now().year
        dfold['Datum'] = pd.to_datetime(dfold['Datum'])
        dfnew = dfold.merge(df, on='Datum', how='left')
        dfnew = dfnew[['Datum', 'Kosten', '2023', '2022', 'Vorkrisenniveau²']]
        dfnew = dfnew.rename(columns={'Kosten': f'{year}'})
        dfnew.set_index('Datum', inplace=True)
        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$', np.nan, regex=True)  # replace empty string with NaN
        dfnew[f'{year}'] = dfnew[f'{year}'].interpolate(
            method='linear', limit_direction='backward')  # for wrong dates
        dfnew = dfnew.drop('2023', axis=1)
        # get pre-crisis value
        mwh_new = dfnew['2024'].loc[dfnew['2024'].last_valid_index()]
        mwh_new_pos = dfnew['2024'].index.get_loc(
            dfnew['2024'].last_valid_index())
        mwh_old = dfnew.iloc[mwh_new_pos]['Vorkrisenniveau²']
        title_mwh_diff = round((mwh_new - mwh_old), 0).astype(int)
        title_mwh = round(mwh_new, 0).astype(int)
        dfnew[f'{year}'] = dfnew[f'{year}'].fillna('')
        # round values further for normal line chart
        df['Kosten'] = df['Kosten'].round(0).astype(int)

        """
        # get weekdays for current year from Dutch stock market
        # import pandas_market_calendars as mcal
        xams = mcal.get_calendar('LSE')  # ICE US
        early = xams.schedule(start_date='2024-01-01', end_date='2024-12-31')
        df_tradingdays = pd.DataFrame(pd.DatetimeIndex(
            mcal.date_range(early, frequency='1D')))
        """

        """
        # START historical ICE data from theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5396828
        url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getHistoricalChartDataAsJson=&marketId=' + \
            market_id + '&historicalSpan=3'
        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)

        # create dataframe and format date column
        df = pd.DataFrame(full_data['bars'], columns=['Datum', 'Kosten'])
        df['Datum'] = pd.to_datetime(df['Datum'])
        df.set_index('Datum', inplace=True)
        df = df['Kosten'][df.index >= '2020-12-31'].to_frame().dropna()

        # round numbers
        df['Kosten'] = df['Kosten'].round(0).astype(int)
        # END  old historical ICE data
        """

        # save current price as csv for dashboard
        df_intra_today = df.copy()
        #df_intra_today.index = pd.to_datetime(df_intra_today.index).strftime('%Y-%m-%d')
        df_intra_today = df_intra_today.rename(
            columns={df_intra_today.columns[0]: 'Gas-Börsenpreis'})
        df_intra_today = pd.concat(
            [df_intra_today.tail(2)])
        df_intra_today.to_csv('./data/ttf-gas-stock-dash.csv')

        """
        # START hourly prices (not reliable)
        # save current price as csv for dashboard
        # get latest intraday data from ICE (avoid errors with Yahoo Finance)
        url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getIntradayChartDataAsJson=&marketId=' + market_id
        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)
        df_intra = pd.DataFrame(full_data['bars'], columns=[
            'Datum', 'Intraday'])
        df_intra = df_intra.tail(1)
        df_intra['Datum'] = pd.to_datetime(df_intra['Datum'])
        df_intra.set_index('Datum', inplace=True)

        df_intra_today = df_intra.copy()
        df_intra_today = df.copy()
        #df_intra_today.index = pd.to_datetime(df_intra_today.index).strftime('%Y-%m-%d')
        df_intra_today = df_intra_today.rename(
            columns={df_intra_today.columns[0]: 'Gas-Börsenpreis'})
        df_intra_today = pd.concat(
            [df_intra_today.head(1), df_intra_today.tail(1)])
            [df_intra_today.tail(2)])
        df_intra_today.to_csv('./data/ttf-gas-stock-dash.csv')
        # END hourly prices (not reliable)

        # calculate intraday mean and drop everything except last row
        df_intra['Kosten'] = df_intra['Intraday'].mean()
        df_intra = df_intra.drop(df_intra.index.to_list()[0:-1], axis=0)
        df_intra = df_intra.drop('Intraday', axis=1)
        df_intra['Kosten'] = df_intra['Kosten'].round(0).astype(int)

        # create final dataframe with historical and intraday data
        # drop last pseudo historical value from Yahoo and replace with intraday data
        df.drop(df.tail(1).index, inplace=True)
        df_full = pd.concat([df, df_intra])
        """

        # dynamic chart title
        title_old = f'Gas kostet an der Börse {title_mwh} Euro je MWh'
        if title_mwh_diff > 0:
            title = f'Gas kostet an der Börse {title_mwh} Euro je MWh ‐ {title_mwh_diff} Euro mehr als vor der Krise'
        elif title_mwh_diff == 0:
            title = f'Gas kostet an der Börse {title_mwh} Euro je MWh ‐ so viel wie vor der Krise'
        else:
            title = f'Gas kostet an der Börse {title_mwh} Euro je MWh ‐ {abs(title_mwh_diff)} Euro weniger als vor der Krise'

        # create date for chart notes
        timecode = df.index[-1]  # old: df_full
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Preise für Terminkontrakte mit Lieferung im nächsten Monat.<br>Stand: ' + timecode_str
        notes_chart_new = '¹ Preise für Terminkontrakte mit Lieferung im nächsten Monat.<br>² Durchschnitt 2018-2020.<br>Stand: ' + timecode_str

        # convert DatetimeIndex
        #df_full.index = df_full.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(id='4decc4d9f742ceb683fd78fa5937acfd',
                     title=title_old, notes=notes_chart, data=df)  # old: df_full
        update_chart(id='74063b3ff77f45a56472a5cc70bb2a93',
                     title=title, notes=notes_chart_new, data=dfnew)
    except:
        raise
