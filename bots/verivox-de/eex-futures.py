import requests
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *

        # generate dates for url
        tday = datetime.today() - timedelta(days=1)
        yday = datetime.today() - timedelta(days=2)
        tdayurl = tday.strftime('%Y/%m/%d')
        tdayurl = tdayurl.replace('/', '%2F')
        ydayurl = yday.strftime('%Y/%m/%d')
        ydayurl = ydayurl.replace('/', '%2F')

        headers = {
            'Referer': 'https://www.eex.com/',
            'Origin': 'https://www.eex.com',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'de,en-US;q=0.9,en;q=0.8,en-GB;q=0.7',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36'
        }

        url = f'https://webservice-eex.gvsi.com/query/json/getChain/gv.pricesymbol/gv.displaydate/gv.expirationdate/tradedatetimegmt/gv.eexdeliverystart/ontradeprice/close/onexchsingletradevolume/onexchtradevolumeeex/offexchtradevolumeeex/openinterest/?optionroot=%22%2FE.DEBY%22&expirationdate={ydayurl}&onDate={tdayurl}'

        # get JSON
        r = requests.get(url, headers=headers)
        dictr = r.json()
        recs = dictr['results']['items']
        df = pd.json_normalize(recs)  # first line is next year ("/E.DEBYF2x")

        # drop everything except "close" and date
        df = df.head(1).filter(['close', 'tradedatetimegmt'])

        # convert do datetimeindex
        df['tradedatetimegmt'] = pd.to_datetime(df['tradedatetimegmt'])
        year = df['tradedatetimegmt'].dt.strftime(
            '%Y').iloc[0]  # get year for column
        df = df.rename(
            columns={'tradedatetimegmt': 'Datum', 'close': f'{year}'})
        df['Datum'] = df['Datum'].dt.strftime('%Y-%m-%d')
        df['Datum'] = pd.to_datetime(df['Datum'])
        df.set_index('Datum', inplace=True)
        df[f'{year}'] = df[f'{year}'].round(2).astype(float)

        # add new close from today and save to tsv
        dfold = pd.read_csv(
            './data/eex-power-stock-historical.tsv', sep='\t', index_col=None)
        dfold['Datum'] = pd.to_datetime(dfold['Datum'])
        dfold.set_index('Datum', inplace=True)
        # create new column with current year if it does not exist
        if f'{year}' not in dfold:
            dfold[f'{year}'] = np.nan
        dfold.update(df)  # add new value from df
        dfold.to_csv('./data/eex-power-stock-historical.tsv',
                     sep='\t', index=True)

        # create chart with comparison and drop columns with old years if needed
        dfnew = dfold[[f'{year}', '2022', 'Vorkrisenniveau²']]
        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$', np.nan, regex=True)  # replace empty string with NaN
        dfnew[f'{year}'] = dfnew[f'{year}'].interpolate(
            method='linear', limit_direction='backward')  # for wrong dates

        # get pre-crisis value
        mwh_new = dfnew[f'{year}'].loc[dfnew[f'{year}'].last_valid_index()]
        mwh_new_pos = dfnew[f'{year}'].index.get_loc(
            dfnew[f'{year}'].last_valid_index())
        mwh_old = dfnew.iloc[mwh_new_pos]['Vorkrisenniveau²']
        title_mwh_diff = round((mwh_new - mwh_old), 0).astype(int)
        title_mwh = round(mwh_new, 0).astype(int)
        dfnew[f'{year}'] = dfnew[f'{year}'].fillna('')

        # dynamic chart title
        if title_mwh_diff > 0:
            title = f'Strom kostet am Terminmarkt {title_mwh} Euro je MWh – {title_mwh_diff} Euro mehr als vor der Krise'
        elif title_mwh_diff == 0:
            title = f'Strom kostet am Terminmarkt {title_mwh} Euro je MWh – so viel wie vor der Krise'
        else:
            title = f'Strom kostet am Terminmarkt{title_mwh} Euro je MWh – {abs(title_mwh_diff)} Euro weniger als vor der Krise'

        # create date for chart notes
        timecode = df.index[-1]  # old: df_full
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Preise für die Grundlastlieferung Strom im jeweils nächsten Kalenderjahr («Frontjahr») im deutschen Marktgebiet.<br>² Durchschnitt 2018-2020.<br>Stand: ' + timecode_str

        # run Q function
        update_chart(id='addc121537e4d1aed887b57de0582f99',
                     title=title, notes=notes_chart, data=dfnew)

    except:
        raise
