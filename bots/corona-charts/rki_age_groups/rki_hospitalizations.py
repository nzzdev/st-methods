import os
import pandas as pd
import gc
from datetime import datetime
import sys


if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        url = 'https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Hospitalisierungen_in_Deutschland/master/Aktuell_Deutschland_COVID-19-Hospitalisierungen.csv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'Aktuell_Deutschland_Impfquoten_COVID-19.csv'), 'wb') as f:
            f.write(download_data(url).read())

        # read columns needed for the chart
        dfall = pd.read_csv('./data/Aktuell_Deutschland_Impfquoten_COVID-19.csv',
                            encoding='utf-8', usecols=['Datum', 'Bundesland_Id', 'Altersgruppe', '7T_Hospitalisierung_Faelle'])

        # select rows with Germany and relevant age groups
        df = dfall.loc[dfall['Bundesland_Id'] == 0]
        df = df.drop(columns="Bundesland_Id")
        df = df.loc[df['Altersgruppe'].isin(
            ['00-04', '05-14', '15-34', '35-59', '60-79', '80+'])]

        # delete old dataframe
        del [[dfall]]
        gc.collect()

        # get date for chart notes and add one day
        timestamp_str = df.loc[0, 'Datum']
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d')
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # create a spreadsheet-style pivot table
        df = df.pivot_table(index=['Datum'], columns=[
                            'Altersgruppe'], values='7T_Hospitalisierung_Faelle')

        # create new column with sum, calculate percentage, then drop it
        sum = df.columns[: df.shape[0]-1]
        df['Summe'] = df[sum].sum(axis=1)
        df['00-04'] = ((df['00-04'] / df['Summe']) * 100)
        df['05-14'] = ((df['05-14'] / df['Summe']) * 100)
        df['15-34'] = ((df['15-34'] / df['Summe']) * 100)
        df['35-59'] = ((df['35-59'] / df['Summe']) * 100)
        df['60-79'] = ((df['60-79'] / df['Summe']) * 100)
        df['80+'] = ((df['80+'] / df['Summe']) * 100)
        df = df.drop(columns="Summe")

        # rename columns
        df = df.rename(columns={'00-04': '0-4', '05-14': '5-14'})

        # show date in chart notes
        notes_chart = '¹ Inklusive Intensivstationen.<br>Stand: ' + \
            timestamp_str

        # run function
        update_chart(id='31ebc60a92f9c59ce4023dc0e8dfec69',
                     data=df, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
