import os
import pandas as pd
import numpy as np
import gc
from datetime import datetime, timedelta
import sys
pd.options.mode.chained_assignment = None

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        url = 'https://raw.githubusercontent.com/jgehrcke/covid-19-germany-gae/master/more-data/7di-rki-by-ags.csv'

        # save data
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

        # Copy values from Wartburgkreis (16063) to Eisenach (16056) region
        df.iloc[383] = df.iloc[386].values

        # add current incidence in df of table chart
        # dftable['Inzidenz'] = df.iloc[:, -1].round(0).astype(int)
        # add incidence from three days ago with little reporting delay
        dftable['Inzidenz'] = df.iloc[:, -4].round(0).astype(int)

        # calculate trend and add to new Inzidenz column
        dftable['Trend'] = (
            ((df.iloc[:, -4] - df.iloc[:, -11]) / df.iloc[:, -11]) * 100)
        # remove inf values
        dftable['Trend'] = dftable['Trend'].replace(
            [np.inf, -np.inf], np.nan)
        # replace rows with unplausible trend/Nachmeldungen
        dftable['Trend'][(dftable['Trend'] >= 500)] = np.nan
        dftable['Trend'][(dftable['Trend'] == -100)] = np.nan

        #dftable = dftable[dftable['Trend'] > 500] = '-'
        #dftable['Trend'] = dftable['Trend'].apply(lambda x: x.replace('.0', ''))
        #dftable['Trend'] = dftable.dropna()
        #dftable = dftable[~(dftable['Trend'] > 500)]

        dftable['Trend_arrow'] = ''
        dftable['Trend_arrow'][(dftable['Trend'] <= -5)] = '➘ '
        dftable['Trend_arrow'][(dftable['Trend'] >= 5)] = '➚ '
        dftable['Trend_arrow'][(dftable['Trend'] < 5)
                               & (dftable['Trend'] > -5)] = '➙ '
        # add arrows to trend and ignore regions with NaN values
        dftable['Trend_tmp'] = dftable['Trend'].round(0)

        dftable['Trend_tmp'] = dftable['Trend_tmp'].apply(
            lambda x: '+'+str(x) if x > 0 else x)
        dftable['Trend'][dftable['Trend'].notnull()] = dftable['Trend_arrow'] + \
            dftable['Trend_tmp'].astype(str) + '%'
        # remove decimals
        dftable['Trend'] = dftable['Trend'].fillna('').astype(str)
        dftable['Trend'] = dftable['Trend'].apply(
            lambda x: x.replace('.0', ''))
        dftable['Trend'] = dftable['Trend'].apply(
            lambda x: x.replace('-0', '+0'))

        # delete old df from memory
        del [[df]]
        gc.collect()

        # create new df for choropleth map
        dfmap = dftable.copy()

        # drop unused/temporary columns
        dfmap = dfmap.drop(dfmap.columns[[0, 1, 2, 4, 5, 6]], axis=1)
        dfmap = dfmap.rename(columns={'Inzidenz': 'Wert'})
        dftable = dftable.drop(dftable.columns[[2, 5, 6]], axis=1)

        # sort dftable by pop
        # dftable.sort_values(dftable.columns[1], inplace=True, ascending=False)

        # sort dftable by case numbers and make region name the row index
        dftable.sort_values('Inzidenz', inplace=True, ascending=False)
        dftable.set_index('Region', inplace=True)

        # rearrange columns
        dftable = dftable[['Land', 'Trend', 'Inzidenz']]

        # replace empty strings with NaN and -
        dftable['Trend'] = dftable['Trend'].replace('', np.nan, regex=False)
        dftable['Trend'] = dftable['Trend'].fillna('-')

        # set chart notes
        notes_chart = 'Farbskala dynamisch.<br>Stand: ' + timestamp_str
        notes_chart_table = 'Wegen des starken Meldeverzugs zeigt die NZZ die korrigierten Werte von vor drei Tagen.<br>Stand: ' + timestamp_str

        # run function
        update_chart(id='2a1327d75c83a9c4ea49f935dd3ee925',
                     data=dfmap, notes=notes_chart)
        update_chart(id='8eed9f1d79be72ddbd0d9d0fc23970ea',
                     data=dftable, notes=notes_chart_table)

    except:
        raise
    finally:
        f.close()
