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
        url = 'https://diviexchange.blob.core.windows.net/%24web/zeitreihe-tagesdaten.csv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'zeitreihe-landkreise.csv'), 'wb') as f:
            f.write(download_data(url).read())

        # read columns needed for the chart
        dfall = pd.read_csv('./data/zeitreihe-landkreise.csv',
                            encoding='utf-8', usecols=['date', 'gemeindeschluessel', 'faelle_covid_aktuell', 'betten_frei', 'betten_belegt'])

        dfags = pd.read_csv('./ags.csv', encoding='utf-8', index_col=0)

        # add leading zero to AGS in dfags
        dfags.index = dfags.index.astype(str)
        dfags.index = dfags.index.str.rjust(5, '0')

        # get date for chart notes and drop old data
        timestamp_str = dfall['date'].iloc[-1]
        dfall = dfall.loc[dfall['date'] == timestamp_str]
        dfall = dfall.drop(['date'], axis=1)
        df = dfall.copy()
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d')
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # delete old df from memory
        del [[dfall]]
        gc.collect()

        # sort data by AGS
        df = df.sort_values(by=['gemeindeschluessel'])
        df = df.set_index('gemeindeschluessel')
        df.index = df.index.rename('ID')

        # add leading zero to AGS in df
        df.index = df.index.astype(str)
        df.index = df.index.str.rjust(5, '0')
        # add leading zero to AGS with int instead of str
        # df['gemeindeschluessel'] = df['gemeindeschluessel'].apply(lambda x: '{0:0>5}'.format(x))

        # calculate percentage of occupied beds and Covid-19 patients
        df['% Belegt'] = (
            df['betten_belegt'] / (df['betten_frei'] + df['betten_belegt'])) * 100
        df['% Belegt'] = df['% Belegt'].round(
            0).astype(int)
        df['% Covid-Patienten'] = (df['faelle_covid_aktuell'] /
                                   df['betten_belegt']) * 100
        df['% Covid-Patienten'] = df['% Covid-Patienten'].round(
            0).astype(int)

        # join with dfags
        df = dfags.join(df)

        # create new dataframe for table
        dftable = df.copy()
        dftable = dftable.sort_values(
            by=['% Covid-Patienten'], ascending=False)
        dftable = dftable.set_index('Region')

        # drop unused columns and NaN values for table
        dftable = dftable.drop(
            ['faelle_covid_aktuell', 'betten_frei', 'betten_belegt'], axis=1)
        dftable['% Covid-Patienten'] = dftable['% Covid-Patienten'].fillna(
            -1).astype(int).astype(str).replace('-1', '')
        dftable['% Belegt'] = dftable['% Belegt'].fillna(
            -1).astype(int).astype(str).replace('-1', '')

        # drop unused columns and NaN values for map
        df = df.drop(
            ['Region', 'Land', 'faelle_covid_aktuell', 'betten_frei', 'betten_belegt', '% Belegt'], axis=1)
        df['% Covid-Patienten'] = df['% Covid-Patienten'].fillna(-1).astype(
            int).astype(str).replace('-1', '')

        # create notes for map and table
        notes_chartmap = 'Kreise ohne Zahlen: Meldung standortübergreifend am Hauptsitz des Klinikverbunds oder keine Intensivstation.<br>Stand: ' + timestamp_str
        notes_charttable = 'Kreise ohne Zahlen: Meldung standortübergreifend am Hauptsitz des Klinikverbunds oder keine Intensivstation.<br>In einzelnen Kreisen mit Intensivstation, etwa in Rastatt, gibt es keine Covid-19-Patienten, weil umliegende Spitäler diese aufnehmen.<br>Stand: ' + timestamp_str

        # run function
        update_chart(id='81caa0242fa168d128995977cd4026a8',
                     data=df, notes=notes_chartmap)
        update_chart(id='81caa0242fa168d128995977cd45268b',
                     data=dftable, notes=notes_charttable)

    except:
        raise
    finally:
        f.close()
