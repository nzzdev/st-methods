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

        # open spreadsheet and select worksheet with function in helpers.py
        wsh = download_sheet(sh, 'Curve')

        # B:B date column
        cells = get_sheet(wsh, 'B:B')
        dt = cells
        # F:F new cases 7 day mvg avg, O:O 7-day incidence, T:T new deaths 7 day mvg avg, Y:Y ICU patients
        cells = get_sheet(wsh, 'O:O')
        cases = cells

        df1 = pd.DataFrame(data=dt)
        df2 = pd.DataFrame(data=cases)
        df = pd.concat([df1, df2], axis=1)

        # drop first (empty) row + column header and reindex with drop=true
        df = df.drop([0, 1]).reset_index(drop=True)

        # create column header names
        cols = list(df.columns)
        cols[0] = ''
        cols[1] = '7-Tage-Inzidenz'
        df.columns = cols

        # add year to values in date column
        # df.loc[:302, ''] = df.loc[:302, ''].apply(lambda x: x + '2020')
        # df.loc[303:, ''] = df.loc[303:, ''].apply(lambda x: x + '2021')

        # add full year to values in date column
        # df.loc[:302, ''] = df.loc[:302, ''].apply(lambda x: str(x).replace('.20', '.2020'))
        # df.loc[303:, ''] = df.loc[303:, ''].apply(lambda x: str(x).replace('.21', '.2021'))

        # change thousands and decimal separator and remove rows with empty values
        df['7-Tage-Inzidenz'] = df['7-Tage-Inzidenz'].str.replace(
            '.', '', regex=False).str.replace(',', '.', regex=False)
        df.dropna(subset=['7-Tage-Inzidenz'], inplace=True)
        # nan_value = float('NaN')
        # df.replace('-', nan_value, inplace=True)

        # convert 'cases' to float, round, then convert to int
        df['7-Tage-Inzidenz'] = df['7-Tage-Inzidenz'].astype(
            float).round().astype(int)

        # drop last row (last value in F:F and S:S is only temporary)
        df = df.iloc[:-1]

        # set date column as index
        df = df.set_index('')

       # get date for chart notes and add one day
        timestamp_str = df.index[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%d.%m.%Y') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # show date in chart notes
        notes_chart = 'Risklayer bezieht seine Zahlen direkt aus den Veröffentlichungen der Gesundheitsämter der Kreise und Städte. Wegen des veralteten Meldesystems sind diese Daten aktueller als jene vom RKI.<br>Stand: ' + \
            timestamp_str

        # insert id and subtitle manually and run function
        update_chart(id='beb6de8405dcbea50a354dc453822c18',
                     data=df, notes=notes_chart)
    except:
        raise
