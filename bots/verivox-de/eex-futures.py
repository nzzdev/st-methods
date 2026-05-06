import requests
import time
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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


        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'de,en-US;q=0.9,en;q=0.8,en-GB;q=0.7',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Origin': 'https://www.eex.com',
            'Referer': 'https://www.eex.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36'
        }
        session = requests.Session()
        retry = Retry(
            total=2,
            connect=2,
            read=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=['GET']
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        session.headers.update(headers)


        # attempt to load the latest front-year German power base future
        df = pd.DataFrame()  # initialize an empty DataFrame
        api_url = 'https://api.eex-group.com/pub/market-data/table-data'
        today = datetime.today()
        last_trading_lookup_date = today - timedelta(days=1)
        maturity = f'{today.year + 1}01'
        params = {
            'shortCode': 'DEBY',
            'commodity': 'POWER',
            'pricing': 'F',
            'area': 'DE',
            'product': 'Base',
            'maturity': maturity,
            'startDate': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'endDate': last_trading_lookup_date.strftime('%Y-%m-%d'),
            'maturityType': 'Year',
            'isRolling': 'true'
        }

        try:
            r = session.get(api_url, params=params, timeout=20)
            r.raise_for_status()
            dictr = r.json()
            header = dictr.get('header', [])
            data = dictr.get('data', [])
            df = pd.DataFrame(data, columns=header)

            if not df.empty:
                missing_cols = {'tradeDate', 'settlPx'} - set(df.columns)
                if missing_cols:
                    print(f'EEX response is missing expected columns: {missing_cols}. Using existing historical data.')
                    df = pd.DataFrame()
                else:
                    df = df.rename(columns={'tradeDate': 'tradedatetimegmt', 'settlPx': 'close'})
                    df['tradedatetimegmt'] = pd.to_datetime(df['tradedatetimegmt'], errors='coerce')
                    df['close'] = pd.to_numeric(df['close'], errors='coerce')
                    df = df[df['tradedatetimegmt'].notna() & df['close'].notna()]
                    if not df.empty:
                        df = df.sort_values('tradedatetimegmt', ascending=False)
        except RequestException as e:
            print(f'EEX request failed: {e}')
        except ValueError as e:
            print(f'EEX returned non-JSON response: {e}')
        
        # load historical data first so the script can continue if EEX returns nothing
        dfold = pd.read_csv(
            './data/eex-power-stock-historical.tsv', sep='\t', index_col=None)
        dfold['Datum'] = pd.to_datetime(dfold['Datum'])
        dfold.set_index('Datum', inplace=True)

        # filter columns if data is found; otherwise keep existing historical data unchanged
        if df.empty:
            print('No EEX data received after all attempts. Using existing historical data.')
            year = str(datetime.today().year)
            if year not in dfold.columns:
                year = str(max(int(col) for col in dfold.columns if str(col).isdigit()))
        else:
            df = df.filter(['close', 'tradedatetimegmt'])
            missing_cols = {'close', 'tradedatetimegmt'} - set(df.columns)
            if missing_cols:
                print(f'EEX response is missing expected columns: {missing_cols}. Using existing historical data.')
                df = pd.DataFrame()
                year = str(datetime.today().year)
                if year not in dfold.columns:
                    year = str(max(int(col) for col in dfold.columns if str(col).isdigit()))
            else:
                # convert to datetimeindex
                df['tradedatetimegmt'] = pd.to_datetime(df['tradedatetimegmt'])
                year = df['tradedatetimegmt'].dt.strftime(
                    '%Y').iloc[0]  # get year for column
                df = df.rename(
                    columns={'tradedatetimegmt': 'Datum', 'close': f'{year}'})
                df['Datum'] = df['Datum'].dt.strftime('%Y-%m-%d')
                df['Datum'] = pd.to_datetime(df['Datum'])
                df.set_index('Datum', inplace=True)
                df[f'{year}'] = df[f'{year}'].round(2).astype(float)

                # create new column with current year if it does not exist
                if f'{year}' not in dfold:
                    dfold[f'{year}'] = np.nan
                dfold.update(df)  # add new value from df
                dfold.to_csv('./data/eex-power-stock-historical.tsv',
                             sep='\t', index=True)

        # create chart with comparison and drop columns with old years if needed
        dfnew = dfold[[f'{year}', '2022', 'Vorkrisenniveau²']].copy()
        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$', np.nan, regex=True)  # replace empty string with NaN
        dfnew[f'{year}'] = dfnew[f'{year}'].interpolate(
            method='linear', limit_direction='backward')  # for wrong dates

        # generate csv for dashboard
        # Time series must start at 2025-01-01.
        # Use column "2025" for 2025 and column "2026" for 2026.
        # Drop non-trading days / holidays (rows without data).

        df_dash_src = dfold.copy()
        for _col in ['2025', '2026']:
            if _col not in df_dash_src.columns:
                df_dash_src[_col] = np.nan

        def _anchor_year(_s: pd.Series, _year: int) -> pd.Series:
            _s = pd.to_numeric(_s, errors='coerce')
            _md = _s.index.strftime('%m-%d')
            # 2025/2026 are not leap years; guard against 02-29 in templates
            _md = pd.Series(_md, index=_s.index).where(_md != '02-29', '02-28')
            _s.index = pd.to_datetime(_md.map(lambda d: f"{_year}-{d}"))
            _s = _s.sort_index()
            return _s[~_s.index.duplicated(keep='last')]

        s2025 = _anchor_year(df_dash_src['2025'], 2025)
        s2026 = _anchor_year(df_dash_src['2026'], 2026)

        df_dash = pd.concat([s2025, s2026]).to_frame(name='Strom-Terminmarkt')
        df_dash = df_dash.sort_index()
        df_dash = df_dash[df_dash.index >= pd.Timestamp('2025-01-01')]

        # Drop non-trading days / holidays
        df_dash = df_dash[df_dash['Strom-Terminmarkt'].notna()]

        df_dash.to_csv('./data/eex-ac-stock-dash_full.csv')
        df_dash.tail(2).to_csv('./data/eex-ac-stock-dash.csv')

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

        # create date for chart notes from the latest available historical value
        timecode = pd.to_numeric(dfold[f'{year}'], errors='coerce').last_valid_index()
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Preise für die Grundlastlieferung Strom im jeweils nächsten Kalenderjahr («Frontjahr») im deutschen Marktgebiet.<br>² Durchschnitt 2018-2020.<br>Stand: ' + timecode_str

        # run Q function
        update_chart(id='addc121537e4d1aed887b57de0582f99', title=title, notes=notes_chart, data=dfnew)

        # Rename column for Datawrapper
        dfnew = dfnew.rename(columns={'Vorkrisenniveau²': 'Vorkrisen-Niveau²'})

        # update Datawrapper chart
        dfnew.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id, data=dfnew)
        dw.update_chart(chart_id=dw_id, title=title)
        date = {'annotate': {'notes': f'{notes_chart}'}}
        dw.update_metadata(chart_id=dw_id, metadata=date)
        dw.publish_chart(chart_id=dw_id, display=False)
    except:
        raise
