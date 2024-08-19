import os
import io
import pandas as pd
from user_agent import generate_user_agent

if __name__ == '__main__':
    try:
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # download data
        url = 'https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081194'
        # url = 'https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=591578'  # new
        resp = download_data(url, headers=fheaders)
        csv_file = resp.text

        # read csv, drop columns
        df = pd.read_csv(io.StringIO(csv_file), encoding='utf-8',
                         sep=';', decimal=',', index_col=None)
        df = df.drop(df.columns[[1, 2, 3, 4, 5, 6, 7, 8]], axis=1)

        # convert date string to datetime
        df[df.columns[0]] = pd.to_datetime(df[df.columns[0]], format='%d.%m.%Y')
        # old date format
        #df[df.columns[0]] = pd.to_datetime(df[df.columns[0]], format='%d.%m.%Y')

        # set date as index
        df = df.set_index(df.columns[0])

        # get latest date for chart notes
        timecode = df.index[-1]
        timecodestr = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Die Exporte beinhalten sämtliche Gasflüsse von Deutschland in angrenzende Staaten, unabhängig davon, wo das Gas bestellt wurde.<br>Stand: ' + timecodestr

        # calculate 7-day mvg average
        #df = df.rolling(window=7).mean().dropna()

        # convert total exports to terrawatts
        df = df.div(1000)

        # dynamic chart title
        title_twh = df[df.columns[0]].iloc[-1].round(1).astype(float)
        title_twh = title_twh.astype(str).replace('.', ',')
        title = f'Deutschland exportiert derzeit {title_twh} TWh Gas am Tag'

        # run Q function
        update_chart(id='332e931d1de8fc64f1b04d2612c7d75e',
                     data=df, title=title, notes=notes_chart)

    except:
        raise
