import os
import io
import numpy as np
import pandas as pd
from user_agent import generate_user_agent
import gc

if __name__ == '__main__':
    try:
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        # locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        """
        ##########
        # NORMAL #
        ##########
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
                       df.columns[0]: 'Datum', df.columns[2]: '', df.columns[3]: '3-Jahres-Mittel'})
        df = df[['Datum', '', '3-Jahres-Mittel', '2022']]

        # add new column with goal
        df = df.assign(goal=['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '1238.45', '1219.75', '1249.5', '1299.65', '1339.6',
                       '1381.25', '1429.7', '1513', '1671.1', '1940.55', '2045.95', '2161.55', '2233.8', '2533.85', '2674.1', '2901.9', '3235.95', '3334.55', '3428.05', '3468.85', '3195.15', '2899.35'])
        df = df.rename(columns={'goal': 'EU-Ziel²'})

        # convert date column to index
        df = df.set_index('Datum')

        # create timestamp for chart notes
        df.iloc[:, 2] = df.iloc[:, 2].replace('', np.nan)
        timestamp = df.iloc[:, 2].notna()[::-1].idxmax()
        timestamp_notes = timestamp + pd.DateOffset(days=1)
        timestamp_notes_str = timestamp_notes.strftime('%-d. %-m. %Y')
        chart_notes = f'¹ Maximum/Minimum des Verbrauchs 2018-2021.<br>² Gemäss Gas-Notfallplan der EU sollen alle Länder ihren Verbrauch von Anfang August 2022 bis März 2023 um 15 Prozent senken, verglichen mit dem Durchschnittsverbrauch der vergangenen fünf Jahre in diesem Zeitraum.<br><br>Stand: {timestamp_notes_str}'

        # create dynamic chart title
        currenty = df.iloc[:, 2].loc[~df.iloc[:, 2].isnull()].iloc[-1]
        eugoaly = df.iloc[:, 3].loc[timestamp]
        diffy = (float(currenty) - float(eugoaly))
        if diffy < 2 and diffy > -2:
            chart_title = 'Deutschland erfüllt derzeit das Gas-Sparziel der EU'
        elif diffy >= 2:
            chart_title = 'Deutschland verfehlt derzeit das Gas-Sparziel der EU'
        else:
            chart_title = 'Deutschland spart derzeit mehr Gas als von der EU gefordert'
        df.iloc[:, 2] = df.iloc[:, 2].replace(np.nan, '')

        # run Q function
        update_chart(id='df32c18d6ba570e13338190d2936f17d',
                     data=df, title=chart_title, notes=chart_notes)

        # cleanup
        del [[df]]
        gc.collect()
        """

        #############
        # BEREINIGT #
        #############

        # download data
        url = 'https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1090950'
        resp = download_data(url, headers=fheaders)
        csv_file = resp.text

        # read csv, drop last column with weather and convert to str
        df = pd.read_csv(io.StringIO(csv_file), encoding='utf-8',
                         sep=';', decimal=',', index_col=None)
        df = df.drop(df.columns[[2, 3]], axis=1)

        # rename and reorder columns
        df = df.rename(columns={
                       df.columns[0]: 'Datum', df.columns[1]: 'Ziel²', df.columns[2]: 'Normaler Verbrauch¹', df.columns[3]: '2022'})
        df = df[['Datum', 'Normaler Verbrauch¹', '2022', 'Ziel²']]

        # convert date column to index
        df = df.set_index('Datum')
        df.index = pd.to_datetime(df.index)

        # convert to float
        cols = df.columns
        # cols.remove('Datum')
        for col in cols:
            df[col] = df[col].astype(float)

        # convert total imports to terrawatts
        df = df.div(1000)

        # create timestamp for chart notes
        timestamp = df.index[-1]
        timestamp_notes = timestamp  # + pd.DateOffset(days=1)
        timestamp_notes_str = timestamp_notes.strftime('%-d. %-m. %Y')
        chart_notes = f'¹ Mittelwert 2018-2021, temperaturbereinigt.<br>² Ziel ist eine temperaturbereinigte Einsparung von mehr als 25 Prozent Gas.<br>Stand: {timestamp_notes_str}'

        # create dynamic chart title
        # OLD
        """
        diff = (df['2022'].iloc[-1] / df['Normaler Verbrauch¹'].iloc[-1])-1
        if diff < -0.25:
            chart_title = 'Deutschland erfüllt derzeit sein Sparziel'
        elif diff >= -0.25 and diff <= -0.15:
            chart_title = 'Deutschland verfehlt sein Sparziel derzeit knapp'
        else:
            chart_title = 'Deutschland verfehlt sein Sparziel derzeit deutlich'
        """
        diff = (df['2022'].iloc[-1] / df['Normaler Verbrauch¹'].iloc[-1])-1
        diff_nice = abs((diff*100).round(0).astype(int))
        if diff < 0:
            chart_title = f'Deutschland verbraucht derzeit {diff_nice} Prozent weniger Gas als üblich'
        elif diff > 0:
            chart_title = f'Deutschland verbraucht derzeit {diff_nice} Prozent mehr Gas als üblich'
        else:
            chart_title = 'Deutschland verbraucht derzeit so viel Gas wie üblich'

        # write to CSV for dashboard
        df.to_csv('./data/gasverbrauch.csv', encoding='utf-8', index=True)

        # run Q function
        update_chart(id='48eb730db09047043a6a34a319789817',
                     data=df, title=chart_title, notes=chart_notes)

    except:
        raise
