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
        df_perc = df_perc.rename(
            columns={'Intensiv': 'Nicht mechanisch beatmet'})

        # get percentage for title of percentage chart
        title_perc = df_perc['Beatmet'].iloc[-1].round(0).astype(int)
        title = f'{title_perc} Prozent der Corona-Intensivpatienten werden derzeit beatmet'

        # create index with max value of winter 2020/21
        df_divi_i = df_divi.copy()
        df_divi_i = df_divi_i[(
            df_divi_i.index.get_level_values(0) >= '2020-10-01')]
        df_divi_i['Intensiv'] = round(
            df_divi_i['Intensiv'] * 100 / df_divi_i.iloc[0:150, 0].max(), 2)
        df_divi_i['Beatmet'] = round(
            df_divi_i['Beatmet'] * 100 / df_divi_i.iloc[0:150, 1].max(), 2)
        df_cases = df_cases[(
            df_cases.index.get_level_values(0) >= '2020-10-01')]
        df_cases['Fälle'] = round(
            df_cases['Fälle'] * 100 / df_cases.iloc[0:150, 0].max(), 2)
        df_deaths = df_deaths[(
            df_deaths.index.get_level_values(0) >= '2020-10-01')]
        df_deaths['Tote'] = round(
            df_deaths['Tote'] * 100 / df_deaths.iloc[0:150, 0].max(), 2)

        # merge dataframes and remove DatetimeIndex for Q
        df = pd.concat([df_cases, df_divi_i, df_deaths], axis=1)
        #df.index = df.index.strftime('%Y-%m-%d')

        # create new ICU chart with ventilated and non-ventilated
        df_divi = df_divi.rename(columns={
                                 df_divi.columns[0]: 'Nicht mechanisch beatmet¹', df_divi.columns[1]: 'Beatmet'})
        df_divi = df_divi[['Beatmet', 'Nicht mechanisch beatmet¹']]
        df_divi_missing = pd.DataFrame({
            'Datum': ['2020-03-20', '2020-03-21', '2020-03-22', '2020-03-23', '2020-03-24', '2020-03-25', '2020-03-26', '2020-03-27', '2020-03-28', '2020-03-29', '2020-03-30', '2020-03-31', '2020-04-01', '2020-04-02', '2020-04-03', '2020-04-04', '2020-04-05', '2020-04-06', '2020-04-07', '2020-04-08', '2020-04-09', '2020-04-10', '2020-04-11', '2020-04-12', '2020-04-13', '2020-04-14', '2020-04-15', '2020-04-16', '2020-04-17', '2020-04-18', '2020-04-19', '2020-04-20', '2020-04-21', '2020-04-22', '2020-04-23', '2020-04-24', '2020-04-25', '2020-04-26', '2020-04-27', '2020-04-28', '2020-04-29', '2020-04-30', '2020-05-01', '2020-05-02', '2020-05-03', '2020-05-04', '2020-05-05', '2020-05-06', '2020-05-07', '2020-05-08', '2020-05-09', '2020-05-10', '2020-05-11', '2020-05-12', '2020-05-13', '2020-05-14', '2020-05-15', '2020-05-16', '2020-05-17', '2020-05-18', '2020-05-19', '2020-05-20', '2020-05-21', '2020-05-22', '2020-05-23', '2020-05-24', '2020-05-25', '2020-05-26', '2020-05-27', '2020-05-28', '2020-05-29', '2020-05-30', '2020-05-31', '2020-06-01', '2020-06-02', '2020-06-03', '2020-06-04', '2020-06-05', '2020-06-06', '2020-06-07', '2020-06-08', '2020-06-09', '2020-06-10', '2020-06-11', '2020-06-12', '2020-06-13', '2020-06-14', '2020-06-15', '2020-06-16', '2020-06-17', '2020-06-18', '2020-06-19', '2020-06-20', '2020-06-21', '2020-06-22', '2020-06-23', '2020-06-24', '2020-06-25', '2020-06-26', '2020-06-27', '2020-06-28', '2020-06-29', '2020-06-30', '2020-07-01', '2020-07-02', '2020-07-03'],
            'Nicht mechanisch beatmet¹': [200, 308, 364, 451, 616, 789, 824, 905, 1001, 1063, 1203, 1550, 1784, 2102, 2361, 2471, 2528, 2551, 2641, 2654, 2714, 2702, 2652, 2652, 2719, 2722, 2735, 2810, 2879, 2928, 2870, 2900, 2855, 2739, 2720, 2644, 2538, 2524, 2466, 2391, 2310, 2235, 2118, 2046, 2011, 1976, 1903, 1820, 1763, 1659, 1594, 1603, 1587, 1496, 1384, 1316, 1232, 1173, 1125, 1122, 1087, 1019, 999, 971, 928, 896, 883, 810, 749, 723, 722, 711, 697, 696, 691, 631, 595, 584, 561, 566, 543, 516, 483, 452, 450, 441, 438, 434, 421, 407, 394, 374, 359, 350, 363, 358, 353, 358, 359, 343, 335, 329, 333, 324, 325, 314]
        })
        df_divi_missing.set_index('Datum', inplace=True)
        df_divi_missing.index = pd.to_datetime(df_divi_missing.index)
        df_divi_full = pd.concat(
            [df_divi_missing, df_divi], join='outer', axis=0)
        df_divi_full = df_divi_full.fillna('')
        df_divi_full = df_divi_full[['Beatmet', 'Nicht mechanisch beatmet¹']]

        # get current date for chart notes
        timestamp_str = df.tail(1).index.item()
        #timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d')
        timestamp_str = timestamp_str.strftime('%-d. %-m. %Y')
        notes_chart = 'Fälle und Tote: 7-Tage-Schnitt.<br>Stand: ' + timestamp_str
        notes_chart_perc = '¹ Mechanisch beatmete Patienten müssen aufwendiger betreut werden und haben ein deutlich höheres Risiko zu sterben.<br>Stand: ' + timestamp_str
        notes_chart_abs = '¹ Die Unterteilung zwischen nicht mechanisch beatmet und mechanisch beatmet erfolgte erst ab dem 4. Juli 2020.<br>Stand: ' + timestamp_str

        # run function
        update_chart(id='8eed9f1d79be72ddbd0d9d0fc27267f7',
                     data=df, notes=notes_chart)
        update_chart(id='9b7619cde29731a44bcd04e18f7589a1',
                     data=df_perc, title=title, notes=notes_chart_perc)
        update_chart(id='ab97925bcc5055b33011fb4d3326e163',
                     data=df_divi_full, notes=notes_chart_abs)

    except:
        raise
    finally:
        f.close()
