import json
import pandas as pd
import os
from user_agent import generate_user_agent
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from datawrapper import Datawrapper

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *
        from market_ids import *

        # Datawrapper API key
        dw_key = os.environ['DATAWRAPPER_API']
        dw = Datawrapper(access_token=dw_key)
        dw_id = 'C3pJx'

        # headers for ICE data
        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # download historical data from Yahoo
        df = yf.download('TTF=F', period='5y', auto_adjust=False)
        # extract the 'Close' column and convert to DataFrame
        df = df[('Close', 'TTF=F')]
        df = df[df.index >= '2020-12-31'].dropna()
        df = df.to_frame(name='Kosten')
        df.index.rename('Datum', inplace=True)
        df['Kosten'] = df['Kosten'].round(2).astype(float)

        """
        # as Dataframe instead of Series
        # extract the Series and convert to DataFrame
        df = df[('Close', 'TTF=F')]
        df = df[df.index >= '2020-12-31'].dropna()
        df = df.to_frame(name='Kosten')

        # rename the index and adjust values
        df.index.rename('Datum', inplace=True)
        df['Kosten'] = df['Kosten'].round(2).astype(float)
        """
        # drop last buggy value from Yahoo if current day
        today = datetime.today().strftime('%Y-%m-%d')
        if today == df.index[-1].strftime('%Y-%m-%d'):
            df.drop(df.tail(1).index, inplace=True)

        # get latest data from ICE (avoid errors with Yahoo Finance)
        url = 'https://www.ice.com/marketdata/api/productguide/charting/data/historical?marketId=' + \
            market_id + '&historicalSpan=2'
        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)

        # Determine bars data in ICE response (key may vary)
        bars = None
        for key in ['bars', 'data']:
            if key in full_data and full_data[key]:
                bars = full_data[key]
                break
        if not bars and isinstance(full_data.get('series'), list):
            for series_entry in full_data['series']:
                if 'bars' in series_entry and series_entry['bars']:
                    bars = series_entry['bars']
                    break

        # If no ICE data found, skip merging ICE price
        if not bars:
            print("Warning: No ICE data found; skipping ICE update")
        else:
            df_ice = pd.DataFrame(bars, columns=['Datum', 'Kosten'])
            df_ice = df_ice.tail(1)
            df_ice['Datum'] = pd.to_datetime(df_ice['Datum']).dt.strftime('%Y-%m-%d')
            df_ice['Datum'] = pd.to_datetime(df_ice['Datum'])
            df_ice.set_index('Datum', inplace=True)
            df_ice['Kosten'] = df_ice['Kosten'].round(2).astype(float)
            # merge with main DataFrame, avoiding duplicates
            df = pd.concat([df, df_ice], axis=0)
            df = df[~df.index.duplicated(keep='last')]
            df = df.sort_index()

        # create chart with comparison
        dfold = pd.read_csv(
            './data/ttf-gas-stock-historical.tsv', sep='\t', index_col=None)
        yesterday_year = datetime.now() - timedelta(days=1)
        year = yesterday_year.year
        dfold['Datum'] = pd.to_datetime(dfold['Datum'])
        dfnew = dfold.merge(df, on='Datum', how='left')
        dfnew = dfnew[['Datum', 'Kosten', '2024', '2023', '2022', 'Vorkrisenniveau²']]
        dfnew = dfnew.rename(columns={'Kosten': f'{year}'})
        dfnew.set_index('Datum', inplace=True)
        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$', np.nan, regex=True)  # replace empty string with NaN
        dfnew[f'{year}'] = dfnew[f'{year}'].interpolate(
            method='linear', limit_direction='backward')  # for wrong dates
        dfnew = dfnew.drop('2023', axis=1)
        dfnew = dfnew.drop('2024', axis=1)

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

        # convert Euro / MWh to Cent / kWh
        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$', np.nan, regex=True)
        dfnew = dfnew.divide(10).round(3)
        df = df.divide(10)

        # get pre-crisis value
        kwh_new = dfnew[f'{year}'].loc[dfnew[f'{year}'].last_valid_index()]
        kwh_new_pos = dfnew[f'{year}'].index.get_loc(
            dfnew[f'{year}'].last_valid_index())
        kwh_old = dfnew.iloc[kwh_new_pos]['Vorkrisenniveau²']
        title_kwh_diff = round((kwh_new - kwh_old), 1)
        title_kwh_diff_perc = round(
            100 * (kwh_new - kwh_old) / kwh_old, 0).astype(int)
        title_kwh = round(kwh_new, 1)
        dfnew[f'{year}'] = dfnew[f'{year}'].fillna('')  # replace NaN for Q

        # dynamic chart title
        title_old = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent'
        if title_kwh_diff > 0:
            title = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {title_kwh_diff_perc} Prozent mehr als vor der Krise'
        elif title_kwh_diff == 0:
            title = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – so viel wie vor der Krise'
        else:
            title = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {abs(title_kwh_diff_perc)} Prozent weniger als vor der Krise'

        """
        title_old = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent'
        if title_kwh_diff > 0:
            title = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {title_kwh_diff.astype(str).replace(".", ",")} Cent mehr als vor der Krise'
        elif title_kwh_diff == 0:
            title = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – so viel wie vor der Krise'
        else:
            title = f'Gas kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {abs(title_kwh_diff).astype(str).replace(".", ",")} Cent weniger als vor der Krise'
        """

        # create date for chart notes
        timecode = df.index[-1]  # old: df_full
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Preise für Terminkontrakte mit Lieferung im jeweils nächsten Monat.<br>Stand: ' + timecode_str
        notes_chart_new = '¹ Preise für Terminkontrakte mit Lieferung im jeweils nächsten Monat.<br>² Durchschnitt 2018-2020.<br>Stand: ' + timecode_str

        # convert DatetimeIndex
        #df_full.index = df_full.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(id='4decc4d9f742ceb683fd78fa5937acfd',
                     title=title_old, notes=notes_chart, data=df)  # old: df_full
        update_chart(id='74063b3ff77f45a56472a5cc70bb2a93',
                     title=title, notes=notes_chart_new, data=dfnew)

        # Rename column for Datawrapper
        dfnew = dfnew.rename(
            columns={'Vorkrisenniveau²': 'Vorkrisen-Niveau²'})

        # update Datawrapper chart
        dfnew.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id, data=dfnew)
        dw.update_chart(chart_id=dw_id, title=title)
        date = {'annotate': {'notes': f' {notes_chart_new}'}}
        dw.update_metadata(chart_id=dw_id, metadata=date)
        dw.publish_chart(chart_id=dw_id, display=False)

    except:
        raise
