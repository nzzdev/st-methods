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

        # read columns need for the chart
        csv = './data/Aktuell_Deutschland_Impfquoten_COVID-19.csv'
        dfall = pd.read_csv(csv, encoding='utf-8',
                            usecols=['Datum', 'Impfquote_gesamt_min1', 'Impfquote_gesamt_voll'])
        df12 = pd.read_csv(
            csv, encoding='utf-8', usecols=['Datum', 'Impfquote_12bis17_min1', 'Impfquote_12bis17_voll'])
        df18 = pd.read_csv(
            csv, encoding='utf-8', usecols=['Datum', 'Impfquote_18plus_min1', 'Impfquote_18plus_voll'])
        df60 = pd.read_csv(
            csv, encoding='utf-8', usecols=['Datum', 'Impfquote_60plus_min1', 'Impfquote_60plus_voll'])

        # extract first rows (=Germany)
        dfall = dfall.iloc[[0]].reset_index(drop=True)
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
        df12.loc[0, 'Datum'] = '12-17'
        df18.loc[0, 'Datum'] = '18+'
        df60.loc[0, 'Datum'] = '60+'

        # add emtpy row as a chart spacer
        dfall.loc[dfall.shape[0]] = [None, None, None]

        # rename columns
        dfall = dfall.rename(columns={'Datum': '', 'Impfquote_gesamt_min1': 'erste Dose',
                                      'Impfquote_gesamt_voll': 'vollständig geimpft'})
        df12 = df12.rename(columns={
            'Datum': '', 'Impfquote_12bis17_min1': 'erste Dose', 'Impfquote_12bis17_voll': 'vollständig geimpft'})
        df18 = df18.rename(columns={
            'Datum': '', 'Impfquote_18plus_min1': 'erste Dose', 'Impfquote_18plus_voll': 'vollständig geimpft'})
        df60 = df60.rename(columns={
            'Datum': '', 'Impfquote_60plus_min1': 'erste Dose', 'Impfquote_60plus_voll': 'vollständig geimpft'})

        # combine datasets
        df = pd.concat([dfall, df60, df18, df12],
                       ignore_index=True)

        # do calculations for stacked bar chart
        df['erste Dose'] = (
            df['erste Dose'] - df['vollständig geimpft']).round(1)
        df['vollständig geimpft'] = df['vollständig geimpft'].round(1)

        # create new column "Ziel" and calculate gap between status quo and herd immunity
        df.loc[0, 'Ziel'] = (80 - (df.loc[0, 'vollständig geimpft'] +
                                   df.loc[0, 'erste Dose'])).round(1)

        # rearrange columns
        df = df[['', 'vollständig geimpft',
                 'erste Dose', 'Ziel']].set_index('')

        # show percentage total (copy to chart title later)
        title_percent = df.iat[0, 0]+df.iat[0, 1]
        title_percent_full = df.iat[0, 0]
        title_chart = str(title_percent.round(1)).replace('.', ',') + \
            ' Prozent sind geimpft, ' + \
            str(title_percent_full.round(1)).replace('.', ',') + \
            ' Prozent vollständig'

        # replace NaN with empty string
        df.fillna('', inplace=True)

        # show date in chart notes
        notes_chart = 'Impfquote von 80% in Grau. Der Impfstoff von J&J, von dem nur eine Dose nötig ist, ist sowohl in den Erst- als auch in den Zweitimpfungen enthalten. <br>Stand: ' + \
            timestamp_str

        # run function
        update_chart(id='e8f976e14bac8280d4b908f99eeb409a',
                     data=df, title=title_chart, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
