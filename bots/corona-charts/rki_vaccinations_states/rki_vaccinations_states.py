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

        # set source data and save
        url = 'https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv'
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'germany_vaccinations_by_state.tsv'), 'wb') as f:
            f.write(download_data(url).read())
        url = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv'
        with open(os.path.join('data', 'germany_vaccinations_timeseries_v2.tsv'), 'wb') as f:
            f.write(download_data(url).read())

        # read vaccination and population data
        df = pd.read_csv('./data/germany_vaccinations_by_state.tsv',
                         delimiter='\t', encoding='utf-8')
        dfpop = pd.read_csv('./pop_states_20193112.csv')
        dfde = pd.read_csv('./data/germany_vaccinations_timeseries_v2.tsv',
                           delimiter='\t', encoding='utf-8', usecols=['date', 'impf_quote_erst', 'impf_quote_voll'])

        # merge df1 and dfpop
        df = df.merge(dfpop, on='code')

        # get date for chart notes and add one day from dfde
        dfde = dfde.iloc[[-1]].reset_index(drop=True)
        timestamp_str = dfde.loc[0, 'date']
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # get percentagedfdes for germany
        de_first = (dfde['impf_quote_erst'].values[0] * 100).round(1)
        de_full = (dfde['impf_quote_voll'].values[0] * 100).round(1)
        de_total = dfde['impf_quote_erst'].values[0] + \
            dfde['impf_quote_voll'].values[0]
        de_total = (de_total * 100).round(1)

        # delete old df from memory
        del [[dfde]]
        gc.collect()

        # caluclate vaccination rates in new columns
        df['Gesamt'] = ((df['vaccinationsTotal'] / df['pop']) * 100).round(1)
        df['1. Dose'] = ((df['peopleFirstTotal'] / df['pop']) * 100).round(1)
        df['2. Dose'] = ((df['peopleFullTotal'] / df['pop']) * 100).round(1)

        # drop unwanted columns with absolute values
        df.drop(['vaccinationsTotal', 'peopleFirstTotal',
                'peopleFullTotal', 'pop'], axis=1, inplace=True)

        # add data for Germany at the top
        de = [{'code': 'Deutschland', 'Gesamt': de_total,
               '1. Dose': de_first, '2. Dose': de_full}]
        df = pd.concat(
            [pd.DataFrame(de), df], ignore_index=True)

        # create new df with data sorted by total vaccinations (except Germany)
        df2 = df[df.code != 'Deutschland'].sort_values(
            by='Gesamt', ascending=True)

        # add Germany
        df2 = df2.append(df[df.code == 'Deutschland'], ignore_index=True)

        # delete old df from memory
        del [[df]]
        gc.collect()

        # sort in descending order and bring Germany to top
        df2 = df2[::-1]

        # rename column headers
        df2['code'] = df2['code'].str.replace("DE-TH", "Thüringen").str.replace("DE-HB", "Bremen").str.replace("DE-SL", "Saarland").str.replace("DE-RP", "Rheinland-Pfalz").str.replace("DE-BY", "Bayern").str.replace("DE-BE", "Berlin").str.replace("DE-SH", "Schleswig-Holstein").str.replace("DE-HH", "Hamburg").str.replace(
            "DE-HE", "Hessen").str.replace("DE-NI", "Niedersachsen").str.replace("DE-BB", "Brandenburg").str.replace("DE-BW", "Baden-Württemberg").str.replace("DE-ST", "Sachsen-Anhalt").str.replace("DE-SN", "Sachsen").str.replace("DE-MV", "Mecklenburg-Vorpommern").str.replace("DE-NW", "Nordrhein-Westfalen")

        # rename first column and set as index
        df2 = df2.rename(columns={'code': 'Land'}).set_index('Land')

        # show date in chart notes
        notes_chart = 'Stand: ' + timestamp_str

        # run function
        update_chart(id='245e5a30acb9ffa8e53b336e6bda032b',
                     data=df2, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
