from time import sleep
from datetime import datetime, timedelta
import gspread
import pandas as pd
import os
import sys


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

        # open spreadsheet and select worksheet
        wsh = download_sheet(sh, 'DIVI')

        # B:B date column
        dt = wsh.get('B:B')
        # D:D all patients
        patients = wsh.get('D:D')

        df1 = pd.DataFrame(data=dt)
        df2 = pd.DataFrame(data=patients)
        df = pd.concat([df1, df2], axis=1)

        # drop empty rows + column header (i.e. start at 10.04.2020) and reindex with drop=true
        df = df.drop([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
                     ).reset_index(drop=True)

        # create column header names
        cols = list(df.columns)
        cols[0] = ''
        cols[1] = 'Patienten'
        df.columns = cols

        # add year to values in date column
        df.loc[:265, ''] = df.loc[:265, ''].apply(lambda x: x + '.2020')
        df.loc[266:, ''] = df.loc[266:, ''].apply(lambda x: x + '.2021')
        # clean some messy dates
        df[''] = df[''].str.replace('2020.2020', '2020', regex=False)

        # clean numeric values and remove rows with empty values
        df['Patienten'] = df['Patienten'].str.replace(
            '.0', '', regex=False).str.replace(',', '', regex=False)
        df.dropna(subset=['Patienten'], inplace=True)
        # nan_value = float('NaN')
        # df.replace('-', nan_value, inplace=True)

        # convert numeric strings to int
        df['Patienten'] = df['Patienten'].astype(int)

        # set date column as index
        df = df.set_index('')

        # fix dates with missing zeros
        df.index = pd.to_datetime(
            df.index, format='%d.%m.%Y').strftime('%d.%m.%Y')

       # get date for chart notes and add one day
        timestamp_str = df.index[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%d.%m.%Y') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # show date in chart notes
        notes_chart = 'Rund die Hälfte der im Jahr 2020 mechanisch beatmeten Covid-19-Intensivpatienten ist gestorben. Bei nicht mechanisch beatmeten lag die Mortalitätsrate zwischen 10 und 38 Prozent.<br>Stand: ' + \
            timestamp_str

        # insert id manually and run function
        update_chart(id='245e5a30acb9ffa8e53b336e6b83c7bc',
                     data=df, notes=notes_chart)
        sleep(5)

    except:
        raise
