import os
import pandas as pd
from datetime import datetime, timedelta
import sys


if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # set source data
        url = 'https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland/master/Aktuell_Deutschland_Impfquoten_COVID-19.csv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'Aktuell_Deutschland_Impfquoten_COVID-19.csv'), 'wb') as f:
            f.write(download_data(url).read())

        # read data
        csv = './data/Aktuell_Deutschland_Impfquoten_COVID-19.csv'
        dfall = pd.read_csv(csv, encoding='utf-8',
                            usecols=['Datum', 'Impfquote_gesamt_min1', 'Impfquote_gesamt_gi', 'Impfquote_gesamt_boost1', 'Impfquote_gesamt_boost2'])
        df5 = pd.read_csv(
            csv, encoding='utf-8', usecols=['Datum', 'Impfquote_05bis11_min1', 'Impfquote_05bis11_gi'])
        df12 = pd.read_csv(
            csv, encoding='utf-8', usecols=['Datum', 'Impfquote_12bis17_min1', 'Impfquote_12bis17_gi', 'Impfquote_12bis17_boost1', 'Impfquote_12bis17_boost2'])
        df18 = pd.read_csv(
            csv, encoding='utf-8', usecols=['Datum', 'Impfquote_18plus_min1', 'Impfquote_18plus_gi', 'Impfquote_18plus_boost1', 'Impfquote_18plus_boost2'])
        df60 = pd.read_csv(
            csv, encoding='utf-8', usecols=['Datum', 'Impfquote_60plus_min1', 'Impfquote_60plus_gi', 'Impfquote_60plus_boost1', 'Impfquote_60plus_boost2'])

        # extract first rows (=Germany)
        dfall = dfall.iloc[[0]].reset_index(drop=True)
        df5 = df5.iloc[[0]].reset_index(drop=True)
        df12 = df12.iloc[[0]].reset_index(drop=True)
        df18 = df18.iloc[[0]].reset_index(drop=True)
        df60 = df60.iloc[[0]].reset_index(drop=True)

        # get date for chart notes and add one day
        timestamp_str = dfall.loc[0, 'Datum']
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # rename headers
        dfall.loc[0, 'Datum'] = 'Alle'
        df5.loc[0, 'Datum'] = '5-11'
        df12.loc[0, 'Datum'] = '12-17'
        df18.loc[0, 'Datum'] = '18+'
        df60.loc[0, 'Datum'] = '60+'

        # add emtpy row as a chart spacer
        dfall.loc[dfall.shape[0]] = [None, None, None, None, None]

        # rename columns
        dfall = dfall.rename(columns={'Datum': '', 'Impfquote_gesamt_min1': '1. Dose',
                                      'Impfquote_gesamt_gi': '2. Dose', 'Impfquote_gesamt_boost1': '3. Dose', 'Impfquote_gesamt_boost2': '4. Dose'})
        df5 = df5.rename(columns={
            'Datum': '', 'Impfquote_05bis11_min1': '1. Dose', 'Impfquote_05bis11_gi': '2. Dose'})
        df12 = df12.rename(columns={
            'Datum': '', 'Impfquote_12bis17_min1': '1. Dose', 'Impfquote_12bis17_gi': '2. Dose', 'Impfquote_12bis17_boost1': '3. Dose', 'Impfquote_12bis17_boost2': '4. Dose'})
        df18 = df18.rename(columns={
            'Datum': '', 'Impfquote_18plus_min1': '1. Dose', 'Impfquote_18plus_gi': '2. Dose', 'Impfquote_18plus_boost1': '3. Dose', 'Impfquote_18plus_boost2': '4. Dose'})
        df60 = df60.rename(columns={
            'Datum': '', 'Impfquote_60plus_min1': '1. Dose', 'Impfquote_60plus_gi': '2. Dose', 'Impfquote_60plus_boost1': '3. Dose', 'Impfquote_60plus_boost2': '4. Dose'})

        # combine datasets, replace nan in column with no boosters
        df = pd.concat([dfall, df60, df18, df12, df5],
                       ignore_index=True)
        df.loc[5, '3. Dose'] = 0
        df.loc[5, '4. Dose'] = 0

        # do calculations for stacked bar chart
        df['1. Dose'] = (df['1. Dose'] -
                         df['2. Dose']).round(1)
        df['2. Dose'] = (
            df['2. Dose'] - df['3. Dose']).round(1)
        df['3. Dose'] = (df['3. Dose'] - df['4. Dose']).round(1)

        # create new column "Ziel" and calculate gap between status quo and herd immunity
        df.loc[0, 'Ziel'] = (80 - (df.loc[0, '2. Dose'] + df.loc[0, '1. Dose'] +
                             df.loc[0, '3. Dose'] + df.loc[0, '4. Dose'])).round(1)

        # rearrange columns
        df = df[['', '4. Dose', '3. Dose', '2. Dose',
                 '1. Dose', 'Ziel']].set_index('')

        # show percentage total (copy to chart title later)
        title_percent = df.iat[0, 0] + \
            df.iat[0, 1] + df.iat[0, 2] + df.iat[0, 3]
        title_percent_full = df.iat[0, 0] + df.iat[0, 1] + df.iat[0, 2]
        title_percent_boost1 = df.iat[0, 1]
        title_percent_boost2 = df.iat[0, 0] + df.iat[0, 1]
        # title_chart = str(title_percent.round(1)).replace('.', ',') + ' Prozent sind geimpft, ' + str(title_percent_full.round(1)).replace('.', ',') + ' Prozent doppelt'
        title_chart = str(title_percent_full.round(1)).replace('.', ',') + ' Prozent sind doppelt geimpft, ' + \
            str(title_percent_boost2.round(1)).replace(
                '.', ',') + ' Prozent mit Booster-Schutz'

        # replace NaN with empty string
        df.fillna('', inplace=True)

        # show date in chart notes
        notes_chart = 'Ziel: Impfquote von 80%.<br>Stand: ' + \
            timestamp_str

        # run function
        update_chart(id='e8f976e14bac8280d4b908f99eeb409a',
                     data=df, title=title_chart, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
