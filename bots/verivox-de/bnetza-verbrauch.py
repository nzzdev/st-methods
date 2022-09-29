import os
import io
import locale
import numpy as np
import pandas as pd
from user_agent import generate_user_agent

if __name__ == '__main__':
    try:
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # download data
        url = 'https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081208'
        resp = download_data(url, headers=fheaders)
        csv_file = resp.text

        # read csv, drop last column with weather and convert to str
        df = pd.read_csv(io.StringIO(csv_file), encoding='utf-8',
                         sep=';', decimal=',', index_col=None)
        df = df.drop(df.columns[[2, 3]], axis=1)

        # convert week number to datetime (and fix first and last week)
        df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.zfill(2)
        df.iloc[:, 0] = df.iloc[:, 0] + '-2022'
        df.iloc[:, 0] = pd.to_datetime(
            '0-' + df.iloc[:, 0], format='%w-%U-%Y') + pd.DateOffset(days=7)
        df.iloc[-1, 0] = df.iloc[-1, 0] - pd.DateOffset(days=1)
        df.iloc[0, 0] = df.iloc[0, 0] - pd.DateOffset(days=8)
        # df['.'] = '2022-W' + df['.']

        # rename and reorder columns
        df = df.rename(columns={
                       df.columns[0]: 'Datum', df.columns[2]: '', df.columns[3]: 'Höchst-/Tiefststand¹'})
        df = df[['Datum', '', 'Höchst-/Tiefststand¹', '2022']]

        # add new column with goal
        df = df.assign(goal=['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '1334.5', '1283.5', '1239.3', '1163.65', '1213.8', '1165.35', '1232.5',
                       '1335.35', '1374.45', '1301.35', '1399.95', '1539.35', '1566.55', '1912.5', '2257.6', '2211.7', '2277.15', '2606.1', '2977.55', '2893.4', '3407.65', '3488.4', '3664.35', '3146.7', '3611.65', '2710.65'])
        df = df.rename(columns={'goal': 'EU-Ziel²'})

        # convert date column to index
        df = df.set_index('Datum')

        # create timestamp for chart notes
        df.iloc[:, 2] = df.iloc[:, 2].replace('', np.nan)
        timestamp = df.iloc[:, 2].notna()[::-1].idxmax()
        timestamp_notes = timestamp + pd.DateOffset(days=1)
        timestamp_notes_str = timestamp.strftime('%-d. %-m. %Y')
        chart_notes = f'¹ Maximum/Minimum des Verbrauchs 2018-2021.<br>² Gemäss Gas-Notfallplan der EU sollen alle Länder ihren Verbrauch bis März 2023 um 15 Prozent gegenüber 2021 senken.<br><br>Stand: {timestamp_notes_str}'

        # create dynamic chart title
        currenty = df.iloc[:, 2].loc[~df.iloc[:, 2].isnull()].iloc[-1]
        eugoaly = df.iloc[:, 3].loc[timestamp]
        diffy = (float(currenty) - float(eugoaly))
        if diffy < 2 and diffy > -2:
            chart_title = 'Gasverbrauch im Soll'
        elif diffy >= 2:
            chart_title = 'Gasverbrauch über dem Soll'
        else:
            chart_title = 'Gasverbrauch unter dem Soll'
        df.iloc[:, 2] = df.iloc[:, 2].replace(np.nan, '')

        # run Q function
        update_chart(id='df32c18d6ba570e13338190d2936f17d',
                     data=df, title=chart_title, notes=chart_notes)

    except:
        raise
