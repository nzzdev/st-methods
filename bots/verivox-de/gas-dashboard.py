import os
import pandas as pd
import sys
import json
from datetime import date

if __name__ == '__main__':
    try:

        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # get current date
        today = date.today()
        todaystr = today.strftime('%Y-%m-%d')

        df_storage = pd.read_csv(
            f'./data/{todaystr}-gasspeicher.csv', encoding='utf-8', index_col='Datum')
        df_gas = pd.read_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t',
                             encoding='utf-8', usecols=['date', 'Gas'], index_col='date')
        df_super = pd.read_csv('./data/node_super.csv', encoding='utf-8',
                               usecols=['day', 'tages_mittel'], index_col='day')

        # sort, round, calculate mvg avg and convert index to DatetimeIndex
        df_storage.index = pd.to_datetime(df_storage.index)
        df_storage = df_storage.sort_index().round(0).astype(int)
        df_gas.index = pd.to_datetime(df_gas.index)
        df_super.index = pd.to_datetime(df_super.index)
        df_super = df_super.round(2)
        df_gas_mean = df_gas.rolling(window=7).mean().dropna()
        df_gas_mean.index = pd.to_datetime(df_gas_mean.index)

        # rename columns and remove dates before 2022-01-01
        df_gas_mean = df_gas_mean[(
            df_gas_mean.index.get_level_values(0) >= '2022-01-01')]
        df_storage.index = df_storage.index.rename('date')
        df_storage = df_storage.rename(columns={'2022': 'Gasspeicher'})
        df_super.index = df_super.index.rename('date')
        df_super = df_super.rename(columns={'tages_mittel': 'Benzinpreis'})
        df_gas = df_gas.rename(columns={'Gas': 'Gaspreis'})
        df_gas_mean = df_gas_mean.rename(columns={'Gas': 'Gaspreis'})

        # convert 20 MWh to 20000 kWh and euro to cent
        df_gas = (df_gas / 200).round(2)
        df_gas_mean = (df_gas_mean / 200).round(2)

        # merge dataframes
        df = pd.concat([df_storage, df_gas_mean, df_super], axis=1)

        # create temporary dataframe for old data in gas storage
        df_temp = df.copy().tail(90)

        # check if last row in gas storage column is NaN, then shift numbers
        while pd.isna(df_temp.iloc[-1:, 0].item()) == True:
            df_temp.iloc[:, 0] = df_temp.iloc[:, 0].shift(1)

        # create new dataframe for trends and find last non NaN value (ICU with iloc)
        df_meta = df_temp.copy().tail(1)
        df_meta['Trend Speicher'] = round(((df['Gasspeicher'].loc[~df['Gasspeicher'].isnull(
        )].iloc[-1] - df['Gasspeicher'].loc[~df['Gasspeicher'].isnull()].iloc[-2]) / df['Gasspeicher'].loc[~df['Gasspeicher'].isnull()].iloc[-2]) * 100, 0)  # diff previous day
        df_meta['Trend Gas'] = round(((df['Gaspreis'].loc[~df['Gaspreis'].isnull(
        )].iloc[-1] - df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-2]) / df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-2]) * 100, 0)  # diff 7-day mvg avg previous day
        df_meta['Trend Benzin'] = round(((df['Benzinpreis'].loc[~df['Benzinpreis'].isnull(
        )].iloc[-1] - df['Benzinpreis'].loc[~df['Benzinpreis'].isnull()].iloc[-8]) / df['Benzinpreis'].loc[~df['Benzinpreis'].isnull()].iloc[-8]) * 100, 0)  # diff previous week
        df_meta = df_meta[['Trend Speicher', 'Trend Gas',
                           'Trend Benzin', 'Gasspeicher', 'Gaspreis', 'Benzinpreis']]

        # replace percentages with strings
        cols = ('Trend Speicher', 'Trend Gas', 'Trend Benzin')

        # function for string trends (storage and gas=previous day, petrol=previous week)
        def replace_vals(df_meta):
            for col in cols:
                if df_meta[col] >= 1:
                    df_meta[col] = 'steigend'
                elif df_meta[col] <= -1:
                    df_meta[col] = 'fallend'
                else:
                    df_meta[col] = 'gleichbleibend'
            return df_meta
        df_meta = df_meta.apply(replace_vals, axis=1)

        # get last values of df_meta as objects
        df_meta = df_meta.iloc[0]
        trend_storage = df_meta['Trend Speicher']
        trend_gas = df_meta['Trend Gas']
        trend_super = df_meta['Trend Benzin']
        diff_storage = df_meta['Gasspeicher']
        diff_gas = df_gas['Gaspreis'].iloc[-1]
        diff_super = df_meta['Benzinpreis']

        # get current date for chart notes and reset index
        df = df.reset_index()
        df_storage = df_storage.reset_index()
        df_gas = df_gas.reset_index()
        df_super = df_super.reset_index()
        df['date'] = pd.to_datetime(
            df['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_storage['date'] = pd.to_datetime(
            df_storage['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_gas['date'] = pd.to_datetime(
            df_gas['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_super['date'] = pd.to_datetime(
            df_super['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        timestamp_str = df['date'].tail(1).item()

        # replace NaN with empty string for old storage data
        #df['Gasspeicher'] = df['Gasspeicher'].fillna(0).astype(int).astype(str)
        #df['Gasspeicher'] = df['Gasspeicher'].replace(['0', '0.0'], '')

        # create dictionaries for JSON file
        dict_storage = df_storage.rename(
            columns={df_storage.columns[1]: 'value'}).to_dict(orient='records')
        # dict_gas = df_gas.rename(columns={df_storage.columns[1]: 'value'}).to_dict(orient='records')
        dict_gas = df.drop(df.columns[[1, 3]], axis=1).rename(
            columns={df.columns[2]: 'value'}).to_dict(orient='records')  # 7-day mvg avg
        dict_super = df.drop(df.columns[[1, 2]], axis=1).rename(
            columns={df.columns[3]: 'value'}).to_dict(orient='records')

        # additional data for JSON file
        # y-axis start and ticks
        storage_y = 0  # if y-axis starts at 0: value is optional
        gas_y = 10
        super_y = 1.4
        storage_ytick = [0, 25, 50, 75, 100]
        gas_ytick = [10, 15, 20, 25]
        super_ytick = [1.6, 1.8, 2.0, 2.2, 2.4]

        # change decimal seperator
        diff_storage_str = diff_storage.astype(int)
        diff_gas_str = diff_gas.astype(str).replace('.', ',')
        diff_super_str = diff_super.astype(str).replace('.', ',')

        meta_storage = {'indicatorTitle': 'Gasspeicher', 'date': timestamp_str, 'indicatorSubtitle': 'Ziel: 80% am 1.10.', 'value': diff_storage,
                        'valueLabel': f'{diff_storage_str}%', 'yAxisStart': storage_y, 'yAxisLabels': storage_ytick, 'color': '#ce4631', 'trend': trend_storage, 'chartType': 'area'}
        meta_gas = {'indicatorTitle': 'Gaspreis', 'date': timestamp_str, 'indicatorSubtitle': 'Cent je kWh', 'value': diff_gas,
                    'valueLabel': f'{diff_gas_str}', 'yAxisStart': gas_y, 'yAxisLabels': gas_ytick, 'color': '#ce4631', 'trend': trend_gas, 'chartType': 'line'}
        meta_super = {'indicatorTitle': 'Benzinpreis', 'date': timestamp_str, 'indicatorSubtitle': 'Euro je Liter', 'value': diff_super,
                      'valueLabel': f'{diff_super_str}', 'yAxisStart': super_y, 'yAxisLabels': super_ytick, 'color': '#4d313c', 'trend': trend_super, 'chartType': 'line'}

        # merge dictionaries
        meta_storage['chartData'] = dict_storage
        meta_gas['chartData'] = dict_gas
        meta_super['chartData'] = dict_super
        dicts = []
        dicts.append(meta_storage)
        dicts.append(meta_gas)
        dicts.append(meta_super)

        with open('./data/dashboard_de.json', 'w') as fp:
            json.dump(dicts, fp, indent=4)
        file = [{
            "loadSyncBeforeInit": True,
            "file": {
                "path": "./data/dashboard_de.json"
            }
        }]

        # run Q function
        update_chart(id='38c6dc628d74a268a1d09ed8065f7803', files=file)

        # delete all csv and geojson files
        dir = 'data/'
        extracted = os.listdir(dir)
        for item in extracted:
            if item.endswith('.csv') or item.endswith('.geojson'):
                os.remove(os.path.join(dir, item))
        #os.remove(os.path.join(dir, 'dashboard_de.json'))

    except:
        raise
