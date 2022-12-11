import os
import pandas as pd
import sys
import json
from datetime import date, timedelta

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
            f'./data/{todaystr}-gasspeicher.csv', encoding='utf-8', index_col='Datum', usecols=['Datum', '2022'])
        df_storage_trend = pd.read_csv(
            f'./data/{todaystr}-gasspeicher.csv', encoding='utf-8', index_col='Datum', usecols=['Datum', 'Trend'])
        df_gas = pd.read_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t',
                             encoding='utf-8', usecols=['date', 'Gas'], index_col='date')
        df_strom = pd.read_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t',
                               encoding='utf-8', usecols=['date', 'Strom'], index_col='date')
        df_ns = pd.read_csv('./data/pipelines_ns.tsv',
                            sep='\t', encoding='utf-8', index_col='periodFrom')
        df_fossile = pd.read_csv(
            './data/smard_percentage.csv', encoding='utf-8', index_col='Datum')
        df_usage = pd.read_csv(
            './data/gasverbrauch.csv', encoding='utf-8', index_col='Datum', usecols=['Datum', 'Normaler Verbrauch¹', '2022'])
        # BENZIN df_super = pd.read_csv('./data/node_super.csv', encoding='utf-8', usecols=['day', 'tages_mittel'], index_col='day')

        # sort, round, calculate mvg avg and convert index to DatetimeIndex
        df_storage.index = pd.to_datetime(df_storage.index)
        df_storage = df_storage.sort_index().round(1)
        df_storage_trend.index = pd.to_datetime(df_storage_trend.index)
        df_storage_trend = df_storage_trend.sort_index()
        df_gas.index = pd.to_datetime(df_gas.index)
        df_strom.index = pd.to_datetime(df_strom.index)
        df_ns.index = pd.to_datetime(df_ns.index)
        # BENZIN df_super.index = pd.to_datetime(df_super.index)
        # BENZIN df_super = df_super.round(2)
        df_gas_mean = df_gas.rolling(window=7).mean().dropna()
        df_gas_mean.index = pd.to_datetime(df_gas_mean.index)
        df_strom_mean = df_strom.rolling(window=7).mean().dropna()
        df_strom_mean.index = pd.to_datetime(df_strom_mean.index)
        df_fossile.index = pd.to_datetime(df_fossile.index)
        df_fossile = df_fossile.sort_index().round(1)
        df_usage.index = pd.to_datetime(df_usage.index)
        df_usage = df_usage.sort_index()

        # rename columns and remove dates before 2022-01-01
        df_gas_mean = df_gas_mean[(
            df_gas_mean.index.get_level_values(0) >= '2022-01-01')]
        # df_gas = df_gas[(df_gas.index.get_level_values(0) >= '2021-01-01')]
        df_strom_mean = df_strom_mean[(
            df_strom_mean.index.get_level_values(0) >= '2022-01-01')]
        # df_strom = df_strom[(df_strom.index.get_level_values(0) >= '2021-01-01')]
        df_storage.index = df_storage.index.rename('date')
        df_storage = df_storage.rename(columns={'2022': 'Gasspeicher'})
        df_storage_trend.index = df_storage_trend.index.rename('date')
        # BENZIN df_super.index = df_super.index.rename('date')
        # BENZIN df_super = df_super.rename(columns={'tages_mittel': 'Benzinpreis'})
        df_gas = df_gas.rename(columns={'Gas': 'Gaspreis'})
        df_gas_mean = df_gas_mean.rename(columns={'Gas': 'Gaspreis'})
        df_strom = df_strom.rename(columns={'Strom': 'Strompreis'})
        df_strom_mean = df_strom_mean.rename(columns={'Strom': 'Strompreis'})
        df_ns.index = df_ns.index.rename('date')
        df_ns = df_ns.rename(columns={'Russland': 'Nord Stream 1'})
        df_fossile.index = df_fossile.index.rename('date')
        df_usage.index = df_usage.index.rename('date')
        df_usage = df_usage.rename(
            columns={'Normaler Verbrauch¹': 'Vorjahr', '2022': 'Gasverbrauch'})

        # convert 20 MWh to 20000 kWh and euro to cent / 4 MWh to 4000 kWh
        df_gas = (df_gas / 200).round(2)
        df_gas_mean = (df_gas_mean / 200).round(2)
        df_strom = (df_strom / 40).round(2)
        df_strom_mean = (df_strom_mean / 40).round(2)

        # merge dataframes
        df = pd.concat([df_gas, df_strom, df_fossile,
                       df_storage, df_usage['Gasverbrauch']], axis=1)
        # STORAGE df = pd.concat([df_storage, df_gas, df_strom], axis=1)
        # BENZIN df = pd.concat([df_storage, df_gas, df_super], axis=1)

        # create temporary dataframe for old data in gas storage and Russian gas
        df_temp = df.copy().tail(90)

        # check if last row in gas fossile(2)/storage (3)/usage(4) column is NaN, then shift numbers
        while pd.isna(df_temp.iloc[-1:, 2].item()) == True:
            df_temp.iloc[:, 2] = df_temp.iloc[:, 2].shift(1)
        while pd.isna(df_temp.iloc[-1:, 3].item()) == True:
            df_temp.iloc[:, 3] = df_temp.iloc[:, 3].shift(1)
        while pd.isna(df_temp.iloc[-1:, 4].item()) == True:
            df_temp.iloc[:, 4] = df_temp.iloc[:, 4].shift(1)
        # RUS GAS while pd.isna(df_temp.iloc[-1:, 1].item()) == True:
           # df_temp.iloc[:, 1] = df_temp.iloc[:, 1].shift(1)

        # calculate gas savings
        u_diff = ((df_usage['Gasverbrauch'].iloc[-1] /
                   df_usage['Vorjahr'].iloc[-1])-1)*100
        u_diffy = ((df_usage['Gasverbrauch'].iloc[-2] /
                    df_usage['Vorjahr'].iloc[-2])-1)*100
        u_diff_diffy = u_diff - u_diffy
        u_diff = u_diff.round(1)
        u_diff_str = f'{u_diff:+g}'

        # create new dataframe for trends and find last non NaN value (ICU with iloc)
        df_meta = df_temp.copy().tail(1)
        df_meta['Trend Gas'] = ((df['Gaspreis'].loc[~df['Gaspreis'].isnull(
        )].iloc[-1] - df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-2]) / df['Gaspreis'].loc[~df['Gaspreis'].isnull()].iloc[-2]) * 100  # diff previous day
        df_meta['Trend Strom'] = ((df['Strompreis'].loc[~df['Strompreis'].isnull(
        )].iloc[-1] - df['Strompreis'].loc[~df['Strompreis'].isnull()].iloc[-2]) / df['Strompreis'].loc[~df['Strompreis'].isnull()].iloc[-2]) * 100  # diff previous day
        df_meta['Trend Fossile'] = ((df['Fossile Abhängigkeit'].loc[~df['Fossile Abhängigkeit'].isnull(
        )].iloc[-1] - df['Fossile Abhängigkeit'].loc[~df['Fossile Abhängigkeit'].isnull()].iloc[-2]) / df['Fossile Abhängigkeit'].loc[~df['Fossile Abhängigkeit'].isnull()].iloc[-2]) * 100
        df_meta['Trend Speicher'] = df_storage_trend['Trend'].iloc[-1] * 10
        df_meta['Trend Verbrauch'] = u_diff_diffy
        # BENZIN df_meta['Trend Benzin'] = round(((df['Benzinpreis'].loc[~df['Benzinpreis'].isnull()].iloc[-1] - df['Benzinpreis'].loc[~df['Benzinpreis'].isnull()].iloc[-8]) / df['Benzinpreis'].loc[~df['Benzinpreis'].isnull()].iloc[-8]) * 100, 0)  # diff previous week

        # NS1 df_meta = df_meta[['Trend Speicher', 'Trend Gas', 'Trend NS1', 'Gasspeicher', 'Gaspreis', 'Strompreis']]
        # STORAGE df_meta = df_meta[['Trend Speicher', 'Trend Gas', 'Trend Strom', 'Gasspeicher', 'Gaspreis', 'Strompreis']]
        df_meta = df_meta[['Trend Gas', 'Trend Strom', 'Trend Fossile', 'Trend Speicher', 'Trend Verbrauch',
                           'Gaspreis', 'Strompreis', 'Fossile Abhängigkeit', 'Gasspeicher', 'Gasverbrauch']]

        # STROM/NS1: change cols1/cols7
        # replace percentages with strings
        # NS1 cols1 = ['Trend Speicher', 'Trend Gas']
        # NS1 cols7 = ['Trend NS1']
        # STORAGE cols1 = ['Trend Speicher', 'Trend Gas', 'Trend Strom']
        cols1 = ['Trend Gas', 'Trend Strom', 'Trend Fossile',
                 'Trend Speicher', 'Trend Verbrauch']

        # function for string trends (storage and gas=previous day, petrol=previous week)
        def replace_vals(df_meta):
            for col in cols1:
                if df_meta[col] >= 0.2:
                    df_meta[col] = 'steigend'
                elif df_meta[col] <= -0.2:
                    df_meta[col] = 'fallend'
                else:
                    df_meta[col] = 'gleichbleibend'
            """
            # NS1
            for col in cols7:
                if df_meta[col] >= 7:
                    df_meta[col] = 'steigend'
                elif df_meta[col] <= -7:
                    df_meta[col] = 'fallend'
                else:
                    df_meta[col] = 'gleichbleibend'
            """
            return df_meta
        df_meta = df_meta.apply(replace_vals, axis=1)

        # get last values of df_meta as objects
        df_meta = df_meta.iloc[0]
        trend_storage = df_meta['Trend Speicher']
        trend_gas = df_meta['Trend Gas']
        trend_strom = df_meta['Trend Strom']
        trend_fossile = df_meta['Trend Fossile']
        trend_usage = df_meta['Trend Verbrauch']
        # NS1 trend_ns = df_meta['Trend NS1']
        # RUS GAS trend_rus = df_meta['Trend Importe']
        # BENZIN trend_super = df_meta['Trend Benzin']
        diff_storage = df_meta['Gasspeicher']
        diff_gas = df_gas['Gaspreis'].iloc[-1]
        diff_strom = df_strom['Strompreis'].iloc[-1]
        diff_ns = df_ns['Nord Stream 1'].iloc[-1].round(2)
        diff_fossile = df_fossile['Fossile Abhängigkeit'].iloc[-1]
        diff_usage = u_diff_str
        # RUS GAS diff_rus = df_meta['Russisches Gas']
        # BENZIN diff_super = df_meta['Benzinpreis']

        # get current date for chart notes and reset index
        df = df.reset_index()
        df_storage = df_storage.reset_index()
        df_gas = df_gas.reset_index()
        df_strom = df_strom.reset_index()
        df_ns = df_ns.reset_index()
        df_fossile = df_fossile.reset_index()
        df_usage = df_usage.reset_index()
        # BENZIN df_super = df_super.reset_index()
        df['date'] = pd.to_datetime(
            df['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_storage['date'] = pd.to_datetime(
            df_storage['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_gas['date'] = pd.to_datetime(
            df_gas['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_strom['date'] = pd.to_datetime(
            df_strom['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_ns['date'] = pd.to_datetime(
            df_ns['date'], dayfirst=True).dt.strftime('%Y-%m-%d %H:%M:%S')
        df_fossile['date'] = pd.to_datetime(
            df_fossile['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        df_usage['date'] = pd.to_datetime(
            df_usage['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        # BENZIN df_super['date'] = pd.to_datetime(df_super['date'], dayfirst=True).dt.strftime('%Y-%m-%d')
        timestamp_str = df_gas['date'].tail(1).item()
        timestamp_str_price = df_gas['date'].tail(1).item()
        timestamp_str_price = pd.to_datetime(
            timestamp_str_price).strftime('%-d. %-m.')
        timestamp_str_usage = df_usage['date'].tail(1).item()
        timestamp_str_usage = pd.to_datetime(
            timestamp_str_usage).strftime('%-d. %-m.')
        timestamp_str_storage = df_storage['date'].tail(1).item()
        timestamp_str_storage = pd.to_datetime(
            timestamp_str_storage).strftime('%-d. %-m.')
        timestamp_str_fossile = (pd.to_datetime(
            df_fossile['date'].tail(1).item()) - timedelta(days=1)).strftime('KW %U')  # tail(2)=last week

        # OLD replace NaN with empty string for old storage data
        # df['Gasspeicher'] = df['Gasspeicher'].fillna(0).astype(int).astype(str)
        # df['Gasspeicher'] = df['Gasspeicher'].replace(['0', '0.0'], '')

        # create dictionaries for JSON file and drop NaN
        # dict_gas = df_gas.rename(columns={df_storage.columns[1]: 'value'}).to_dict(orient='records')
        # BENZIN dict_super = df.drop(df.columns[[1, 2]], axis=1).rename(columns={df.columns[3]: 'value'}).to_dict(orient='records')
        dict_storage = df_storage.rename(
            columns={df_storage.columns[1]: 'value'}).to_dict(orient='records')
        dict_gas = df.drop(df.columns[[2, 3]], axis=1).rename(
            columns={df.columns[1]: 'value'}).dropna().to_dict(orient='records')
        dict_strom = df.drop(df.columns[[1, 3]], axis=1).rename(
            columns={df.columns[2]: 'value'}).dropna().to_dict(orient='records')
        dict_fossile = df_fossile.rename(
            columns={df_fossile.columns[1]: 'value'}).to_dict(orient='records')
        dict_usage = df_usage.rename(
            columns={df_usage.columns[2]: 'value'}).to_dict(orient='records')
        df_ns['Nord Stream 1'] = df_ns['Nord Stream 1'].round(2).astype(float)
        dict_ns = df_ns.rename(
            columns={'Nord Stream 1': 'value'}).dropna().to_dict(orient='records')

        # additional data for JSON file
        # y-axis start and ticks
        storage_y = 0  # if y-axis starts at 0: value is optional
        gas_y = 0
        strom_y = 0
        ns_y = 0
        fossile_y = 20
        # RUS GAS rus_y = 0
        # BENZIN super_y = 1.6
        storage_ytick = [0, 25, 50, 75, 100]
        gas_ytick = [0, 15, 30, 45]
        strom_ytick = [0, 20, 40, 60]
        ns_ytick = [0, 0.5, 1, 1.5]
        fossile_ytick = [20, 35, 50, 65]
        # RUS GAS rus_ytick = [0, 100, 200, 300]
        # BENZIN super_ytick = [1.6, 1.8, 2.0, 2.2, 2.4]

        # change decimal seperator
        diff_storage_str = diff_storage.astype(str).replace('.', ',')
        diff_gas_str = diff_gas.astype(str).replace('.', ',')
        diff_strom_str = diff_strom.astype(str).replace('.', ',')
        diff_ns_str = diff_ns.astype(str).replace('.', ',')
        diff_fossile_str = diff_fossile.astype(str).replace('.', ',')
        diff_fossile = diff_fossile.astype(float)
        diff_usage_str = u_diff_str.replace('.', ',')
        # RUS GAS diff_rus_str = diff_rus.round(0).astype(int)
        # BENZIN diff_super_str = diff_super.astype(str).replace('.', ',')

        meta_storage = {'indicatorTitle': 'Gasspeicher', 'date': timestamp_str, 'indicatorSubtitle': f'Füllstand in Prozent am {timestamp_str_storage}', 'value': diff_storage, 'valueLabel': f'{diff_storage_str} %',
                        'yAxisStart': storage_y, 'yAxisLabels': storage_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_storage, 'chartType': 'area'}
        meta_gas = {'indicatorTitle': 'Gaspreis', 'date': timestamp_str, 'indicatorSubtitle': f'je kWh für Neukunden am  {timestamp_str_price}', 'value': diff_gas, 'valueLabel': f'{diff_gas_str} Cent',
                    'yAxisStart': gas_y, 'yAxisLabels': gas_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_gas, 'chartType': 'line'}
        meta_strom = {'indicatorTitle': 'Strompreis', 'date': timestamp_str, 'indicatorSubtitle': f'je kWh für Neukunden am  {timestamp_str_price}', 'value': diff_strom, 'valueLabel': f'{diff_strom_str} Cent',
                      'yAxisStart': strom_y, 'yAxisLabels': strom_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_strom, 'chartType': 'line'}
        meta_fossile = {'indicatorTitle': 'Fossile Abhängigkeit', 'date': timestamp_str, 'indicatorSubtitle': f'bei der Stromerzeugung in der {timestamp_str_fossile}',
                        'value': diff_fossile, 'valueLabel': f'{diff_fossile_str} %', 'yAxisStart': fossile_y, 'yAxisLabels': fossile_ytick, 'yAxisLabelDecimals': 0, 'color': '#374e8e', 'trend': trend_fossile, 'chartType': 'area'}
        meta_usage = {'indicatorTitle': 'Gasverbrauch', 'date': timestamp_str, 'indicatorSubtitle': f'Abweichung vom üblichen Verbrauch',
                      'value': u_diff, 'valueLabel': f'{diff_usage_str} %', 'yAxisStart': gas_y, 'yAxisLabels': gas_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_fossile, 'chartType': 'line'}

        # NS 1 meta_ns = {'indicatorTitle': 'Nord Stream 1', 'date': timestamp_str, 'indicatorSubtitle': 'Gasflüsse pro Stunde', 'value': diff_ns, 'valueLabel': f'{diff_ns_str} Mio. m³', 'yAxisStart': strom_y, 'yAxisLabels': ns_ytick, 'yAxisLabelDecimals': 1, 'color': '#ce4631', 'trend': trend_ns, 'chartType': 'line'}
        # RUS GAS meta_rus = {'indicatorTitle': 'Russisches Gas', 'date': timestamp_str, 'indicatorSubtitle': 'Gasflüsse nach Deutschland', 'value': diff_rus, 'valueLabel': f'{diff_rus_str} Mio. m³', 'yAxisStart': rus_y, 'yAxisLabels': rus_ytick, 'yAxisLabelDecimals': 0, 'color': '#ce4631', 'trend': trend_rus, 'chartType': 'line'}
        # BENZIN meta_super = {'indicatorTitle': 'Benzinpreis', 'date': timestamp_str, 'indicatorSubtitle': 'je Liter Super E5', 'value': diff_super, 'valueLabel': f'{diff_super_str} Euro', 'yAxisStart': super_y, 'yAxisLabels': super_ytick, 'yAxisLabelDecimals': 1, 'color': '#4d313c', 'trend': trend_super, 'chartType': 'line'}

        # merge dictionaries
        # STORAGE meta_storage['chartData'] = dict_storage
        meta_gas['chartData'] = dict_gas
        meta_strom['chartData'] = []
        meta_fossile['chartData'] = []
        meta_usage['chartData'] = []
        meta_storage['chartData'] = []
        # NS1 meta_ns['chartData'] = dict_ns
        # RUS GAS meta_rus['chartData'] = dict_rus
        # BENZIN meta_super['chartData'] = dict_super
        dicts = []
        # STORAGE dicts.append(meta_storage)
        # RUS GAS dicts.append(meta_rus)
        dicts.append(meta_gas)
        dicts.append(meta_usage)
        dicts.append(meta_storage)
        dicts.append(meta_strom)
        dicts.append(meta_fossile)
        # NS1 dicts.append(meta_ns)
        # BENZIN dicts.append(meta_super)
        with open('./data/dashboard_de.json', 'w') as fp:
            json.dump(dicts, fp, indent=4)
        file = [{
            "loadSyncBeforeInit": True,
            "file": {
                "path": "./data/dashboard_de.json"
            }
        }]

        # add chart notes
        # today_str = today.strftime('%-d. %-m. %Y')
        # notes_chart = f'Stand: {today_str}. Pfeile: Veränderung zum Vortag, beim Sprit zur Vorwoche. Quellen: Agsi, Verivox, Bundeskartellamt'

        # run Q function
        update_chart(id='38c6dc628d74a268a1d09ed8065f7803', files=file)

        # delete all csv and geojson files
        dir = 'data/'
        extracted = os.listdir(dir)
        for item in extracted:
            if item.endswith('.csv') or item.endswith('.geojson'):
                os.remove(os.path.join(dir, item))
        # os.remove(os.path.join(dir, 'dashboard_de.json'))

    except:
        raise
