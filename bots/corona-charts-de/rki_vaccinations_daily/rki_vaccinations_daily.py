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
        url = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v3.tsv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'germany_vaccinations_timeseries_v2.tsv'), 'wb') as f:
            f.write(download_data(url).read())

        # read relevant columns
        df = pd.read_csv('./data/germany_vaccinations_timeseries_v2.tsv', delimiter='\t', encoding='utf-8',
                         usecols=['date', 'impfungen_min1', 'impfungen_gi', 'impfungen_boost1', 'impfungen_boost2'])

        # rearrange columns
        # df2 = df2[['date', 'impf_quote_voll', 'impf_quote_erst', 'Ziel']]

        # only show last year
        # df = df.tail(365)

        # get 7-day average of vaccinations for chart title and notes
        mean_first = df.tail(
            7)['impfungen_min1'].mean()
        mean_full = df.tail(
            7)['impfungen_gi'].mean()
        mean_third = df.tail(
            7)['impfungen_boost1'].mean()
        mean_fourth = df.tail(
            7)['impfungen_boost2'].mean()
        mean = mean_first + mean_full + mean_third + mean_fourth
        mean_booster = mean_third + mean_fourth
        # round, use thousand seperator and convert to str
        mean = f'{mean.round(-3).astype(int):,}'.replace(',', ' ')
        mean_booster = f'{mean_booster.round(-3).astype(int):,}'.replace(
            ',', ' ')
        mean_first = f'{mean_first.round(-3).astype(int):,}'.replace(',', '')
        mean_full = f'{mean_full.round(-3).astype(int):,}'.replace(',', '')
        mean_third = f'{mean_third.round(-3).astype(int):,}'.replace(',', '')
        mean_fourth = f'{mean_fourth.round(-3).astype(int):,}'.replace(',', '')

        # get date for chart notes and add one day
        timestamp_str = df['date'].iloc[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # rename first column and set as index
        df = df.rename(columns={'date': '', 'impfungen_min1': '1. Dose',
                       'impfungen_gi': '2. Dose', 'impfungen_boost1': '3. Dose', 'impfungen_boost2': '4. Dose'}).set_index('')

        # add row with no values and current date as index for step-after chart
        df.loc[df.shape[0]] = ['', '', '', '']
        df.rename({df.index[-1]: timestamp_dt}, inplace=True)

        # change date format
        df.index = pd.to_datetime(
            df.index, format='%Y-%m-%d').strftime('%d.%m.%Y')

       # show date in chart notes
        notes_chart = '¹ Sieben-Tage-Schnitt, gerundet (1. Dose: ' + mean_first + ', 2. Dose: ' + mean_full + ', Booster: ' + mean_booster + \
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
