import os
import pandas as pd
import gspread
import json
from datetime import datetime, timedelta
from time import sleep


def download_sheet(sh, name):  # function for sheet download
    try:
        wsh = sh.worksheet(name)
        return wsh
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 429:
            sleep(5)
            try:
                wsh = sh.worksheet(name)
                return wsh
            except gspread.exceptions.APIError as e:
                print('Script failed twice (blacklisted?):', e)
        elif e.response.status_code > 499:
            sleep(20)
            try:
                wsh = sh.worksheet(name)
                return wsh
            except gspread.exceptions.APIError as e:
                print('Script failed twice (check source):', e)
        else:
            print('Other HTTP error:', e)
    except gspread.exceptions.APIError as e:
        print('Other URL error:', e)


def updateChart(id, title="", subtitle="", notes="", data=pd.DataFrame()):  # Q helper function
    # read qConfig file
    json_file = open('../q.config.json')
    qConfig = json.load(json_file)

    # update chart properties
    for item in qConfig.get('items'):
        for environment in item.get('environments'):
            if environment.get('id') == id:
                if title != '':
                    item.get('item').update({'title': title})
                if subtitle != '':
                    item.get('item').update({'subtitle': subtitle})
                if notes != '':
                    item.get('item').update({'notes': notes})
                if data.size > 0:
                    # reset_index() and T (for transpose) are used to bring column names into the first row
                    transformed_data = data.applymap(str).reset_index(
                        drop=False).T.reset_index().T.apply(list, axis=1).to_list()
                    if 'table' in item.get('item').get('data'):
                        item.get('item').get('data').update(
                            {'table': transformed_data})
                    else:
                        item.get('item').update({'data': transformed_data})
                print('Successfully updated item with id', id,
                      'on', environment.get('name'), 'environment')
    # write qConfig file
    with open('../q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False, indent=1)
    json_file.close()


if __name__ == '__main__':
    try:
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
        wsh = download_sheet(sh, 'Curve')

        # B:B date column
        dt = wsh.get('B:B')
        # F:F new cases 7 day mvg avg, O:O 7-day incidence T:T new deaths 7 day mvg avg, Y:Y ICU patients
        cases = wsh.get('T:T')

        df1 = pd.DataFrame(data=dt)
        df2 = pd.DataFrame(data=cases)
        df = pd.concat([df1, df2], axis=1)

        # drop first (empty) row + column header and reindex with drop=true
        df = df.drop([0, 1]).reset_index(drop=True)

        # create column header names
        cols = list(df.columns)
        cols[0] = ''
        cols[1] = '7-Tage-Schnitt'
        df.columns = cols

        # add year to values in date column
        df.loc[:302, ''] = df.loc[:302, ''].apply(lambda x: x + '2020')
        df.loc[303:, ''] = df.loc[303:, ''].apply(lambda x: x + '2021')

        # change thousands and decimal separator and remove rows with empty values
        df['7-Tage-Schnitt'] = df['7-Tage-Schnitt'].str.replace(
            '.', '', regex=False).str.replace(',', '.', regex=False)
        df.dropna(subset=['7-Tage-Schnitt'], inplace=True)
        # nan_value = float('NaN')
        # df.replace('-', nan_value, inplace=True)

        # convert 'cases' to float, round, then convert to int
        df['7-Tage-Schnitt'] = df['7-Tage-Schnitt'].astype(
            float).round().astype(int)

        # drop last row (last value in F:F and T:T is only temporary)
        df = df.iloc[:-1]

        # set date column as index
        df = df.set_index('')

       # get date for chart notes and add one day
        timestamp_str = df.index[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%d.%m.%Y') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # show date in chart notes
        notes_chart = 'Bei einem tödlichen Verlauf liegen zwischen Beginn der Symptome und Tod im Mittel 18 Tage.<br>Stand: ' + \
            timestamp_str

        # insert id and subtitle manually and run function
        updateChart(id='d6e523e17e1d929e6277292aea28b903',
                    data=df, notes=notes_chart)

    except:
        raise
