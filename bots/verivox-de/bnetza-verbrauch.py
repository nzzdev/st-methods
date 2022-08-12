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
        url = 'https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/Versorgungssicherheit/aktuelle_gasversorgung/_svg/download.csv?nn=1059464&svgid=1067070&view=renderCSV'
        resp = download_data(url, headers=fheaders)
        csv_file = resp.text

        # read csv, drop last column with weather and convert to str
        df = pd.read_csv(io.StringIO(csv_file), encoding='utf-8',
                         sep=';', decimal=',', index_col=0)
        df = df.iloc[:, :-1]
        df.iloc[:, 0] = df.iloc[:, 0].astype(
            str).str.replace('0.0', '', regex=False)

        # convert month strings to datetime
        df.index = df.index + ' 2022'
        df.index = df.index.str.replace('Mrz', 'Mar').str.replace(
            'Mai', 'May').str.replace('Okt', 'Oct').str.replace('Dez', 'Dec', regex=False)
        df.index = pd.to_datetime(df.index, errors='coerce')

        # add new column with goal
        df = df.assign(goal=['', '', '', '', '', '', '34.34',
                       '32.98', '38.505', '62.22', '93.245', '106.76'])
        df = df.rename(columns={'goal': 'EU-Ziel¹'})

        # create timestamp for chart notes
        df.iloc[:, 0] = df.iloc[:, 0].replace('', np.nan)
        timestamp = df.iloc[:, 0].notna()[::-1].idxmax()
        timestamp_str = timestamp.strftime("%B %Y")
        chart_notes = f'Gemäss Gas-Notfallplan der EU sollen alle Länder ihren Verbrauch bis März 2023 um 15 Prozent senken.<br><br>Stand: {timestamp_str}'

        # create dynamic chart title
        currenty = df.iloc[:, 0].loc[~df.iloc[:, 0].isnull()].iloc[-1]
        lasty = df.iloc[:, 1].loc[timestamp]
        diffy = (float(currenty) - float(lasty))
        if diffy < 2 and diffy > -2:
            chart_title = 'Gasverbrauch wieder auf Vorjahresniveau'
        elif diffy >= 2:
            chart_title = 'Deutschland verbraucht mehr Gas als im Vorjahr'
        else:
            chart_title = 'Deutschland verbraucht weniger Gas als im Vorjahr'
        df.iloc[:, 0] = df.iloc[:, 0].replace(np.nan, '')

        # run Q function
        update_chart(id='df32c18d6ba570e13338190d2936f17d',
                     data=df, title=chart_title, notes=chart_notes)

    except:
        raise
