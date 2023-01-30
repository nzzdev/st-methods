import time
import pandas as pd
import os
from datetime import datetime, timedelta
from time import sleep

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *
        import helpers_smard as smard

        # power generation
        REALIZED_POWER_GENERATION = [1001224, 1004066, 1004067, 1004068,
                                     1001223, 1004069, 1004071, 1004070, 1001226, 1001228, 1001227, 1001225]
        INSTALLED_POWER_GENERATION = [3004072, 3004073, 3004074, 3004075,
                                      3004076, 3000186, 3000188, 3000189, 3000194, 3000198, 3000207, 3003792]
        FORECASTED_POWER_GENERATION = [
            2000122, 2000715, 2000125, 2003791, 2000123]

        # power consumption
        FORECASTED_POWER_CONSUMPTION = [6000411, 6004362]
        REALIZED_POWER_CONSUMPTION = [5000410, 5004359]

        # market
        WHOLESALE_PRICES = [8004169, 8004170, 8000252, 8000253, 8000251, 8000254,
                            8000255, 8000256, 8000257, 8000258, 8000259, 8000260, 8000261, 8000262]
        COMMERCIAL_FOREIGN_TRADE = [8004169, 8004170, 8000252, 8000253, 8000251, 8000254,
                                    8000255, 8000256, 8000257, 8000258, 8000259, 8000260, 8000261, 8000262]
        PHYSICAL_POWER_FLOW = [31000714, 31000140, 31000569, 31000145, 31000574, 31000570, 31000139, 31000568,
                               31000138, 31000567, 31000146, 31000575, 31000144, 31000573, 31000142, 31000571, 31000143, 31000572, 31000141]

        # commercial trade Germany/France
        COMMERCIAL_TRADE_FRANCE = [22004546, 22004404]

        # spot market
        SPOT_MARKET = [8004169]

        def last_valid_value(list):
            nnlist = []
            for i in list:
                if(i != "-"):
                    nnlist.append(i)
            return float(nnlist[-1])

        ################################
        # API request power generation #
        ################################
        modules = REALIZED_POWER_GENERATION
        # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
        df = smard.requestSmardData(
            modulIDs=modules, timestamp_from_in_milliseconds=1609628400000)  # first week of 2021

        # check if data is corrupted
        errors = 0
        while ('Anfang' not in df.columns) and (errors < 5):
            sleep(2)
            errors += 1
            # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
            df = smard.requestSmardData(
                modulIDs=modules, timestamp_from_in_milliseconds=1609628400000)  # first week of 2021
        if ('Anfang' in df.columns):
            # fix wrong decimal
            df = df.replace('-', '', regex=False)
            df.to_csv('./data/smard_fixed.tsv', sep='\t',
                      encoding='utf-8', index=False)
            df = pd.read_csv('./data/smard_fixed.tsv', sep='\t', thousands='.', decimal=',',
                             index_col=None, dtype={'Datum': 'string', 'Anfang': 'string'})

            # drop time and convert dates
            df.drop('Anfang', axis=1, inplace=True)
            df.drop('Ende', axis=1, inplace=True)
            df['Datum'] = pd.to_datetime(df['Datum'], format="%d.%m.%Y")

            # old decimal fix
            #df.loc[:, df.columns != 'Datum'] = df.loc[:, df.columns != 'Datum'].replace('\,', '.', regex=True).astype(float)

            df = df.groupby(['Datum']).sum()

            # create new columns and drop the old ones
            df['Biomasse'] = df['Biomasse [MWh] Originalauflösungen']
            df['Sonstige'] = df['Sonstige Konventionelle [MWh] Originalauflösungen']
            df['Kernkraft'] = df['Kernenergie [MWh] Originalauflösungen']
            df['Erdgas'] = df['Erdgas [MWh] Originalauflösungen']
            df['Pumpspeicher'] = df['Pumpspeicher [MWh] Originalauflösungen']
            df['Kohle'] = df['Braunkohle [MWh] Originalauflösungen'] + \
                df['Steinkohle [MWh] Originalauflösungen']
            df['Sonstige EE'] = df['Sonstige Erneuerbare [MWh] Originalauflösungen'] + \
                df['Wasserkraft [MWh] Originalauflösungen']
            df['Wind'] = df['Wind Offshore [MWh] Originalauflösungen'] + \
                df['Wind Onshore [MWh] Originalauflösungen']
            df['Sonne'] = df['Photovoltaik [MWh] Originalauflösungen']
            df.drop(list(df)[0:12], axis=1, inplace=True)

            # convert to week and drop first and last row with partial values
            df.reset_index(inplace=True)
            df = df.resample('W', on='Datum').sum()
            # no drop for step-after chart
            df.drop(df.tail(1).index, inplace=True)
            df.drop(df.head(1).index, inplace=True)

            # save tsv
            df.to_csv('./data/smard_fixed.tsv', sep='\t',
                      encoding='utf-8', index=True)

        # read tsv (old or new)
        df = pd.read_csv('./data/smard_fixed.tsv', sep='\t', index_col='Datum')
        df.index = pd.to_datetime(df.index)

        # get current date for chart notes
        time_dt_notes = df.index[-1] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Auf der Y-Achse: Stromerzeugung in absoluten Zahlen (TWh) gemäss EU-Transparenzverordnung; diese entsprachen im Jahr 2020 93 Prozent des insgesamt erzeugten Stroms.<br>Stand: {time_str_notes}'

        # calculate percentage for chart title
        df_perc = df.tail(1).div(df.tail(1).sum(axis=1), axis=0)
        perc_gas = (df_perc['Erdgas'].iloc[-1]*100).round(0).astype(int)
        if perc_gas > 1:
            title_chart = f'{perc_gas} Prozent des Stroms stammen derzeit aus Erdgas'
        else:
            title_chart = f'{perc_gas} Prozent des Stroms stammt derzeit aus Erdgas'

        # calculate percentage for dashboard
        df_dash = df.div(df.sum(axis=1), axis=0)
        df_dash = (df_dash * 100).round(1)
        df_dash = df_dash[~(df_dash.index < '2021-01-04 00:00:00')]
        column_sum = ['Erdgas', 'Sonstige', 'Kohle']
        df_dash['Fossile Abhängigkeit'] = df_dash[column_sum].sum(axis=1)
        df_dash = df_dash[['Fossile Abhängigkeit']]

        # combine conventional
        df['Sonstige'] = df['Sonstige'] + \
            df['Pumpspeicher'] + df['Sonstige EE']

        df = df.drop(['Pumpspeicher', 'Sonstige EE'], axis=1)

        # drop unused rows and convert to terawatt
        df = df[~(df.index < '2021-07-18 00:00:00')]
        df = df.div(1000000)

        df_dash.to_csv('./data/smard_percentage.csv')

        # convert DatetimeIndex to string
        # df.index = df.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(id='e468de3ac9c422bcd0924e26b60a2af8',
                     data=df, notes=notes_chart, title=title_chart)

        ###########################
        # API request spot market #
        ###########################
        modules = SPOT_MARKET
        df_spot = smard.requestSmardData(
            modulIDs=modules, region="DE-LU", timestamp_from_in_milliseconds=1608764400000)  # 2021/1/1: 1609455600000

        # check if data is corrupted
        errors = 0
        while ('Anfang' not in df_spot.columns) and (errors < 5):
            sleep(2)
            errors += 1
            df_spot = smard.requestSmardData(
                modulIDs=modules, region="DE-LU", timestamp_from_in_milliseconds=1608764400000)  # 2021/1/1: 1609455600000
        if ('Anfang' in df_spot.columns):
            # fix wrong decimal
            df_spot = df_spot.replace('-', '', regex=False)
            df_spot.to_csv('./data/smard_spot.tsv', sep='\t',
                           encoding='utf-8', index=False)
            df_spot = pd.read_csv('./data/smard_spot.tsv', sep='\t', thousands='.', decimal=',',
                                  index_col=None, dtype={'Datum': 'string', 'Anfang': 'string'})

            # drop time and convert dates to DatetimeIndex
            df_spot.drop('Anfang', axis=1, inplace=True)
            df_spot.drop('Ende', axis=1, inplace=True)
            df_spot['Datum'] = pd.to_datetime(
                df_spot['Datum'], format="%d.%m.%Y")

            # calculate daily mean and 7-day moving average
            df_spot = df_spot.resample('D', on='Datum').mean()
            df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'] = df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'].rolling(
                window=7).mean().dropna()
            df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'] = df_spot[
                'Deutschland/Luxemburg [€/MWh] Originalauflösungen'].round(0)

            # drop last row with current date to avoid constant commits
            df_spot = df_spot.drop(df_spot.tail(1).index)

            # save tsv
            df_spot.to_csv('./data/smard_spot.tsv', sep='\t',
                           encoding='utf-8', index=True)

        # read tsv (old or new)
        df_spot = pd.read_csv('./data/smard_spot.tsv',
                              sep='\t', index_col='Datum')
        df_spot.index = pd.to_datetime(df_spot.index)

        # get current date
        q_date = df_spot.last_valid_index()
        notes_chart = '¹ Marktgebiet Deutschland/Luxemburg (Day-Ahead).<br>Stand: ' + \
            q_date.strftime("%-d. %-m. %Y")

        # drop unused dates
        #df_spot = df_spot[df_spot.any(1)]
        df_spot = df_spot['2021-01-01': q_date]
        df_spot = df_spot[df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'].notna()]
        df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'] = df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'].astype(
            int)

        # dynamic chart title
        title_mwh = df_spot[df_spot.columns[0]].iloc[-1]
        title = f'Strom kostet an der Börse {title_mwh} Euro je MWh'

        # run Q function
        update_chart(id='90005812afc9964bbfe4f952f51d6a57',
                     title=title, notes=notes_chart, data=df_spot)

        ################
        # TRADE FRANCE #
        ################

        modules = COMMERCIAL_TRADE_FRANCE
        df_trade = smard.requestSmardData(
            modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1606604400000)  # 2020/11/29

        # check if data is corrupted
        errors = 0
        while ('Anfang' not in df.columns) and (errors < 5):
            sleep(2)
            errors += 1
            # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
            df = smard.requestSmardData(
                modulIDs=modules, timestamp_from_in_milliseconds=1609628400000)  # first week of 2021
        if ('Anfang' in df_trade.columns):
            # fix wrong decimal
            df_trade = df_trade.replace('-', '', regex=False)
            df_trade.to_csv('./data/smard_trade_fixed.tsv',
                            sep='\t', encoding='utf-8', index=False)
            df_trade = pd.read_csv('./data/smard_trade_fixed.tsv', sep='\t', thousands='.',
                                   decimal=',', index_col=None, dtype={'Datum': 'string', 'Anfang': 'string'})

            # drop time and convert dates
            df_trade.drop('Anfang', axis=1, inplace=True)
            df_trade.drop('Ende', axis=1, inplace=True)
            df_trade['Datum'] = pd.to_datetime(
                df_trade['Datum'], format="%d.%m.%Y")

            # calculate net electricity exports
            df_trade['Saldo'] = df_trade['Frankreich (Export) [MWh] Originalauflösungen'] - \
                abs(df_trade['Frankreich (Import) [MWh] Originalauflösungen'])

            # convert to gigawatt
            df_trade['Saldo'] = df_trade['Saldo'].div(1000)
            df_trade = df_trade[['Datum', 'Saldo']]

            # convert to week and drop first row with partial values
            df_trade = df_trade.resample('W', on='Datum').sum()
            df_trade.drop(df_trade.head(1).index, inplace=True)

            # update first row for prettier x-axis
            #df_trade['Datum'] = df_trade.index
            #df_trade['Datum'].iloc[0] = '2021-01-01'
            #df_trade.set_index('Datum', inplace=True)

            # update last row for step-after chart (avoid constant commits)
            df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

            # save tsv
            df_trade.to_csv('./data/smard_trade_fixed.tsv',
                            sep='\t', encoding='utf-8', index=True)

        df_trade = pd.read_csv(
            './data/smard_trade_fixed.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value > 714.032:
            title = 'Neuer Rekordwert beim Strom-Export nach Frankreich'
        else:
            title = 'Kein neuer Rekordwert beim Strom-Export nach Frankreich'

        # run Q function
        update_chart(id='03a56b0c1c7af72413d8325ae84d7c81',
                     title=title, notes=notes_chart, data=df_trade)

        """
        ################################
        # HISTORICAL POWER SINCE 2015  #
        ################################
        modules = REALIZED_POWER_GENERATION
        # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
        df = smard.requestSmardData(
            modulIDs=modules, timestamp_from_in_milliseconds=1420059600000)  # first week of 2021

        # check if data is corrupted
        errors = 0
        while ('Anfang' not in df.columns) and (errors < 5):
            sleep(2)
            errors += 1
            # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
            df = smard.requestSmardData(
                modulIDs=modules, timestamp_from_in_milliseconds=1420059600000)  # first week of 2021
        if ('Anfang' in df.columns):
            # fix wrong decimal
            df = df.replace('-', '', regex=False)
            df.to_csv('./data/smard_fixed.tsv', sep='\t',
                      encoding='utf-8', index=False)
            df = pd.read_csv('./data/smard_fixed.tsv', sep='\t', thousands='.', decimal=',',
                             index_col=None, dtype={'Datum': 'string', 'Anfang': 'string'})

            # drop time and convert dates
            df.drop('Anfang', axis=1, inplace=True)
            df.drop('Ende', axis=1, inplace=True)
            df['Datum'] = pd.to_datetime(df['Datum'], format="%d.%m.%Y")

            # old decimal fix
            #df.loc[:, df.columns != 'Datum'] = df.loc[:, df.columns != 'Datum'].replace('\,', '.', regex=True).astype(float)

            df = df.groupby(['Datum']).sum()

            # create new columns and drop the old ones
            df['Kernkraft'] = df['Kernenergie [MWh] Originalauflösungen']
            df['Fossile'] = df['Erdgas [MWh] Originalauflösungen'] + df['Braunkohle [MWh] Originalauflösungen'] + \
                df['Steinkohle [MWh] Originalauflösungen'] + \
                df['Sonstige Konventionelle [MWh] Originalauflösungen']
            df['Sonstige'] = df['Pumpspeicher [MWh] Originalauflösungen'] + df['Biomasse [MWh] Originalauflösungen'] + \
                df['Wasserkraft [MWh] Originalauflösungen'] + \
                df['Sonstige Erneuerbare [MWh] Originalauflösungen']
            df['Wind'] = df['Wind Offshore [MWh] Originalauflösungen'] + df['Wind Onshore [MWh] Originalauflösungen']
            df['Sonne'] = df['Photovoltaik [MWh] Originalauflösungen']
            df.drop(list(df)[0:12], axis=1, inplace=True)

            # convert to week and drop first and last row with partial values
            df.reset_index(inplace=True)
            df = df.resample('W', on='Datum').sum()
            # no drop for step-after chart
            df.drop(df.tail(1).index, inplace=True)
            df.drop(df.head(1).index, inplace=True)

            # save tsv
            df.to_csv('./data/smard_fixed_historical.tsv', sep='\t',
                      encoding='utf-8', index=True)

        # read tsv (old or new)
        df = pd.read_csv('./data/smard_fixed_historical.tsv',
                         sep='\t', index_col='Datum')
        df.index = pd.to_datetime(df.index)

        # get current date for chart notes
        time_dt_notes = df.index[-1] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Auf der Y-Achse: Stromerzeugung in absoluten Zahlen (TWh) gemäss EU-Transparenzverordnung; diese entsprachen im Jahr 2020 93 Prozent des insgesamt erzeugten Stroms.<br>Stand: {time_str_notes}'

        # drop unused rows and convert to terawatt
        df = df[~(df.index < '2021-07-18 00:00:00')]
        df = df.div(1000000)
        df.to_clipboard()
        """

    except:
        raise
