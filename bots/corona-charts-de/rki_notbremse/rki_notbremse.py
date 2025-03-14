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
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')
        timestamp_str2 = format_date(timestamp_dt, 'd. MMMM', locale='de_DE')

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

        # create new df for choropleth map
        dfmap = df[[]].copy()
        dfedumap = df[[]].copy()

        # Notbremse on the 22th of April in dfmap?
        # starting from the the 20th of April, comes into effect two days later
        dfmap['Wert'] = 'keine Notbremse'
        dfmap['Wert'][(df.iloc[:, 414] > 100) & (
            df.iloc[:, 413] > 100) & (df.iloc[:, 412] > 100)] = 'Notbremse'

        # Notbremse for schools on the 22th of April in dfedumap?
        # starting from the the 20th of April, comes into effect two days later
        dfedumap['Wert'] = 'Schulen offen'
        dfedumap['Wert'][(df.iloc[:, 414] > 165) & (
            df.iloc[:, 413] > 165) & (df.iloc[:, 412] > 165)] = 'Schulen geschlossen'

        # Notbremse on the 22th of April in dftable?
        # starting from the the 20th of April, comes into effect two days later
        dftable['Notbremse'] = '‍	‍	‍	‍	✖‍	‍	‍	‍	'  # with ‍	‍	‍	‍	blank
        dftable['Notbremse'][(df.iloc[:, 414] > 100) & (
            df.iloc[:, 413] > 100) & (df.iloc[:, 412] > 100)] = '‍	‍	‍	‍	✔‍	‍	‍	‍	'  # with ‍	‍	‍	‍	blank

        # When does the Notbremse come into effect? (placeholder)
        # dfmap['Gilt ab'] = 'current day + 2 days'

        # calculate current status of Notbremse since 23th of April
        # update every day (i)
        for i in range(415, df.shape[1]):
            # update every AGS (j)
            for j in range(dfmap.shape[0]):
                if dfmap['Wert'][j] == 'Notbremse':
                    if (df.iloc[j, i] < 100) & (df.iloc[j, i-1] < 100) & (df.iloc[j, i-2] < 100) & (df.iloc[j, i-3] < 100) & (df.iloc[j, i-4] < 100):
                        dfmap['Wert'][j] = 'keine Notbremse'
                        dftable['Notbremse'][j] = '‍	‍	‍	‍	✖‍	‍	‍	‍	'
                        # dfmap['Gilt ab'][j] = df.columns[i]
                if dfedumap['Wert'][j] == 'Schulen geschlossen':
                    if (df.iloc[j, i] < 165) & (df.iloc[j, i-1] < 165) & (df.iloc[j, i-2] < 165) & (df.iloc[j, i-3] < 165) & (df.iloc[j, i-4] < 165):
                        dfedumap['Wert'][j] = 'Schulen offen'
                        # dfmap['Gilt ab'][j] = df.columns[i]
                else:
                    if (df.iloc[j, i] > 100) & (df.iloc[j, i-1] > 100) & (df.iloc[j, i-2] > 100):
                        dfmap['Wert'][j] = 'Notbremse'
                        dftable['Notbremse'][j] = '‍	‍	‍	‍	✔‍	‍	‍	‍	'
                        # dfmap['Gilt ab'][j] = df.columns[i]
                    if (df.iloc[j, i] > 165) & (df.iloc[j, i-1] > 165) & (df.iloc[j, i-2] > 165):
                        dfedumap['Wert'][j] = 'Schulen geschlossen'
                        # dfmap['Gilt ab'][j] = df.columns[i]

        # add current incidence in df of table chart
        dftable['Inzidenz_tmp'] = df.iloc[:, -1]

        # calculate trend and add to new Inzidenz column
        dftable['Trend'] = (
            ((df.iloc[:, -1] - df.iloc[:, -3]) / df.iloc[:, -3]) * 100)
        dftable['Trend_arrow'] = ''
        dftable['Trend_arrow'][(dftable['Trend'] < -5)] = ' ↓'
        dftable['Trend_arrow'][(dftable['Trend'] > 5)] = ' ↑'
        dftable['Inzidenz_tmp'] = dftable['Inzidenz_tmp'].round(
            0).astype(int).clip(lower=0)  # trim negative numbers

        dftable['Inzidenz'] = dftable['Inzidenz_tmp'].astype(
            str) + dftable['Trend_arrow']

        # sort dftable by pop
        dftable.sort_values(
            dftable.columns[1], inplace=True, ascending=False)

        # drop some columns and delete old df from memory
        del [[df]]
        del dftable['Trend']
        del dftable['Trend_arrow']
        del dftable['Inzidenz_tmp']
        del dftable['Bewohner']
        gc.collect()

        # drop AGS and make region name the row index
        dftable.set_index('Region', inplace=True)

        # change order of columns
        dftable = dftable[['Inzidenz', 'Notbremse']]

        # number of regions with Notbremse on
        notbremse = (dfmap['Wert'] == 'Notbremse').sum()
        # calculate difference between 24th of April and now
        notbremse_diff = 367 - notbremse
        notbremse_diff = notbremse_diff.astype(str)
        notbremse = (dfmap['Wert'] == 'Notbremse').sum().astype(str)

        # number of regions with schools closed
        schools = (dfedumap['Wert'] == 'Schulen geschlossen').sum().astype(str)

        # set chart titles and notes
        # title_map = notbremse + ' Regionen sind derzeit von der Notbremse betroffen'
        subtitle_chart = 'Am ' + timestamp_str2 + ' lagen ' + \
            notbremse + ' Kreise und Städte 3 Tage in Folge über dem Inzidenzwert von 100 und noch keine 5 Tage in Folge darunter - das sind ' + \
            notbremse_diff + ' weniger als noch Ende April'
        subtitle_chart2 = 'Am ' + timestamp_str2 + ' lagen ' + \
            schools + ' Kreise und Städte 3 Tage in Folge über dem Inzidenzwert von 165 und noch keine 5 Tage in Folge darunter'
        notes_chart = 'Die Grafik zeigt, ob die Notbremse gemäss RKI-Inzidenz (demnächst) greift, nicht ob sie vor Ort bereits in Kraft ist. Der Berechnung liegen korrigierte Werte zugrunde inklusive Nachmeldungen. Stand: ' + \
            timestamp_str
        notes_chart2 = 'Der Berechnung liegen korrigierte Inzidenzwerte zugrunde inklusive Nachmeldungen. Stand: ' + \
            timestamp_str

        # insert id manually and run function
        update_chart(id='530c9a2b291a3ac848e9dc471a762204',
                     data=dfmap, notes=notes_chart, subtitle=subtitle_chart)
        update_chart(id='4c6603c3b465e2d11eb5b22d736dadcc',
                     data=dfedumap, notes=notes_chart2, subtitle=subtitle_chart2)
        update_chart(id='050befd50ccb2f5f9080d4bba4df423d',
                     data=dftable, notes=notes_chart, subtitle=subtitle_chart)

    except:
        raise
    finally:
        f.close()
