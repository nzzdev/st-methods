import os
import pandas as pd
import sys
import subprocess
from datetime import datetime

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # call Node.js script and save output as csv
        # subprocess.call(['npm' 'i' 'dataunwrapper'])
        dw_divi = subprocess.Popen(
            ['node', 'dataunwrapper.js', 'HCAPG'], stdout=subprocess.PIPE)
        output = dw_divi.stdout.read()
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'node_divi.csv'), 'wb') as f:
            f.write(output)

        # read csv
        df_cases = pd.read_csv('./data/faelle7d.csv',
                               encoding='utf-8', index_col=0)
        df_divi = pd.read_csv('./data/node_divi.csv',
                              encoding='utf-8', index_col=0)
        df_deaths = pd.read_csv(
            './data/tote7d.csv', encoding='utf-8', index_col=0)

        # 7-day mvg average new cases
        df_cases.index = pd.to_datetime(df_cases.index)

        # ICU patients and ventilated
        df_divi = df_divi.drop(df_divi.columns[[0, 1, 4]], axis=1)
        df_divi = df_divi.rename(
            columns={df_divi.columns[0]: 'Intensiv', df_divi.columns[1]: 'Beatmet'})
        df_divi.index.rename('Datum', inplace=True)
        df_divi.index = pd.to_datetime(df_divi.index)
        # add missing dates and fill in missing values
        df_divi = df_divi.asfreq('d')
        df_divi['Intensiv'] = df_divi['Intensiv'].interpolate(
            method='linear', limit_direction='backward', limit_area='inside')
        df_divi['Beatmet'] = df_divi['Beatmet'].interpolate(
            method='linear', limit_direction='backward', limit_area='inside')
        df_divi.astype(int).to_csv('./data/intensiv.csv',
                                   encoding='utf-8', index=True)

        # 7-day mvg average deaths
        df_deaths.index = pd.to_datetime(df_deaths.index)

        # create chart with percentages of ventilated and non-ventilated
        df_perc = df_divi.copy()
        df_perc = df_perc[(df_perc.index.get_level_values(0) >= '2021-01-01')]
        df_perc['Summe'] = df_perc['Beatmet'] + df_perc['Intensiv']
        df_perc['Beatmet'] = (df_perc['Beatmet'] / df_perc['Summe']) * 100
        df_perc['Intensiv'] = (df_perc['Intensiv'] / df_perc['Summe']) * 100
        df_perc = df_perc[['Beatmet', 'Intensiv']]
        df_perc = df_perc.rename(columns={'Intensiv': 'Nicht beatmet'})

        # get percentage for title of percentage chart
        title_perc = df_perc['Beatmet'].iloc[-1].round(0).astype(int)
        title = f'{title_perc} Prozent der Corona-Intensivpatienten werden derzeit beatmet'

        # create index with max value of winter 2020/21
        df_divi = df_divi[(df_divi.index.get_level_values(0) >= '2020-10-01')]
        df_divi['Intensiv'] = round(
            df_divi['Intensiv'] * 100 / df_divi.iloc[0:150, 0].max(), 2)
        df_divi['Beatmet'] = round(
            df_divi['Beatmet'] * 100 / df_divi.iloc[0:150, 1].max(), 2)
        df_cases = df_cases[(
            df_cases.index.get_level_values(0) >= '2020-10-01')]
        df_cases['Fälle'] = round(
            df_cases['Fälle'] * 100 / df_cases.iloc[0:150, 0].max(), 2)
        df_deaths = df_deaths[(
            df_deaths.index.get_level_values(0) >= '2020-10-01')]
        df_deaths['Tote'] = round(
            df_deaths['Tote'] * 100 / df_deaths.iloc[0:150, 0].max(), 2)

        # merge dataframes and remove DatetimeIndex for Q
        df = pd.concat([df_cases, df_divi, df_deaths], axis=1)
        #df.index = df.index.strftime('%Y-%m-%d')

        # get current date for chart notes
        timestamp_str = df.tail(1).index.item()
        #timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d')
        timestamp_str = timestamp_str.strftime('%-d. %-m. %Y')
        notes_chart = 'Fälle und Tote: 7-Tage-Schnitt.<br>Stand: ' + timestamp_str
        notes_chart_perc = '¹ Mechanisch beatmete Patienten müssen aufwendiger betreut werden.<br>Stand: ' + timestamp_str

        # run function
        update_chart(id='8eed9f1d79be72ddbd0d9d0fc27267f7',
                     data=df, notes=notes_chart)
        update_chart(id='9b7619cde29731a44bcd04e18f7589a1',
                     data=df_perc, title=title, notes=notes_chart_perc)

    except:
        raise
    finally:
        f.close()
