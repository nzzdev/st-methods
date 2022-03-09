import os
import pandas as pd
import sys

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # read csv
        df_divi = pd.read_csv('./data/intensiv.csv',
                              encoding='utf-8', index_col=0)
        df_cases = pd.read_csv('./data/faelle7d.csv',
                               encoding='utf-8', index_col=0)
        df_deaths = pd.read_csv('./data/tote7d.csv',
                                encoding='utf-8', index_col=0)

        # ICU patients
        df_divi['Intensiv'] = df_divi['Intensiv'] + df_divi['Beatmet']
        df_divi = df_divi.drop(df_divi.columns[1], axis=1)
        df_divi.index = pd.to_datetime(df_divi.index)

        # 7-day mvg average new cases
        df_cases.index = pd.to_datetime(df_cases.index)

        # 7-day mvg average deaths
        df_deaths.index = pd.to_datetime(df_deaths.index)

        # merge dataframes
        df = pd.concat([df_cases, df_divi, df_deaths], axis=1)

        # check if last row in ICU column is nan, then shift cases and deaths
        if pd.isna(df['Intensiv'].iloc[-1]) == True:
            df['Fälle'] = df['Fälle'].shift(1)
            df['Tote'] = df['Tote'].shift(1)

        # create new dataframe for trends and find last non NaN value
        df_meta = df.copy().tail(1)
        df_meta['Trend ICU'] = round(((df['Intensiv'].loc[~df['Intensiv'].isnull(
        )].iloc[-1] - df['Intensiv'].loc[~df['Intensiv'].isnull()].iloc[-8]) / df['Intensiv'].loc[~df['Intensiv'].isnull()].iloc[-8]) * 100, 0)
        df_meta['Trend Fälle'] = round(((df['Fälle'].loc[~df['Fälle'].isnull(
        )].iloc[-1] - df['Fälle'].loc[~df['Fälle'].isnull()].iloc[-8]) / df['Fälle'].loc[~df['Fälle'].isnull()].iloc[-8]) * 100, 0)
        df_meta['Trend Tote'] = round(((df['Tote'].loc[~df['Tote'].isnull(
        )].iloc[-1] - df['Tote'].loc[~df['Tote'].isnull()].iloc[-8]) / df['Tote'].loc[~df['Tote'].isnull()].iloc[-8]) * 100, 0)
        df_meta['Diff ICU'] = df['Intensiv'].loc[~df['Intensiv'].isnull(
        )].iloc[-1] - df['Intensiv'].loc[~df['Intensiv'].isnull()].iloc[-2]
        df_meta = df_meta[['Trend ICU', 'Trend Fälle',
                           'Trend Tote', 'Diff ICU', 'Fälle', 'Tote']]

        # replace percentages with strings
        cols = ('Trend ICU', 'Trend Fälle', 'Trend Tote')

        def replace_vals(df_meta):
            for col in cols:
                if df_meta[col] >= 5:
                    df_meta[col] = 'steigend'
                elif df_meta[col] <= -5:
                    df_meta[col] = 'fallend'
                else:
                    df_meta[col] = 'gleichbleibend'
            return df_meta
        df_meta = df_meta.apply(replace_vals, axis=1)

        # get last values of df_meta as objects
        df_meta = df_meta.iloc[0]
        trend_icu = df_meta['Trend ICU']
        trend_cases = df_meta['Trend Fälle']
        trend_deaths = df_meta['Trend Tote']
        diff_icu = df_meta['Diff ICU'].astype(int)
        diff_cases = df_meta['Fälle'].astype(int)
        diff_deaths = df_meta['Tote'].astype(int)

        # drop unused columns
        df = df[(df.index.get_level_values(0) >= '2020-10-01')].astype(int)
        df.dropna(inplace=True)

        # get current date for chart notes and reset index
        df = df.reset_index().rename({'Datum': 'date'}, axis='columns')
        df['date'] = pd.to_datetime(
            df['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        timestamp_str = df['date'].tail(1).item()

        # create dictionaries for JSON file
        dict_icu = df.drop(['Fälle', 'Tote'], axis=1).rename(
            columns={'Intensiv': 'value'}).to_dict(orient='records')
        dict_cases = df.drop(['Intensiv', 'Tote'], axis=1).rename(
            columns={'Fälle': 'value'}).to_dict(orient='records')
        dict_deaths = df.drop(['Intensiv', 'Fälle'], axis=1).rename(
            columns={'Tote': 'value'}).to_dict(orient='records')

        # additional data for JSON file
        meta_icu = {'indicatorTitle': 'Intensivpatienten', 'date': timestamp_str, 'indicatorSubtitle': 'Belegte Betten',
                    'value': int(diff_icu), 'color': '#24b39c', 'trend': trend_icu, 'chartType': 'area'}
        meta_cases = {'indicatorTitle': 'Neuinfektionen', 'date': timestamp_str, 'indicatorSubtitle': '7-Tage-Schnitt',
                      'value': int(diff_cases), 'color': '#e66e4a', 'trend': trend_cases, 'chartType': 'area'}
        meta_deaths = {'indicatorTitle': 'Neue Todesfälle', 'date': timestamp_str, 'indicatorSubtitle': '7-Tage-Schnitt',
                       'value': int(diff_deaths), 'color': '#05032d', 'trend': trend_deaths, 'chartType': 'area'}

        # merge dictionaries
        meta_icu['chartData'] = dict_icu
        meta_cases['chartData'] = dict_cases
        meta_deaths['chartData'] = dict_deaths
        dicts = []
        dicts.append(meta_cases)
        dicts.append(meta_icu)
        dicts.append(meta_deaths)

        # save data
        with open('./data/dashboard_de.json', 'w') as fp:
            json.dump(dicts, fp, indent=4)
        file = [{
            "loadSyncBeforeInit": True,
            "file": {
                "path": "./rki_cases/data/dashboard_de.json"
            }
        }]

        # run function
        update_chart(id='499935fb791197fd126bda721f15884a', files=file)

    except:
        raise
    finally:
        fp.close()
