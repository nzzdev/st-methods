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
                         usecols=['date', 'dosen_erst_differenz_zum_vortag', 'dosen_zweit_differenz_zum_vortag'])

        # rearrange columns
        # df2 = df2[['date', 'impf_quote_voll', 'impf_quote_erst', 'Ziel']]

        # only show last six months
        df = df.tail(180)

        # get 7-day average of total vaccinations for chart title
        mean = df.tail(
            7)['dosen_differenz_zum_vortag'].mean().round(-3).astype(int)
        # use thousand seperator and convert to str
        mean = f'{mean:,}'.replace(',', ' ')
        # drop column from df
        df.drop('dosen_differenz_zum_vortag', axis=1, inplace=True)

        # get date for chart notes and add one day
        timestamp_str = df['date'].iloc[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # rename first column and set as index
        df = df.rename(columns={'date': '', 'dosen_erst_differenz_zum_vortag': 'erste Dose',
                       'dosen_zweit_differenz_zum_vortag': 'vollständig geimpft'}).set_index('')

        # change date format
        df.index = pd.to_datetime(
            df.index, format='%Y-%m-%d').strftime('%d.%m.%Y')

       # show date in chart notes
        notes_chart = '¹ Sieben-Tage-Schnitt. Der Impfstoff von J&J, von dem nur eine Dose nötig ist, ist sowohl in den Erst- als auch in den Zweitimpfungen enthalten.<br>Stand: ' + \
            timestamp_str

        # show 7-day average in chart title
        title_chart = 'Deutschland verimpft derzeit ' + mean + ' Dosen¹ täglich'

        # insert id and subtitle manually and run function
        update_chart(id='dd4b1de66b3907bb65164669b0d3353f',
                     data=df, title=title_chart, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
