import os
import pandas as pd
import gspread
import sys
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

        # open spreadsheet with patients and merge dataframes
        wsh = download_sheet(sh, 'DIVI')
        # B:B date column
        dt = get_sheet(wsh, 'B:B')
        df1 = pd.DataFrame(data=dt)
        # D:D all patients
        patients = get_sheet(wsh, 'D:D')
        df2 = pd.DataFrame(data=patients)
        # E:E ventialted patients
        ventilated = get_sheet(wsh, 'E:E')
        df3 = pd.DataFrame(data=ventilated)
        df = pd.concat([df1, df2, df3], axis=1)

        # open spreadsheet with cases and merge dataframes
        wsh = download_sheet(sh, 'Curve')
        # B:B date column
        dt = get_sheet(wsh, 'B:B')
        df4 = pd.DataFrame(data=dt)
        # F:F new cases 7 day mvg avg
        cases = get_sheet(wsh, 'F:F')
        df5 = pd.DataFrame(data=cases)
        # S:S new deaths 7 day mvg avg
        deaths = get_sheet(wsh, 'T:T')
        df6 = pd.DataFrame(data=deaths)
        df_cases = pd.concat([df4, df5, df6], axis=1)

        # drop empty rows + column header (i.e. start at 1.9.2021) and reindex with drop=true
        df = df.drop(df.index[0:186]).reset_index(drop=True)
        df_cases = df_cases.drop(df_cases.index[0:213]).reset_index(drop=True)

        # create column header names
        cols = list(df.columns)
        cols[0] = ''
        cols[1] = 'Intensiv'
        cols[2] = 'Beatmet'
        df.columns = cols
        cols = list(df_cases.columns)
        cols[0] = ''
        cols[1] = 'Fälle'
        cols[2] = 'Tote'
        df_cases.columns = cols

        # add year to values in date column
        df.loc[:91, ''] = df.loc[:91, ''].apply(lambda x: x + '.2020')
        df.loc[92:456, ''] = df.loc[92:456, ''].apply(lambda x: x + '.2021')
        df.loc[457:, ''] = df.loc[457:, ''].apply(lambda x: x + '.2022')

        # clean some messy dates
        df[''] = df[''].str.replace('2020.2020', '2020', regex=False)

        # clean numeric values and remove rows with empty values
        df['Intensiv'] = df['Intensiv'].str.replace(
            '.0', '', regex=False).str.replace(',', '', regex=False)
        df['Beatmet'] = df['Beatmet'].str.replace(
            '.0', '', regex=False).str.replace(',', '', regex=False)
        df.dropna(subset=['Intensiv'], inplace=True)
        df_cases['Fälle'] = df_cases['Fälle'].str.replace(
            '.', '', regex=False).str.replace(',', '.', regex=False)
        df_cases['Tote'] = df_cases['Tote'].str.replace(
            '.', '', regex=False).str.replace(',', '.', regex=False)
        df_cases.dropna(subset=['Fälle'], inplace=True)
        df_cases.dropna(subset=['Tote'], inplace=True)

        # extrapolate missing values on christmas eve
        df['Beatmet'] = pd.to_numeric(df['Beatmet'], errors='coerce')
        df['Beatmet'] = df['Beatmet'].interpolate(
            method='slinear', fill_value='extrapolate', limit_direction='backward')

        # convert numeric strings to int/float
        df['Intensiv'] = df['Intensiv'].astype(float)  # nan
        df['Beatmet'] = df['Beatmet'].astype(float)  # nan
        df_cases['Fälle'] = df_cases['Fälle'].astype(float).round().astype(int)
        df_cases['Tote'] = df_cases['Tote'].astype(float).round().astype(int)

        # create Index with max value of winter 2020/21
        df['Intensiv'] = round(
            df['Intensiv'] * 100 / df.loc[0:150, 'Intensiv'].max(), 2)
        df['Beatmet'] = round(df['Beatmet'] * 100 /
                              df.loc[0:150, 'Beatmet'].max(), 2)
        df_cases['Fälle'] = round(
            df_cases['Fälle'] * 100 / df_cases.loc[0:150, 'Fälle'].max(), 2)
        df_cases['Tote'] = round(
            df_cases['Tote'] * 100 / df_cases.loc[0:150, 'Tote'].max(), 2)

        # drop last temporary row
        df_cases = df_cases.iloc[:-1]

        # set date column as index
        df = df.set_index('')
        df_cases = df_cases.set_index('')

        # fix dates with missing zeros
        df.index = pd.to_datetime(
            df.index, format='%d.%m.%Y').strftime('%d.%m.%Y')

        # merge dataframes
        # df = df.iloc[:-1]
        # dataframe with no NaN values (same date)
        df_no_nan = df.join(df_cases)
        # dataframe with NaN values (different dates)
        df_nan = pd.concat([df, df_cases], axis=1)

        # change column order
        df_nan = df_nan[['Fälle', 'Intensiv', 'Beatmet', 'Tote']]
        df_no_nan = df_no_nan[[
            'Fälle', 'Intensiv', 'Beatmet', 'Tote']]

       # get date for chart notes
        timestamp_str = df.index[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%d.%m.%Y')
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # show date in chart notes
        notes_chart = 'Fälle und Tote: 7-Tage-Schnitt.<br>Stand: ' + \
            timestamp_str

        # insert id and subtitle manually and run function
        update_chart(id='16461281a4d978edd55e4bc123570944',
                     data=df_nan, notes=notes_chart)

    except:
        raise
