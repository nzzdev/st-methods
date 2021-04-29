import os
import pandas as pd
import gc
import sys
from datetime import datetime, timedelta, date
from babel.dates import format_date
pd.options.mode.chained_assignment = None

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # set source data
        url = 'https://raw.githubusercontent.com/jgehrcke/covid-19-germany-gae/master/more-data/7di-rki-by-ags.csv'
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', '7di-rki-by-ags.csv'), 'wb') as f:
            f.write(download_data(url).read())

        # read data and transpose
        df = pd.read_csv(
            './data/7di-rki-by-ags.csv', encoding='utf-8', index_col=0).transpose()
        dftable = pd.read_csv(
            './pop_ags.csv', encoding='utf-8', index_col=0)

        # get current date for chart notes
        timestamp_str = df.columns[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%dT%H:%M:%S+%f') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')
        timestamp_str2 = format_date(timestamp_dt, 'd. MMMM', locale='de_DE')

        # clean AGS and add leading zero to numerical AGS values with <5 characters
        df.index = df.index.str.replace('_7di', '')
        df.index = df.index.str.rjust(5, '0')
        df.index = df.index.rename('ID')
        dftable.index = dftable.index.astype(str)
        dftable.index = dftable.index.str.rjust(5, '0')

        # sort by AGS
        df.sort_values(by=['ID'], inplace=True)

        # remove last row with German incidence and Berlin districts
        df = df[:-1]
        df = df.drop(df.index[325:337])
        df.to_csv('out.csv', index=True)
        # add current incidence in df of table chart
        dftable['Inzidenz'] = df.iloc[:, -1]

        # create new df for choropleth map
        dfmap = df[[]].copy()

        # Notbremse on the 22th of April in dfmap?
        # starting from the the 20th of April, comes into effect two days later
        dfmap['Wert'] = 'unter 100'
        dfmap['Wert'][(df.iloc[:, 414] >= 100) & (
            df.iloc[:, 413] >= 100) & (df.iloc[:, 412] >= 100)] = 'über 100'

        # Notbremse on the 22th of April in dftable?
        # starting from the the 20th of April, comes into effect two days later
        dftable['Notbremse'] = '✖'
        dftable['Notbremse'][(df.iloc[:, 414] >= 100) & (
            df.iloc[:, 413] >= 100) & (df.iloc[:, 412] >= 100)] = '✔'

        # When does the Notbremse come into effect? (placeholder)
        # dfmap['Gilt ab'] = 'current day + 2 days'

        # calculate current status of Notbremse since 23th of April
        # update every day (i)
        for i in range(415, df.shape[1]):
            # update every AGS (j)
            for j in range(dfmap.shape[0]):
                if dfmap['Wert'][j] == 'über 100':
                    if (df.iloc[j, i] < 100) & (df.iloc[j, i-1] < 100) & (df.iloc[j, i-2] < 100) & (df.iloc[j, i-3] < 100) & (df.iloc[j, i-4] < 100):
                        dfmap['Wert'][j] = 'unter 100'
                        dftable['Notbremse'][j] = '✖'
                        # dfmap['Gilt ab'][j] = df.columns[i]
                else:
                    if (df.iloc[j, i] >= 100) & (df.iloc[j, i-1] >= 100) & (df.iloc[j, i-2] >= 100):
                        dfmap['Wert'][j] = 'über 100'
                        dftable['Notbremse'][j] = '✔'
                        # dfmap['Gilt ab'][j] = df.columns[i]

        # sort dftable by pop
        dftable.sort_values(
            dftable.columns[1], inplace=True, ascending=False)

        # drop pop and delete old df from memory
        del [[df]]
        del dftable['Bewohner']
        gc.collect()

        # round incidence
        dftable['Inzidenz'] = dftable['Inzidenz'].round(0).astype(int)

        # drop AGS and make region name the row index
        dftable.set_index('Region', inplace=True)

        # number of regions with Notbremse on
        notbremse = (dftable['Notbremse'] == '✔').sum().astype(str)

        # set chart titles and notes
        title_map = notbremse + ' Regionen sind derzeit von der Notbremse betroffen'
        subtitle_table = 'Am ' + timestamp_str2 + ' waren ' + \
            notbremse + ' Kreise und Städte von der Notbremse betroffen'
        notes_chart = 'Die Grafik zeigt, ob gemäss Gesetz die Notbremse (demnächst) gezogen werden muss, nicht ob sie vor Ort bereits in Kraft ist. Den Bundesländern steht es frei, strengere Massnahmen zu verhängen. Gelockert werden darf erst, wenn die 7-Tage-Inzidenz fünf Werktage in Folge unter 100 liegt. Massgeblich für die Notbremse sind die Zahlen vom RKI. Stand: ' + \
            timestamp_str

        # insert id manually and run function
        updateChart(id='530c9a2b291a3ac848e9dc471a762204',
                    data=dfmap, notes=notes_chart, title=title_map)
        updateChart(id='050befd50ccb2f5f9080d4bba4df423d',
                    data=dftable, notes=notes_chart, subtitle=subtitle_table)

    except:
        raise
    finally:
        f.close()
