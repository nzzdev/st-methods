import requests
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from user_agent import generate_user_agent
from datawrapper import Datawrapper

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *

        # Datawrapper API key
        dw_key = os.environ['DATAWRAPPER_API']
        dw = Datawrapper(access_token=dw_key)
        dw_id = 'QhtLB'

        # generate dates for url
        tday = datetime.today() - timedelta(days=1)
        yday = datetime.today() - timedelta(days=2)
        tdayurl = tday.strftime('%Y/%m/%d')
        tdayurl = tdayurl.replace('/', '%2F')
        ydayurl = yday.strftime('%Y/%m/%d')
        ydayurl = ydayurl.replace('/', '%2F')

        headers = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://www.eex.com/',
            'Origin': 'https://www.eex.com',
            'Host': 'webservice-eex.gvsi.com'
        }

        # attempt to load data for multiple days backward in case of bank holidays or missing data
        df = pd.DataFrame()  # initialize an empty DataFrame
        days_back = 1  # start checking from one day before today
        max_attempts = 5  # maximum number of days to go back

        while df.empty and days_back <= max_attempts:
            # generate URLs for the current attempt day
            tday = datetime.today() - timedelta(days=days_back)
            yday = datetime.today() - timedelta(days=days_back + 1)
            tdayurl = tday.strftime('%Y/%m/%d').replace('/', '%2F')
            ydayurl = yday.strftime('%Y/%m/%d').replace('/', '%2F')
            
            url = f'https://webservice-eex.gvsi.com/query/json/getChain/gv.pricesymbol/gv.displaydate/gv.expirationdate/tradedatetimegmt/gv.eexdeliverystart/ontradeprice/close/onexchsingletradevolume/onexchtradevolumeeex/offexchtradevolumeeex/openinterest/?optionroot=%22%2FE.DEBY%22&expirationdate={ydayurl}&onDate={tdayurl}'
            
            # send request to the API
            r = requests.get(url, headers=headers)
            dictr = r.json()
            recs = dictr.get('results', {}).get('items', [])
            df = pd.json_normalize(recs)
            
            # increment days_back to check the next previous day if df is still empty
            days_back += 1

        # filter columns if data is found
        if not df.empty:
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

        # generate csv for dashboard
        df_dash = dfnew.copy()
        df_dash = df_dash[[f'{year}']]
        df_dash.replace(r'^\s*$', np.nan, regex=True)
        df_dash = df_dash[df_dash[f'{year}'].notna()]
        df_dash = df_dash.rename(
            columns={df_dash.columns[0]: 'Strom-Terminmarkt'})
        df_dash = pd.concat([df_dash.tail(2)])
        df_dash.to_csv('./data/eex-ac-stock-dash.csv')

        # convert Euro / MWh to Cent / kWh
        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$', np.nan, regex=True)
        dfnew = dfnew.divide(10).round(3)

        # get pre-crisis value
        kwh_new = dfnew[f'{year}'].loc[dfnew[f'{year}'].last_valid_index()]
        kwh_new_pos = dfnew[f'{year}'].index.get_loc(
            dfnew[f'{year}'].last_valid_index())
        kwh_old = dfnew.iloc[kwh_new_pos]['Vorkrisenniveau²']
        title_kwh_diff = round((kwh_new - kwh_old), 1)
        title_kwh_diff_perc = round(
            100 * (kwh_new - kwh_old) / kwh_old, 0).astype(int)
        title_kwh = round(kwh_new, 1)

        # replace NaN for Q
        dfnew[f'{year}'] = dfnew[f'{year}'].fillna('')

        # dynamic chart title
        if title_kwh_diff > 0:
            title = f'Strom kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {title_kwh_diff_perc} Prozent mehr als vor der Krise'
        elif title_kwh_diff == 0:
            title = f'Strom kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – so viel wie vor der Krise'
        else:
            title = f'Strom kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {abs(title_kwh_diff_perc)} Prozent weniger als vor der Krise'
        """
        if title_kwh_diff > 0:
            title = f'Strom kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {title_kwh_diff.astype(str).replace(".", ",")} Cent mehr als vor der Krise'
        elif title_kwh_diff == 0:
            title = f'Strom kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – so viel wie vor der Krise'
        else:
            title = f'Strom kostet im Grosshandel {title_kwh.astype(str).replace(".", ",")} Cent – {abs(title_kwh_diff).astype(str).replace(".", ",")} Cent weniger als vor der Krise'
        """

        # create date for chart notes
        timecode = df.index[-1]
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Preise für die Grundlastlieferung Strom im jeweils nächsten Kalenderjahr («Frontjahr») im deutschen Marktgebiet.<br>² Durchschnitt 2018-2020.<br>Stand: ' + timecode_str

        # run Q function
        update_chart(id='addc121537e4d1aed887b57de0582f99',
                     title=title, notes=notes_chart, data=dfnew)

        # Rename column for Datawrapper
        dfnew = dfnew.rename(columns={'Vorkrisenniveau²': 'Vorkrisen-Niveau²'})

        # update Datawrapper chart
        dfnew.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id, data=dfnew)
        dw.update_chart(chart_id=dw_id, title=title)
        date = {'annotate': {'notes': f'{notes_chart}'}}
        dw.update_metadata(chart_id=dw_id, metadata=date)
        dw.publish_chart(chart_id=dw_id, display=False)
        print("debug verivox daily")
    except:
        raise
