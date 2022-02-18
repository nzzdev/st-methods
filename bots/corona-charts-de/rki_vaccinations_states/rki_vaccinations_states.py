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
        url = 'https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland/master/Aktuell_Deutschland_Impfquoten_COVID-19.csv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'Aktuell_Deutschland_Impfquoten_COVID-19.csv'), 'wb') as f:
            f.write(download_data(url).read())

        # read data
        csv = './data/Aktuell_Deutschland_Impfquoten_COVID-19.csv'
        df = pd.read_csv(csv, encoding='utf-8',
                         usecols=['Datum', 'Bundesland', 'Impfquote_gesamt_voll', 'Impfquote_gesamt_boost'])

        # get date for chart notes and drop date column
        timestamp_str = df.loc[0, 'Datum']
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')
        df = df.drop(['Datum'], axis=1)

        # extract Germany, drop first and last row
        dfde = df.iloc[[0]].reset_index(drop=True)
        df = df.drop(df.index[[-1, 0]])

        # sorty by fully vaccinated
        df = df.sort_values(by='Impfquote_gesamt_voll', ascending=False)

        # add Germany at the top
        df = pd.concat([pd.DataFrame(dfde), df], ignore_index=True)

        # rename column headers
        df = df.rename(columns={'Bundesland': 'Land', 'Impfquote_gesamt_voll': '2. Dose',
                       'Impfquote_gesamt_boost': '3. Dose'}).set_index('Land')

        # show date in chart notes
        notes_chart = 'Stand: ' + timestamp_str

        # run function
        update_chart(id='245e5a30acb9ffa8e53b336e6bda032b',
                     data=df, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
