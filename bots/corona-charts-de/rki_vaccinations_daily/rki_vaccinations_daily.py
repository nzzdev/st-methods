import os
import pandas as pd
import gc
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
        url = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'germany_vaccinations_timeseries_v2.tsv'), 'wb') as f:
            f.write(download_data(url).read())

        # read relevant columns
        df = pd.read_csv('./data/germany_vaccinations_timeseries_v2.tsv', delimiter='\t', encoding='utf-8',
                         usecols=['date', 'dosen_erst_differenz_zum_vortag', 'dosen_zweit_differenz_zum_vortag', 'dosen_dritt_differenz_zum_vortag'])

        # rearrange columns
        # df2 = df2[['date', 'impf_quote_voll', 'impf_quote_erst', 'Ziel']]

        # only show last year
        df = df.tail(365)

        # get 7-day average of vaccinations for chart title and notes
        mean_first = df.tail(
            7)['dosen_erst_differenz_zum_vortag'].mean()
        mean_full = df.tail(
            7)['dosen_zweit_differenz_zum_vortag'].mean()
        mean_third = df.tail(
            7)['dosen_dritt_differenz_zum_vortag'].mean()
        mean = mean_first + mean_full + mean_third
        # round, use thousand seperator and convert to str
        mean = f'{mean.round(-3).astype(int):,}'.replace(',', ' ')
        mean_first = f'{mean_first.round(-3).astype(int):,}'.replace(',', '')
        mean_full = f'{mean_full.round(-3).astype(int):,}'.replace(',', '')
        mean_third = f'{mean_third.round(-3).astype(int):,}'.replace(',', '')

        # get date for chart notes and add one day
        timestamp_str = df['date'].iloc[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # rename first column and set as index
        df = df.rename(columns={'date': '', 'dosen_erst_differenz_zum_vortag': 'Erstimpfung',
                       'dosen_zweit_differenz_zum_vortag': 'Zweitimpfung', 'dosen_dritt_differenz_zum_vortag': 'Auffrischung'}).set_index('')

        # add row with no values and current date as index for step-after chart
        df.loc[df.shape[0]] = ['', '', '']
        df.rename({df.index[-1]: timestamp_dt}, inplace=True)

        # change date format
        df.index = pd.to_datetime(
            df.index, format='%Y-%m-%d').strftime('%d.%m.%Y')

       # show date in chart notes
        notes_chart = '¹ Sieben-Tage-Schnitt (Erstimpfung: ' + mean_first + ', Zweitimpfung: ' + mean_full + ', Auffrischung: ' + mean_third + \
            ').<br>Stand: ' + timestamp_str

        # show 7-day average in chart title
        title_chart = 'Deutschland verimpft derzeit im Schnitt ' + mean + ' Dosen¹ pro Tag'

        # insert id and subtitle manually and run function
        update_chart(id='dd4b1de66b3907bb65164669b0d3353f',
                     data=df, title=title_chart, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
