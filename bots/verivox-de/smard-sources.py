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

        def last_valid_value(list):
            nnlist = []
            for i in list:
                if(i != "-"):
                    nnlist.append(i)
            return float(nnlist[-1])

        modules = REALIZED_POWER_GENERATION

        # API request
        df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=(
            int(time.time()) * 1000) - (24*3600)*373000)  # 365000 = 1 year

        # check if data is corrupted
        errors = 0
        while ('Uhrzeit' not in df.columns) and (errors < 5):
            sleep(2)
            errors += 1
            df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=(
                int(time.time()) * 1000) - (24*3600)*373000)  # 365000 = 1 year
        else:
            # fix wrong decimal
            df.to_csv('./data/smard_fixed.csv', sep=';',
                      encoding='utf-8', index=False)
            df = pd.read_csv('./data/smard_fixed.csv', sep=';', thousands='.',
                             decimal=',', index_col=None, dtype={'Datum': 'string', 'Uhrzeit': 'string'})

            # drop time and convert dates to DatetimeIndex
            df.drop('Uhrzeit', axis=1, inplace=True)
            df['Datum'] = pd.to_datetime(df['Datum'], format="%d.%m.%Y")
            df = df.groupby(['Datum']).sum()

            # create new columns and drop the old ones
            df['Gas'] = df['Erdgas[MWh]']
            df['Kernkraft'] = df['Kernenergie[MWh]']
            df['Kohle'] = df['Braunkohle[MWh]'] + df['Steinkohle[MWh]']
            df['Sonstige'] = df['Pumpspeicher[MWh]'] + \
                df['Sonstige Konventionelle[MWh]']
            df['Erneuerbare'] = df['Biomasse[MWh]'] + df['Wasserkraft[MWh]'] + df['Wind Offshore[MWh]'] + \
                df['Wind Offshore[MWh]'] + df['Wind Onshore[MWh]'] + \
                df['Photovoltaik[MWh]'] + df['Sonstige Erneuerbare[MWh]']
            df.drop(list(df)[0:12], axis=1, inplace=True)

            # convert to week and drop first and last row with partial values
            df.reset_index(inplace=True)
            df = df.resample('W', on='Datum').sum()
            # no drop for step-after chart
            df.drop(df.tail(1).index, inplace=True)
            df.drop(df.head(1).index, inplace=True)

            # get current date for chart notes
            time_dt_notes = df.index[-1] + timedelta(days=1)
            time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
            notes_chart = f'Stand: {time_str_notes}'

            # calculate percentage for chart title
            df_perc = df.tail(1).div(df.tail(1).sum(axis=1), axis=0)
            perc_gas = (df_perc['Gas'].iloc[-1]*100).round(0).astype(int)
            if perc_gas > 1:
                title_chart = f'{perc_gas} Prozent des Stroms stammen derzeit aus Erdgas'
            else:
                title_chart = f'{perc_gas} Prozent des Stroms stammt derzeit aus Erdgas'

            # convert to terawatt
            df = df.div(1000000)

            # convert DatetimeIndex to string
            df.index = df.index.strftime('%Y-%m-%d')

            # run Q function
            update_chart(id='e468de3ac9c422bcd0924e26b60a2af8',
                         data=df, notes=notes_chart, title=title_chart)

    except:
        raise
