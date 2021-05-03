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
                         usecols=['date', 'indikation_pflegeheim_erst', 'indikation_pflegeheim_voll'])

        # extract last row (=today), reset index and delete old df
        df2 = df.iloc[[-1]].reset_index(drop=True)
        del [[df]]
        gc.collect()

        # get date for chart notes and add one day
        timestamp_str = df2.loc[0, 'date']
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # delete date value
        df2.loc[0, 'date'] = ''

        # rename first column and set as index
        df2 = df2.rename(columns={'date': '', 'indikation_pflegeheim_erst': 'erste Dose',
                         'indikation_pflegeheim_voll': 'vollständig geimpft'}).set_index('')

        # show date in chart notes
        notes_chart = 'Laut dem Statistischen Bundesamt (StBA) lebten in Deutschland im Jahr 2019 rund 820 000 Menschen in Pflege- und Altersheimen. In die Statistik zu «geimpften Pflegeheimbewohnern» des RKI fliessen allerdings inzwischen auch Zahlen von geimpften Menschen ein, die gemäss der Definition des StBA keine Pflegeheimbewohner sind.<br>Stand: ' + \
            timestamp_str

        # insert id and subtitle manually and run function
        update_chart(id='b4b5354dc92073edbdccdff477de959a',
                     data=df2, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
