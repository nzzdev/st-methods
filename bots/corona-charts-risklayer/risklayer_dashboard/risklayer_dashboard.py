import os
import pandas as pd
import gspread
import sys
import json
from datetime import datetime, timedelta
from time import sleep


if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # create dict with Google API keys instead of using JSON file
        google_secrets = {
            'type': 'service_account',
            'project_id': 'nzz-risklayer-sheet',
            'private_key_id': os.environ['GSPREAD_PRIVATE_KEY_ID'],
            'private_key': os.environ['GSPREAD_PRIVATE_KEY'].replace('\\n', '\n'),
            'client_email': 'view-risklayer-sheet@nzz-risklayer-sheet.iam.gserviceaccount.com',
            'client_id': '117834230046379590580',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/view-risklayer-sheet%40nzz-risklayer-sheet.iam.gserviceaccount.com'
        }

        # authenticate with dict
        gc = gspread.service_account_from_dict(google_secrets)

        # key from risklayer spreadsheet
        sh = gc.open_by_key('1wg-s4_Lz2Stil6spQEYFdZaBEp8nWW26gVyfHqvcl8s')

        # open spreadsheet and merge dataframes
        wsh = download_sheet(sh, 'Curve')
        # B:B date column
        dt = get_sheet(wsh, 'B:B')
        df1 = pd.DataFrame(data=dt)
        # Z:Z ICU patients
        icu = get_sheet(wsh, 'Z:Z')
        df2 = pd.DataFrame(data=icu)
        # F:F new cases 7 day mvg avg
        cases = get_sheet(wsh, 'F:F')
        df3 = pd.DataFrame(data=cases)
        # S:S new deaths 7 day mvg avg
        deaths = get_sheet(wsh, 'T:T')
        df4 = pd.DataFrame(data=deaths)
        df = pd.concat([df1, df2, df3, df4], axis=1)

        # AA:AA ICU patients trend
        trend_icu = get_sheet(wsh, 'AA:AA')
        df2 = pd.DataFrame(data=trend_icu)
        # G:G new cases trend
        trend_cases = get_sheet(wsh, 'G:G')
        df3 = pd.DataFrame(data=trend_cases)
        # U:U new deaths trend
        trend_deaths = get_sheet(wsh, 'U:U')
        df4 = pd.DataFrame(data=trend_deaths)
        # AC:AC new ICU patients
        new_patients = get_sheet(wsh, 'AC:AC')
        df5 = pd.DataFrame(data=new_patients)
        # E:E new cases
        new_cases = get_sheet(wsh, 'E:E')
        df6 = pd.DataFrame(data=new_cases)
        # S:S new deaths
        new_deaths = get_sheet(wsh, 'S:S')
        df7 = pd.DataFrame(data=new_deaths)
        df_meta = pd.concat([df1, df2, df3, df4, df5, df6, df7], axis=1)

        # drop some rows + column header and reindex
        df = df.drop(df.index[0:212]).reset_index(drop=True)
        df_meta = df_meta.drop(df_meta.index[0:688]).reset_index(drop=True)

        # create column header names
        cols = list(df.columns)
        cols[0] = 'date'
        cols[1] = 'Intensivpatienten'
        cols[2] = 'Neuinfektionen'
        cols[3] = 'Neue Todesfälle'
        df.columns = cols

        cols = list(df_meta.columns)
        cols[0] = 'date'
        cols[1] = 'Trend ICU'
        cols[2] = 'Trend Fälle'
        cols[3] = 'Trend Tote'
        cols[4] = 'Neu ICU'
        cols[5] = 'Neu Fälle'
        cols[6] = 'Neu Tote'
        df_meta.columns = cols

        # clean numeric values and remove rows with empty values
        df['Intensivpatienten'] = df['Intensivpatienten'].str.replace(
            '.', '', regex=False)
        df['Neuinfektionen'] = df['Neuinfektionen'].str.replace(
            '.', '', regex=False).str.replace(',', '.', regex=False)
        df['Neue Todesfälle'] = df['Neue Todesfälle'].str.replace(
            '.', '', regex=False).str.replace(',', '.', regex=False)
        df_meta['Trend ICU'] = df_meta['Trend ICU'].str.replace(
            ',', '.', regex=False).str.replace('%', '', regex=False)
        df_meta['Trend Fälle'] = df_meta['Trend Fälle'].str.replace(
            ',', '.', regex=False).str.replace('%', '', regex=False)
        df_meta['Trend Tote'] = df_meta['Trend Tote'].str.replace(
            ',', '.', regex=False).str.replace('%', '', regex=False)
        df_meta['Neu ICU'] = df_meta['Neu ICU'].str.replace(
            '.', '', regex=False)
        df_meta['Neu Fälle'] = df_meta['Neu Fälle'].str.replace(
            '.', '', regex=False)
        df_meta['Neu Tote'] = df_meta['Neu Tote'].str.replace(
            '.', '', regex=False)
        df.dropna(subset=['Neuinfektionen'], inplace=True)
        df.dropna(subset=['Neue Todesfälle'], inplace=True)
        # df.dropna(subset=['Intensivpatienten'], inplace=True)
        # df_meta.dropna(subset=['Trend ICU'], inplace=True)
        df_meta.dropna(subset=['Trend Fälle'], inplace=True)
        df_meta.dropna(subset=['Trend Tote'], inplace=True)
        # df_meta.dropna(subset=['Neu ICU'], inplace=True)
        df_meta.dropna(subset=['Neu Fälle'], inplace=True)
        df_meta.dropna(subset=['Neu Tote'], inplace=True)

        # convert numeric strings to int/float
        df['Intensivpatienten'] = df['Intensivpatienten'].astype(float)  # nan
        df['Neuinfektionen'] = df['Neuinfektionen'].astype(
            float).round().astype(int)
        df['Neue Todesfälle'] = df['Neue Todesfälle'].astype(
            float).round().astype(int)
        df_meta['Trend ICU'] = df_meta['Trend ICU'].astype(float)  # nan
        df_meta['Trend Fälle'] = df_meta['Trend Fälle'].astype(float)
        df_meta['Trend Tote'] = df_meta['Trend Tote'].astype(float)
        df_meta['Neu ICU'] = df_meta['Neu ICU'].astype(float)  # nan
        df_meta['Neu Fälle'] = df_meta['Neu Fälle'].astype(int)
        df_meta['Neu Tote'] = df_meta['Neu Tote'].astype(int)

        # check if last row in ICU column is not nan, then shift cases and deaths
        if pd.notna(df['Intensivpatienten'].iloc[-1]) == True:
            df = df.append(pd.DataFrame(df[-1:].values, columns=df.columns))
            df_meta = df_meta.append(pd.DataFrame(
                df_meta[-1:].values, columns=df_meta.columns))
            df['Neuinfektionen'] = df['Neuinfektionen'].shift(1)
            df['Neue Todesfälle'] = df['Neue Todesfälle'].shift(1)
            df_meta['Trend Fälle'] = df_meta['Trend Fälle'].shift(1)
            df_meta['Trend Tote'] = df_meta['Trend Tote'].shift(1)
            df_meta['Neu Fälle'] = df_meta['Neu Fälle'].shift(1)
            df_meta['Neu Tote'] = df_meta['Neu Tote'].shift(1)

        # drop rows (last row with cases and deaths is temporary)
        df = df.iloc[1:-1].reset_index(drop=True)
        df_meta = df_meta.iloc[1:-1].reset_index(drop=True)
        df['Intensivpatienten'] = df['Intensivpatienten'].astype(int)

        # replace percentages with strings
        cols = ('Trend ICU', 'Trend Fälle', 'Trend Tote')

        def replace_vals(df_meta):
            for col in cols:
                if df_meta[col] >= 5:
                    df_meta[col] = 'steigend'
                elif df_meta[col] <= -5:
                    df_meta[col] = 'fallend'
                else:
                    df_meta[col] = 'gleichbleibend'
            return df_meta
        df_meta = df_meta.apply(replace_vals, axis=1)

        # get last values of df_meta as objects
        df_meta = df_meta.iloc[-1]
        trend_icu = df_meta['Trend ICU']
        trend_cases = df_meta['Trend Fälle']
        trend_deaths = df_meta['Trend Tote']
        diff_icu = df_meta['Neu ICU']
        diff_cases = df_meta['Neu Fälle']
        diff_deaths = df_meta['Neu Tote']

        # convert dates to ISO standard with European-style date parsing
        df['date'] = pd.to_datetime(
            df['date'], dayfirst=True).dt.strftime('%Y-%m-%d')

        # get date for chart notes and add one day
        timestamp_str = df['date'].iloc[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        # timestamp_str_notes = timestamp_dt.strftime('%-d. %-m. %Y')

        # create dictionaries for JSON file
        dict_icu = df.drop(['Neuinfektionen', 'Neue Todesfälle'], axis=1).rename(
            columns={'Intensivpatienten': 'value'}).to_dict(orient='records')
        dict_cases = df.drop(['Intensivpatienten', 'Neue Todesfälle'], axis=1).rename(
            columns={'Neuinfektionen': 'value'}).to_dict(orient='records')
        dict_deaths = df.drop(['Intensivpatienten', 'Neuinfektionen'], axis=1).rename(
            columns={'Neue Todesfälle': 'value'}).to_dict(orient='records')

        # additional data for JSON file
        trend_icu = 'fallend'
        trend_cases = 'steigend'
        trend_deaths = 'fallend'
        meta_icu = {'indicatorTitle': 'Intensivpatienten', 'date': timestamp_str,
                    'value': int(diff_icu), 'color': '#24b39c', 'trend': trend_icu, 'chartType': 'area'}
        meta_cases = {'indicatorTitle': 'Neuinfektionen', 'date': timestamp_str, 'indicatorSubtitle': '7-Tage-Schnitt',
                      'value': int(diff_cases), 'color': '#e66e4a', 'trend': trend_cases, 'chartType': 'area'}
        meta_deaths = {'indicatorTitle': 'Neue Todesfälle', 'date': timestamp_str, 'indicatorSubtitle': '7-Tage-Schnitt',
                       'value': int(diff_deaths), 'color': '#05032d', 'trend': trend_deaths, 'chartType': 'area'}

        # merge dictionaries
        meta_icu['chartData'] = dict_icu
        meta_cases['chartData'] = dict_cases
        meta_deaths['chartData'] = dict_deaths
        dicts = []
        dicts.append(meta_icu)
        dicts.append(meta_cases)
        dicts.append(meta_deaths)

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open('./data/dashboard_de.json', 'w') as fp:
            json.dump(dicts, fp, ensure_ascii=True, indent=4)
        file = [{
            "loadSyncBeforeInit": "true",
            "file": {
                "path": "./risklayer_dashboard/data/dashboard_de.json"
            }
        }]

        # run function
        update_chart(id='499935fb791197fd126bda721f15884a', files=file)

    except:
        raise
