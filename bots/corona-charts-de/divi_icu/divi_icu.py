import os
import pandas as pd
import gc
import sys
from datetime import datetime

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # set source data
        url = 'https://diviexchange.blob.core.windows.net/%24web/zeitreihe-bundeslaender.csv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'zeitreihe-bundeslaender.csv'), 'wb') as f:
            f.write(download_data(url).read())

        # read columns needed for the chart
        df = pd.read_csv('./data/zeitreihe-bundeslaender.csv',
                         encoding='utf-8', usecols=['Datum', 'Bundesland', 'Aktuelle_COVID_Faelle_ITS', 'Belegte_Intensivbetten', 'Freie_Intensivbetten'])

        # non-Covid-19 patients
        df['Andere Patienten'] = df['Belegte_Intensivbetten'] - \
            df['Aktuelle_COVID_Faelle_ITS']

        # change date format and get current date for chart notes
        df['Datum'] = df['Datum'].str.replace(
            r'T12:15:00\+0[0-2]:00', '', regex=True)
        timestamp_str = df['Datum'].iloc[-1]
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d')
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # create dataframes for each variable and calculate sums for all states
        dfcovid = df.pivot_table(index=['Datum'], columns=[
            'Bundesland'], values='Aktuelle_COVID_Faelle_ITS')
        sum = dfcovid.columns[: dfcovid.shape[0]-1]
        dfcovid['mit Corona-Fällen'] = dfcovid[sum].sum(axis=1)
        dfcovid = dfcovid.filter(
            ['mit Corona-Fällen']).reset_index().rename_axis(None, axis=1)

        dfother = df.pivot_table(index=['Datum'], columns=[
            'Bundesland'], values='Andere Patienten')
        sum = dfother.columns[: dfother.shape[0]-1]
        dfother['mit anderen Patienten'] = dfother[sum].sum(axis=1)
        dfother = dfother.filter(
            ['mit anderen Patienten']).reset_index().rename_axis(None, axis=1)

        dffree = df.pivot_table(index=['Datum'], columns=[
            'Bundesland'], values='Freie_Intensivbetten')
        sum = dffree.columns[: dffree.shape[0]-1]
        dffree['unbelegt'] = dffree[sum].sum(axis=1)
        dffree = dffree.filter(
            ['unbelegt']).reset_index().rename_axis(None, axis=1)

        # create new dataframes for charts with Covid-19 patients and bed occupancy
        dfbeds = dfcovid.set_index('Datum').join(dfother.set_index('Datum')).join(
            dffree.set_index('Datum')).rename_axis(None)
        dfpatients = dfbeds[['mit Corona-Fällen']].copy().rename(
            columns={'mit Corona-Fällen': 'Corona-Patienten'})

        # delete old dataframes
        del [[df, dfcovid, dfother, dffree]]
        gc.collect()

        # start bed occupancy in August 2020 due to methodology update
        dfbeds = dfbeds.iloc[148:]

        # show date in chart notes
        notes_chartpatients = 'Stand: ' + \
            timestamp_str
        notes_chartbeds = '¹ Belegte und freie Betten ohne Notfallreserve (wird seit dem 3. 8. 2020 separat erfasst).<br>Stand: ' + \
            timestamp_str

        dfpatients.to_csv('../rki_cases/data/intensiv12h.csv',
                          encoding='utf-8', index=True)

        # insert id manually and run function
        update_chart(id='ab97925bcc5055b33011fb4d3326e163',
                     data=dfpatients, notes=notes_chartpatients)
        update_chart(id='ca6ad78976cf6de104f01ab6f59ce114',
                     data=dfbeds, notes=notes_chartbeds)

    except:
        raise
    finally:
        f.close()
