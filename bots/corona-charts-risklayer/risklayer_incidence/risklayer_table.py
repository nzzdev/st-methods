from time import sleep
from datetime import datetime
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
        wsh = download_sheet(sh, 'nzz')

        # name column
        cells = get_sheet(wsh, 'E:E')
        name = cells

        # Bundesland column
        cells = get_sheet(wsh, 'H:H')
        state = cells

        # deaths column
        # cells = get_sheet(wsh, 'J:J')
        # deaths = cells

        # trend column
        cells = get_sheet(wsh, 'N:N')
        trend = cells

        # new cases 7 day mvg avg
        cells = get_sheet(wsh, 'B:B')
        cases = cells

        df1 = pd.DataFrame(data=name)
        df2 = pd.DataFrame(data=state)
        df3 = pd.DataFrame(data=trend)
        df4 = pd.DataFrame(data=cases)
        df = pd.concat([df1, df2, df3, df4], axis=1)

        # drop column header and reindex with drop=true
        df = df.drop([0]).reset_index(drop=True)

        # create column header names
        cols = list(df.columns)
        cols[0] = 'Region'
        cols[1] = 'Land'
        cols[2] = 'Trend'
        cols[3] = 'Inzidenz'
        df.columns = cols

        # convert case column to int and sort by case numbers
        df['Inzidenz'] = pd.to_numeric(df['Inzidenz'], errors='ignore')
        df = df.sort_values(by=['Inzidenz'], ascending=False)

        # set AGS column as index
        df = df.set_index('Region')

       # get date for chart notes
        timestamp_dt = datetime.today()
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # show date in chart notes
        notes_chart = 'Risklayer bezieht seine Zahlen direkt aus den Veröffentlichungen der Gesundheitsämter der Kreise und Städte. Wegen des veralteten Meldesystems sind diese Daten aktueller als jene vom RKI.<br>Stand: ' + timestamp_str

        # insert id and subtitle manually and run function
        update_chart(id='549b5522072c32f00946aa2ea073bfbd',
                     data=df, notes=notes_chart)
    except:
        raise
