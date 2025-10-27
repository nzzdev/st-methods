import time
import pandas as pd
import os
from datetime import datetime, timedelta
from time import sleep
from datawrapper import Datawrapper
import numpy as np

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *
        import helpers_smard as smard

        # Datawrapper API key
        dw_key = os.environ['DATAWRAPPER_API']
        dw = Datawrapper(access_token=dw_key)
        dw_id = 'G2Vtz'  # Importe gesamt
        dw_id_fr = 'XJFzP'  # Importe Frankreich
        dw_id_ch = 'BjzEn'  # Importe Schweiz
        dw_id_nl = 'mOf7y'  # Importe Niederlande
        dw_id_emix = 'Mzofi'  # Strommix
        dw_source_all = 'https://www.smard.de/home/marktdaten?marketDataAttributes=%7B%22resolution%22:%22week%22,%22moduleIds%22:%5B22004629%5D,%22selectedCategory%22:null,%22activeChart%22:true,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D,%22region%22:%22DE%22%7D'
        dw_source_france = 'https://www.smard.de/home/marktdaten?marketDataAttributes=%7B%22resolution%22:%22week%22,%22moduleIds%22:%5B22004546,22004404%5D,%22selectedCategory%22:null,%22activeChart%22:true,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D,%22region%22:%22DE%22%7D'
        dw_source_ch = 'https://www.smard.de/home/marktdaten?marketDataAttributes=%7B%22resolution%22:%22week%22,%22moduleIds%22:%5B22004552,22004410%5D,%22selectedCategory%22:null,%22activeChart%22:true,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D,%22region%22:%22DE%22%7D'
        dw_source_nl = 'https://www.smard.de/home/marktdaten?marketDataAttributes=%7B%22resolution%22:%22week%22,%22moduleIds%22:%5B22004406,22004548%5D,%22selectedCategory%22:null,%22activeChart%22:true,%22style%22:%22color%22,%22categoriesModuleOrder%22:%7B%7D,%22region%22:%22DE%22%7D'

        # power generation
        REALIZED_POWER_GENERATION = [1001224, 1004066, 1004067, 1004068,
                                     1001223, 1004069, 1004071, 1004070, 1001226, 1001228, 1001227, 1001225]
        INSTALLED_POWER_GENERATION = [3004072, 3004073, 3004074, 3004075,
                                      3004076, 3000186, 3000188, 3000189, 3000194, 3000198, 3000207, 3003792]
        FORECASTED_POWER_GENERATION = [
            2000122, 2000715, 2000125, 2003791, 2000123]

        # power consumption
        FORECASTED_POWER_CONSUMPTION = [6000411, 6004362]
        REALIZED_POWER_CONSUMPTION = [5000410]
        REALIZED_POWER_CONSUMPTION_RESIDUAL = [5004359]

        # market
        WHOLESALE_PRICES = [8004169, 8004170, 8000252, 8000253, 8000251, 8000254,
                            8000255, 8000256, 8000257, 8000258, 8000259, 8000260, 8000261, 8000262]
        COMMERCIAL_FOREIGN_TRADE = [8004169, 8004170, 8000252, 8000253, 8000251, 8000254,
                                    8000255, 8000256, 8000257, 8000258, 8000259, 8000260, 8000261, 8000262]
        PHYSICAL_POWER_FLOW = [31000714, 31000140, 31000569, 31000145, 31000574, 31000570, 31000139, 31000568,
                               31000138, 31000567, 31000146, 31000575, 31000144, 31000573, 31000142, 31000571, 31000143, 31000572, 31000141]

        # commercial trade Germany/France
        COMMERCIAL_TRADE_FR = [22004546, 22004404]  # first import
        # commercial trade Germany/Netherlands
        COMMERCIAL_TRADE_NL = [22004548, 22004406]
        # commercial trade Germany/Belgium
        COMMERCIAL_TRADE_BE = [22004712, 22004998]
        # commercial trade Germany/Czechia
        COMMERCIAL_TRADE_CZ = [22004553, 22004412]
        # commercial trade Germany/Switzerland
        COMMERCIAL_TRADE_CH = [22004552, 22004410]
        # commercial trade Germany/Poland
        COMMERCIAL_TRADE_PL = [22004550, 22004408]
        # commercial trade Germany/Norway
        COMMERCIAL_TRADE_NO = [22004724, 22004722]
        # commercial trade Germany/Denmark
        COMMERCIAL_TRADE_DK = [22004545, 22004403]
        # commercial trade all countries
        COMMERCIAL_TRADE_ALL = [22004629]

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
        try:
            df = smard.requestSmardData(
                modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df.columns) and (errors < 3):
                sleep(2)
                errors += 1
                # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df.columns):
                # flag for incomplete-week check
                _incomplete_week_flag = False
                # fix wrong decimal
                df = df.replace('-', '', regex=False)
                df = df.rename(columns={'Datum von': 'Datum'})
                df.drop('Datum bis', axis=1, inplace=True)
                df.dropna(axis='columns', inplace=True)
                df.to_csv('./data/smard_fixed.tsv', sep='\t',
                          encoding='utf-8', index=False)
                df = pd.read_csv('./data/smard_fixed.tsv', sep='\t', thousands='.', decimal=',',
                                 index_col=None, dtype={'Datum': 'string'})
                # drop rows if there are at least three NaN values (one is always nuclear)
                df = df.dropna(thresh=len(df.columns) - 2)

                # convert dates
                df['Datum'] = pd.to_datetime(
                    df['Datum'], format="%d.%m.%Y %H:%M")

                # --- Incomplete-week check over previous (second-last) week; exclude nuclear ---
                # determine columns to evaluate (all except date and nuclear original column)
                _value_cols = [c for c in df.columns if c not in ['Datum', 'Kernenergie [MWh] Originalauflösungen']]
                # coerce to numeric; non-numeric/empties become NaN
                _df_num = df[_value_cols].apply(pd.to_numeric, errors='coerce')
                # identify weekly bins like resample('W') (weeks end on Sunday)
                _weekly_index_tmp = df.resample('W', on='Datum').sum().index
                if len(_weekly_index_tmp) >= 2:
                    _target_week_end = _weekly_index_tmp[-2]
                    _target_mask = df['Datum'].dt.to_period('W-SUN') == _target_week_end.to_period('W-SUN')
                else:
                    # fallback: use last available week if only one week present
                    _target_mask = df['Datum'].dt.to_period('W-SUN') == df['Datum'].dt.to_period('W-SUN').iloc[-1]
                # count non-numeric/empty entries per column within target week
                _non_numeric_counts = _df_num[_target_mask].isna().sum()
                # threshold strictly greater than 95 missing quarter-hours in any column triggers drop
                if (_non_numeric_counts > 95).any():
                    _incomplete_week_flag = True

                # old decimal fix
                #df.loc[:, df.columns != 'Datum'] = df.loc[:, df.columns != 'Datum'].replace('\,', '.', regex=True).astype(float)

                df = df.groupby(['Datum']).sum()

                # create new columns and drop the old ones
                df['Biomasse'] = df['Biomasse [MWh] Originalauflösungen']
                df['Kernkraft'] = df['Kernenergie [MWh] Originalauflösungen']
                df['Erdgas'] = df['Erdgas [MWh] Originalauflösungen']
                df['Pumpspeicher'] = df['Pumpspeicher [MWh] Originalauflösungen']
                df['Sonstige'] = df['Sonstige Konventionelle [MWh] Originalauflösungen']
                df['Kohle'] = df['Braunkohle [MWh] Originalauflösungen'] + \
                    df['Steinkohle [MWh] Originalauflösungen']
                df['Sonstige EE'] = df['Sonstige Erneuerbare [MWh] Originalauflösungen'] + \
                    df['Wasserkraft [MWh] Originalauflösungen']
                df['Wind'] = df['Wind Offshore [MWh] Originalauflösungen'] + \
                    df['Wind Onshore [MWh] Originalauflösungen']
                df['Sonne'] = df['Photovoltaik [MWh] Originalauflösungen']
                df.drop(list(df)[0:12], axis=1, inplace=True)
                df = df.drop(['Pumpspeicher'], axis=1)

                # convert to week and drop first and last row with partial values
                df.reset_index(inplace=True)
                df = df.resample('W', on='Datum').sum()

                # no drop for step-after chart
                df.drop(df.tail(1).index, inplace=True)
                df.drop(df.head(1).index, inplace=True)

                # drop last row if faulty data
                if df['Biomasse'].iloc[-1] < 200000.00:
                    df.drop(df.tail(1).index, inplace=True)
                # drop last row if previous week's data is incomplete across any column (excluding nuclear)
                if _incomplete_week_flag:
                    df.drop(df.tail(1).index, inplace=True)

                # save tsv
                df.to_csv('./data/smard_fixed.tsv', sep='\t',
                          encoding='utf-8', index=True)

        except:
            pass
        # read tsv (old or new)
        df = pd.read_csv('./data/smard_fixed.tsv', sep='\t', index_col='Datum')
        df.index = pd.to_datetime(df.index)

        # get current date for chart notes
        time_dt_notes = df.index[-1] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Auf der Y-Achse: Stromerzeugung in absoluten Zahlen (TWh) gemäss EU-Transparenzverordnung; diese entsprachen im Jahr 2020 93 Prozent des insgesamt erzeugten Stroms. Öl sowie andere Erneuerbare in der grafischen Darstellung unter «Sonstige», ohne Pumpspeicher. Nachmeldungen möglich.<br>Stand: {time_str_notes}'
        notes_chart_nogas = f'Auf der Y-Achse: Stromerzeugung in absoluten Zahlen (TWh) gemäss EU-Transparenzverordnung; diese entsprachen im Jahr 2020 93 Prozent des insgesamt erzeugten Stroms. Ohne Pumpspeicher. Nachmeldungen möglich.<br>Stand: {time_str_notes}'

        """
        # old gas chart title: calculate percentage for chart title
        df_perc = df.tail(1).div(df.tail(1).sum(axis=1), axis=0)
        perc_gas = (df_perc['Erdgas'].iloc[-1]*100).round(0).astype(int)
        if perc_gas > 1:
            title_chart = f'{perc_gas} Prozent des Stroms stammen derzeit aus Erdgas'
        else:
            title_chart = f'{perc_gas} Prozent des Stroms stammt derzeit aus Erdgas'
        """

        # calculate percentage for chart title
        _last = df.tail(1)
        df_perc = _last.div(_last.sum(axis=1), axis=0)
        perc_fossile = int(round(((df_perc['Erdgas'].iloc[-1] + df_perc['Kohle'].iloc[-1] + df_perc['Sonstige'].iloc[-1]) * 100), 0))

        # determine if last available week equals the immediately previous ISO week
        _today = pd.Timestamp.today().normalize()
        _start_this_week = _today - pd.Timedelta(days=_today.dayofweek)  # Monday of this week
        _end_prev_week = _start_this_week - pd.Timedelta(days=1)         # Sunday of previous week

        _row_ts = pd.to_datetime(_last.index[-1])
        _row_iso = _row_ts.isocalendar()
        _prev_iso = _end_prev_week.isocalendar()

        if (_row_iso.year == _prev_iso.year) and (_row_iso.week == _prev_iso.week):
            title_chart = (
                f'{perc_fossile} Prozent des Stroms stammten vergangene Woche aus fossilen Quellen'
                if perc_fossile > 1 else
                f'{perc_fossile} Prozent des Stroms stammte vergangene Woche aus fossilen Quellen'
            )
        else:
            title_chart = (
                f'{perc_fossile} Prozent des Stroms stammten in der KW {_row_iso.week:02d} aus fossilen Quellen'
                if perc_fossile > 1 else
                f'{perc_fossile} Prozent des Stroms stammte in der KW {_row_iso.week:02d} aus fossilen Quellen'
            )

        # calculate percentage for dashboard
        df_dash = df.div(df.sum(axis=1), axis=0)
        df_dash = (df_dash * 100).round(1)
        df_dash = df_dash[~(df_dash.index < '2020-12-27 00:00:00')]
        column_sum = ['Erdgas', 'Sonstige', 'Kohle']
        df_dash['Fossile Abhängigkeit'] = df_dash[column_sum].sum(axis=1)
        df_dash = df_dash[['Fossile Abhängigkeit']]

        # NEW fossile without gas
        # combine fossile
        df_nogas = df.copy()
        df_nogas['Erdgas'] = df_nogas['Erdgas'] + \
            df_nogas['Kohle'] + df_nogas['Sonstige']  # fossile
        df_nogas = df_nogas.drop(['Sonstige', 'Kohle'], axis=1)
        df_nogas = df_nogas.rename(columns={'Erdgas': 'Fossile',
                                            'Sonstige EE': 'Sonstige'})
        # drop unused rows and convert to terawatt
        df_nogas = df_nogas[~(df_nogas.index < '2023-01-01 00:00:00')] # old: 2021-12-12, always pick sunday of last week
        df_nogas = df_nogas.div(1000000)

        # OLD fossile with gas
        # combine conventional
        df['Sonstige'] = df['Sonstige'] + df['Sonstige EE']
        df = df.drop(['Sonstige EE'], axis=1)
        # drop unused rows and convert to terawatt
        df = df[~(df.index < '2023-01-01 00:00:00')] # old: 2021-12-12, always pick sunday of last week
        df = df.div(1000000)

        df_dash.to_csv('./data/smard_percentage.csv')

        # convert DatetimeIndex to string
        # df.index = df.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(id='e468de3ac9c422bcd0924e26b60a2af8',
                     data=df, notes=notes_chart, title=title_chart)
        update_chart(id='377d6a0926cf5246344267f1b9db9dc3',
                     data=df_nogas, notes=notes_chart_nogas, title=title_chart)

        # update Datawrapper chart
        df_nogas.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id_emix, data=df_nogas)
        dw.update_chart(chart_id=dw_id_emix, title=title_chart)
        date = {'annotate': {
            'notes': f'Auf der Y-Achse: Stromerzeugung in absoluten Zahlen (TWh) gemäss EU-Transparenzverordnung; diese entsprachen im Jahr 2020 93 Prozent des insgesamt erzeugten Stroms. Ohne Pumpspeicher. Nachmeldungen möglich.<br>Stand: {time_str_notes}'}}
        dw.update_metadata(chart_id=dw_id_emix, metadata=date)
        dw.update_description(
            chart_id=dw_id_emix, source_url='https://www.smard.de/home/downloadcenter/download-marktdaten/', source_name='Bundesnetzagentur/Entso-E', intro='Stromerzeugung in Deutschland, in TWh<br><span style="line-height:40px"><span style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; padding:1px 6px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px"><b>Wöchentlich</b></span> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/rcnPY/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; padding:1px 6px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Monatlich</a></span>')
        dw.publish_chart(chart_id=dw_id_emix, display=False)

        #################################
        # API request power consumption #
        #################################
        modules = REALIZED_POWER_CONSUMPTION
        try:
            df = smard.requestSmardData(
                modulIDs=modules, timestamp_from_in_milliseconds=1672520400000)  # last day of 2022

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df.columns) and (errors < 3):
                sleep(2)
                errors += 1
            if ('Datum bis' in df.columns):
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1672520400000)  # last day of 2022
                # fix wrong decimal
                df = df.replace('-', '', regex=False)
                df = df.rename(columns={'Datum von': 'Datum'})
                df.drop('Datum bis', axis=1, inplace=True)
                df.to_csv('./data/power_consumption.tsv',
                          sep='\t', encoding='utf-8', index=False)
                df = pd.read_csv('./data/power_consumption.tsv', sep='\t', thousands='.',
                                 decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df['Datum'] = pd.to_datetime(
                    df['Datum'], format="%d.%m.%Y %H:%M")

                df = df.groupby(['Datum']).sum()

                # convert to week and drop first and last row with partial values
                df.reset_index(inplace=True)
                df = df.resample('W', on='Datum').sum()
                # no drop for step-after chart
                df.drop(df.tail(1).index, inplace=True)
                df.drop(df.head(1).index, inplace=True)

                # save tsv
                df.to_csv('./data/power_consumption.tsv', sep='\t',
                          encoding='utf-8', index=True)

        except:
            pass

        ###########################
        # API request spot market #
        ###########################
        modules = SPOT_MARKET
        try:
            df_spot = smard.requestSmardData(
                modulIDs=modules, region="DE-LU", timestamp_from_in_milliseconds=1608764400000)  # 160815600000 for 14-day avg

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_spot.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df_spot = smard.requestSmardData(
                    modulIDs=modules, region="DE-LU", timestamp_from_in_milliseconds=1608764400000)  # 160815600000 for 14-day avg
            if ('Datum bis' in df_spot.columns):
                # fix wrong decimal
                df_spot = df_spot.replace('-', '', regex=False)
                df_spot = df_spot.rename(columns={'Datum von': 'Datum'})
                df_spot.drop('Datum bis', axis=1, inplace=True)
                df_spot.to_csv('./data/smard_spot.tsv', sep='\t',
                               encoding='utf-8', index=False)
                df_spot = pd.read_csv('./data/smard_spot.tsv', sep='\t', thousands='.', decimal=',',
                                      index_col=None, dtype={'Datum': 'string'})

                # save current price as csv for dashboard
                df_spot_today = df_spot.copy()
                df_spot_today['Datum'] = pd.to_datetime(
                    df_spot_today['Datum'], format='%d.%m.%Y %H:%M', dayfirst=True)
                """
                # irrelevant with new API
                # combine the date column and hour column to create a new datetime column
                df_spot_today['Datum'] = df_spot_today['Datum'].dt.strftime(
                    '%Y-%m-%d')
                df_spot_today['Datum'] = pd.to_datetime(
                    df_spot_today['Datum'] + ' ' + df_spot_today['Datum bis'])
                # drop unused columns
                df_spot_today.drop('Datum bis', axis=1, inplace=True)
                """
                df_spot_today = df_spot_today.rename(
                    columns={df_spot_today.columns[1]: 'Strom-Börsenpreis'})
                df_spot_today.reset_index(drop=True, inplace=True)
                # find the most current time
                most_current_time = df_spot_today['Datum'].max()
                # find the corresponding time from yesterday
                yesterday_time = most_current_time - pd.DateOffset(days=1)
                # create a boolean mask to filter rows
                mask = (df_spot_today['Datum'] == most_current_time) | (
                    df_spot_today['Datum'] == yesterday_time)
                # use the mask to filter the DataFrame
                df_spot_today = df_spot_today[mask]
                df_spot_today.set_index('Datum', inplace=True)
                df_spot_today.to_csv(
                    './data/smard_spot_current.csv', encoding='utf-8')

                # drop time and convert dates to DatetimeIndex
                df_spot['Datum'] = pd.to_datetime(
                    df_spot['Datum'], format="%d.%m.%Y %H:%M")

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
        except:
            pass
        # read tsv (old or new)
        df_spot = pd.read_csv('./data/smard_spot.tsv',
                              sep='\t', index_col='Datum')
        df_spot.index = pd.to_datetime(df_spot.index)

        # get current date
        q_date = df_spot.last_valid_index()
        notes_chart = '¹ Marktgebiet Deutschland/Luxemburg; gewichteter Day-Ahead-Preis des vortägigen Stromhandels.<br>Stand: ' + \
            q_date.strftime("%-d. %-m. %Y")
        notes_chart_compare = '¹ Marktgebiet Deutschland/Luxemburg; gewichteter Day-Ahead-Preis des vortägigen Stromhandels.<br>² Durchschnitt 2019-2020.<br>Stand: ' + \
            q_date.strftime("%-d. %-m. %Y")

        # drop unused dates
        #df_spot = df_spot[df_spot.any(1)]
        df_spot = df_spot['2021-01-01': q_date]
        df_spot = df_spot[df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'].notna()]
        df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'] = df_spot['Deutschland/Luxemburg [€/MWh] Originalauflösungen'].astype(
            int)

        # create dataframe for chart with crisis and pre-crisis level
        df_spot_old = pd.read_csv(
            './data/smard_spot_historical.tsv', sep='\t', index_col=None)
        df_spot_old['Datum'] = pd.to_datetime(df_spot_old['Datum'])
        yesterday_year = datetime.now() - timedelta(days=1)
        year = yesterday_year.year
        df_spot_new = df_spot.copy()[df_spot.index >= f'{year}-01-01']
        df_spot_new = df_spot_new.rename(
            columns={f'Deutschland/Luxemburg [€/MWh] Originalauflösungen': f'{year}'})
        df_spot_new = df_spot_new.reset_index()
        df_spot_compare = df_spot_old.merge(
            df_spot_new, on='Datum', how='left')  # int will be float due to NaN
        df_spot_compare = df_spot_compare[[
            'Datum', f'{year}', '2022', 'Vorkrisenniveau²']]
        df_spot_compare.set_index('Datum', inplace=True)
        # get pre-crisis value
        mwh_new = df_spot_compare[f'{year}'].loc[df_spot_compare[f'{year}'].last_valid_index(
        )]
        mwh_new_pos = df_spot_compare[f'{year}'].index.get_loc(
            df_spot_compare[f'{year}'].last_valid_index())
        mwh_old = df_spot_compare.iloc[mwh_new_pos]['Vorkrisenniveau²']
        title_mwh_diff = round((mwh_new - mwh_old), 0).astype(int)
        title_mwh = round(mwh_new, 0).astype(int)
        df_spot_compare[f'{year}'] = df_spot_compare[f'{year}'].fillna('')

        # dynamic chart title
        title_old = f'Strom kostet am Spotmarkt im Schnitt {title_mwh} Euro je MWh'
        if title_mwh_diff > 0:
            title = f'Strom kostet am Spotmarkt im Schnitt {title_mwh} Euro je MWh – {title_mwh_diff} Euro mehr als vor der Krise'
        elif title_mwh_diff == 0:
            title = f'Strom kostet am Spotmarkt im Schnitt {title_mwh} Euro je MWh – so viel wie vor der Krise'
        else:
            title = f'Strom kostet am Spotmarkt im Schnitt {title_mwh} Euro je MWh – {abs(title_mwh_diff)} Euro weniger als vor der Krise'

        # run Q function
        update_chart(id='90005812afc9964bbfe4f952f51d6a57',
                     title=title_old, notes=notes_chart, data=df_spot)
        # run Q function
        update_chart(id='cc0c892a4433991f1c77c35df8beaff3',
                     title=title, notes=notes_chart_compare, data=df_spot_compare)

        ################
        # TRADE FRANCE #
        ################

        modules = COMMERCIAL_TRADE_FR
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_fr.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_fr.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

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
                df_trade.to_csv('./data/smard_trade_fixed_fr.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_fr.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        """
        # old dynamic chart title with peak comparison
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value > 714.032:
            title = 'Neuer Rekordwert beim Strom-Export nach Frankreich'
        else:
            title = 'Kein neuer Rekordwert beim Strom-Export nach Frankreich'
        """

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom nach Frankreich als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus Frankreich als umgekehrt'

        # run Q function
        #update_chart(id='03a56b0c1c7af72413d8325ae84d7c81', title=title, notes=notes_chart, data=df_trade)

        # update Datawrapper chart
        df_trade.drop(df_trade.tail(1).index, inplace=True)
        df_trade.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id_fr, data=df_trade)
        dw.update_chart(chart_id=dw_id_fr, title=title)
        date = {'annotate': {
            'notes': f'Negative Werte in Rot bedeuten Importe, positive Werte in Blau Exporte. Nachmeldungen möglich.<br><br>Stand: {time_str_notes}'}}
        dw.update_metadata(chart_id=dw_id_fr, metadata=date)
        dw.update_description(
            chart_id=dw_id_fr, source_url=dw_source_france, source_name='Bundesnetzagentur/Entso-E', intro='Wöchentlicher grenzüberschreitender Stromhandel Deutschlands (Export-Import-Saldo), in GWh<br><span style="line-height:40px"><a target="_self" href="https://datawrapper.dwcdn.net/G2Vtz/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Gesamt</a> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/XJFzP/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px"><b>Frankreich</b></a> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/BjzEn/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Schweiz</a></span>')
        dw.publish_chart(chart_id=dw_id_fr, display=False)

        """
        #################
        # TRADE BELGIUM #
        #################

        modules = COMMERCIAL_TRADE_BE
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_be.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_be.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # calculate net electricity exports
                df_trade['Saldo'] = df_trade['Belgien (Export) [MWh] Originalauflösungen'] - \
                    abs(df_trade['Belgien (Import) [MWh] Originalauflösungen'])

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Saldo'].div(1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_be.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_be.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom nach Belgien als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus Belgien als umgekehrt'

        # run Q function
        update_chart(id='12496a04992590f16cb3aaa749aea0a4',
                     title=title, notes=notes_chart, data=df_trade)

        """
        #####################
        # TRADE NETHERLANDS #
        #####################

        modules = COMMERCIAL_TRADE_NL
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_nl.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_nl.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # calculate net electricity exports
                df_trade['Saldo'] = df_trade['Niederlande (Export) [MWh] Originalauflösungen'] - \
                    abs(df_trade['Niederlande (Import) [MWh] Originalauflösungen'])

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Saldo'].div(1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_nl.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_nl.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom in die Niederlande als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus den Niederlanden als umgekehrt'

        # run Q function
        #update_chart(id='5135d71baf12ad518000453bad2d0416', title=title, notes=notes_chart, data=df_trade)

        # update Datawrapper chart
        df_trade.drop(df_trade.tail(1).index, inplace=True)
        df_trade.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id_nl, data=df_trade)
        dw.update_chart(chart_id=dw_id_nl, title=title)
        date = {'annotate': {
            'notes': f'Negative Werte in Rot bedeuten Importe, positive Werte in Blau Exporte. Nachmeldungen möglich.<br><br>Stand: {time_str_notes}'}}
        dw.update_metadata(chart_id=dw_id_nl, metadata=date)
        dw.update_description(
            chart_id=dw_id_nl, source_url=dw_source_nl, source_name='Bundesnetzagentur/Entso-E', intro='Wöchentlicher grenzüberschreitender Stromhandel Deutschlands (Export-Import-Saldo), in GWh<br><span style="line-height:40px"><a target="_self" href="https://datawrapper.dwcdn.net/G2Vtz/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Gesamt</a> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/XJFzP/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Frankreich</a> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/BjzEn/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Schweiz</a> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/mOf7y/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px"><b>Niederlande</b></a></span>')
        dw.publish_chart(chart_id=dw_id_nl, display=False)

        """
        #################
        # TRADE CZECHIA #
        #################

        modules = COMMERCIAL_TRADE_CZ
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_cz.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_cz.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # calculate net electricity exports
                df_trade['Saldo'] = df_trade['Tschechien (Export) [MWh] Originalauflösungen'] - \
                    abs(df_trade['Tschechien (Import) [MWh] Originalauflösungen'])

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Saldo'].div(1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_cz.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_cz.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom nach Tschechien als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus Tschechien als umgekehrt'

        # run Q function
        update_chart(id='12496a04992590f16cb3aaa749aea20c',
                     title=title, notes=notes_chart, data=df_trade)

        ################
        # TRADE NORWAY #
        ################

        modules = COMMERCIAL_TRADE_NO
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_no.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_no.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # calculate net electricity exports
                df_trade['Saldo'] = df_trade['Norwegen (Export) [MWh] Originalauflösungen'] - \
                    abs(df_trade['Norwegen (Import) [MWh] Originalauflösungen'])

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Saldo'].div(1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_no.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_no.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom nach Norwegen als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus Norwegen als umgekehrt'

        # run Q function
        update_chart(id='12496a04992590f16cb3aaa749b045bb',
                     title=title, notes=notes_chart, data=df_trade)
        """
        ###############
        # TRADE SWISS #
        ###############

        modules = COMMERCIAL_TRADE_CH
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_ch.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_ch.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # calculate net electricity exports
                df_trade['Saldo'] = df_trade['Schweiz (Export) [MWh] Originalauflösungen'] - \
                    abs(df_trade['Schweiz (Import) [MWh] Originalauflösungen'])

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Saldo'].div(1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_ch.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_ch.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom in die Schweiz als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus der Schweiz als umgekehrt'

        # run Q function
        #update_chart(id='5135d71baf12ad518000453bad2ea7af', title=title, notes=notes_chart, data=df_trade)

        # update Datawrapper chart
        df_trade.drop(df_trade.tail(1).index, inplace=True)
        df_trade.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id_ch, data=df_trade)
        dw.update_chart(chart_id=dw_id_ch, title=title)
        date = {'annotate': {
            'notes': f'Negative Werte in Rot bedeuten Importe, positive Werte in Blau Exporte. Nachmeldungen möglich.<br><br>Stand: {time_str_notes}'}}
        dw.update_metadata(chart_id=dw_id_fr, metadata=date)
        dw.update_description(
            chart_id=dw_id_ch, source_url=dw_source_ch, source_name='Bundesnetzagentur/Entso-E', intro='Wöchentlicher grenzüberschreitender Stromhandel Deutschlands (Export-Import-Saldo), in GWh<br><span style="line-height:40px"><a target="_self" href="https://datawrapper.dwcdn.net/G2Vtz/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Gesamt</a> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/XJFzP/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Frankreich</a> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/BjzEn/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px"><b>Schweiz</b></a></span>')
        dw.publish_chart(chart_id=dw_id_ch, display=False)

        """
        ################
        # TRADE POLAND #
        ################

        modules = COMMERCIAL_TRADE_PL
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_pl.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_pl.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # calculate net electricity exports
                df_trade['Saldo'] = df_trade['Polen (Export) [MWh] Originalauflösungen'] - \
                    abs(df_trade['Polen (Import) [MWh] Originalauflösungen'])

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Saldo'].div(1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_pl.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_pl.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom nach Polen als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus Polen als umgekehrt'

        # run Q function
        update_chart(id='5135d71baf12ad518000453bad2ea91b',
                     title=title, notes=notes_chart, data=df_trade)

        #################
        # TRADE DENMARK #
        #################

        modules = COMMERCIAL_TRADE_DK
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_dk.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_dk.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # calculate net electricity exports
                df_trade['Saldo'] = df_trade['Dänemark (Export) [MWh] Originalauflösungen'] - \
                    abs(df_trade['Dänemark (Import) [MWh] Originalauflösungen'])

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Saldo'].div(1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_dk.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_dk.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom nach Dänemark als umgekehrt'
        else:
            title = 'Deutschland importiert derzeit mehr Strom aus Dänemark als umgekehrt'

        # run Q function
        update_chart(id='12496a04992590f16cb3aaa749b04fb0',
                     title=title, notes=notes_chart, data=df_trade)
        """

        #############
        # TRADE ALL #
        #############

        modules = COMMERCIAL_TRADE_ALL
        try:
            df_trade = smard.requestSmardData(
                modulIDs=modules, region="DE", timestamp_from_in_milliseconds=1609095600000)  # last week of 2020

            # check if data is corrupted
            errors = 0
            while ('Datum bis' not in df_trade.columns) and (errors < 3):
                sleep(2)
                errors += 1
                df = smard.requestSmardData(
                    modulIDs=modules, timestamp_from_in_milliseconds=1609095600000)  # last week of 2020
            if ('Datum bis' in df_trade.columns):
                # fix wrong decimal
                df_trade = df_trade.replace('-', '', regex=False)
                df_trade = df_trade.rename(columns={'Datum von': 'Datum'})
                df_trade.drop('Datum bis', axis=1, inplace=True)
                df_trade.to_csv('./data/smard_trade_fixed_all.tsv',
                                sep='\t', encoding='utf-8', index=False)
                df_trade = pd.read_csv('./data/smard_trade_fixed_all.tsv', sep='\t', thousands='.',
                                       decimal=',', index_col=None, dtype={'Datum': 'string'})

                # convert dates
                df_trade['Datum'] = pd.to_datetime(
                    df_trade['Datum'], format="%d.%m.%Y %H:%M")

                # --- Incomplete-week check (TRADE ALL): evaluate 'Nettoexport [MWh] Originalauflösungen' only ---
                _incomplete_week_trade_all = False
                _series_num = pd.to_numeric(df_trade['Nettoexport [MWh] Originalauflösungen'], errors='coerce')
                _weekly_index_tmp_tr_all = df_trade.resample('W', on='Datum').sum().index
                if len(_weekly_index_tmp_tr_all) >= 2:
                    _target_week_end_tr_all = _weekly_index_tmp_tr_all[-2]
                    _target_mask_tr_all = df_trade['Datum'].dt.to_period('W-SUN') == _target_week_end_tr_all.to_period('W-SUN')
                else:
                    # fallback: use last available week if only one week present
                    _target_mask_tr_all = df_trade['Datum'].dt.to_period('W-SUN') == df_trade['Datum'].dt.to_period('W-SUN').iloc[-1]
                _non_numeric_count_tr_all = _series_num[_target_mask_tr_all].isna().sum()
                if _non_numeric_count_tr_all > 95:
                    _incomplete_week_trade_all = True

                # convert to gigawatt
                df_trade['Saldo'] = df_trade['Nettoexport [MWh] Originalauflösungen'].div(
                    1000)
                df_trade = df_trade[['Datum', 'Saldo']]

                # convert to week and drop first row with partial values
                df_trade = df_trade.resample('W', on='Datum').sum()
                df_trade.drop(df_trade.head(1).index, inplace=True)
                #df_trade.drop(df_trade.tail(1).index, inplace=True)

                # drop second-last row if previous week's data is incomplete (preserve last placeholder week)
                if _incomplete_week_trade_all and len(df_trade.index) >= 2:
                    df_trade.drop(df_trade.index[-2], inplace=True)

                # update last row for step-after chart (avoid constant commits)
                df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0

                # save tsv
                df_trade.to_csv('./data/smard_trade_fixed_all.tsv',
                                sep='\t', encoding='utf-8', index=True)
        except:
            pass
        df_trade = pd.read_csv(
            './data/smard_trade_fixed_all.tsv', sep='\t', index_col='Datum')
        df_trade.index = pd.to_datetime(df_trade.index)

        # run Q function
        #update_chart(id='12496a04992590f16cb3aaa749b3b7b4', title=title, notes=notes_chart, data=df_trade)

        """
        # temp fix for last row (if energy-charts has newer data)
        df_trade.at[df_trade.index[-1], 'Saldo'] = -898.0
        d = datetime.today()
        time_str_notes = d - timedelta(days=d.weekday())  # last monday
        time_str_notes = time_str_notes.strftime('%-d. %-m. %Y')
        """

        # Read the imports-countries-dash.csv file
        df_imports = pd.read_csv('./data/imports-countries-dash.csv', sep=',', index_col=None)

        # Ensure that the 'date' column in df_imports is consistent
        # The 'date' format is assumed to be like 'KW 45' where 'KW' stands for 'Kalenderwoche' (calendar week)
        # Extract the week number from the 'date' column
        df_imports['KW'] = df_imports['date'].str.extract(r'KW\s?(\d+)', expand=False).astype(int)

        # Get the last entry from df_imports
        last_import_week = df_imports['KW'].iloc[-1]
        last_import_value = df_imports['value'].iloc[-1]

        # Get the last date from df_trade and extract the calendar week number
        last_trade_date = df_trade.index[-2]
        last_trade_week = last_trade_date.isocalendar()[1]

        # Check if the weeks match
        if last_trade_week == last_import_week:
            # Replace the 'Saldo' value in df_trade with the 'value' from df_imports
            df_trade.at[df_trade.index[-2], 'Saldo'] = last_import_value
            print(f"Replaced last 'Saldo' value in df_trade with {last_import_value} from imports-countries-dash.csv")
        else:
            print("The last week in df_trade and imports-countries-dash.csv do not match. No replacement made.")

        # update last row for step-after chart (avoid constant commits)
        df_trade.at[df_trade.index[-1], 'Saldo'] = 0.0
        # Align saved trade weeks to consumption weeks (robust share calc) and drop placeholder week
        try:
            _cons = pd.read_csv('./data/power_consumption.tsv', sep='\t', index_col='Datum')
            _cons.index = pd.to_datetime(_cons.index)
            _common = df_trade.index.intersection(_cons.index)
            if len(_common) > 0:
                _to_save = df_trade.loc[_common]
            else:
                _to_save = df_trade.drop(df_trade.tail(1).index)
        except Exception:
            _to_save = df_trade.drop(df_trade.tail(1).index)
        _to_save.to_csv('./data/smard_trade_fixed_all.tsv', sep='\t', encoding='utf-8', index=True)

        # get current date for chart notes
        time_dt_notes = df_trade.index[-2] + timedelta(days=1)
        time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
        notes_chart = f'Stand: {time_str_notes}'

        # dynamic chart title
        last_value = df_trade['Saldo'].iloc[-2]
        if last_value >= 0:
            title = 'Deutschland exportiert derzeit mehr Strom, als es importiert'
        else:
            title = 'Deutschland importiert derzeit mehr Strom, als es exportiert'

        # Remove latest week
        df_trade.drop(df_trade.tail(1).index, inplace=True)
        df_trade.reset_index(inplace=True)

        # update Datawrapper chart
        dw_chart = dw.add_data(chart_id=dw_id, data=df_trade)
        dw.update_chart(chart_id=dw_id, title=title)
        date = {'annotate': {
            'notes': f'Negative Werte in Rot bedeuten Importe, positive Werte in Blau Exporte. Nachmeldungen möglich.<br><br>Stand: {time_str_notes}'}}
        dw.update_metadata(chart_id=dw_id, metadata=date)
        dw.update_description(
            chart_id=dw_id, source_url=dw_source_all, source_name='Bundesnetzagentur/Entso-E', intro='Grenzüberschreitender Stromhandel Deutschlands (Export-Import-Saldo), in GWh<br><span style="line-height:40px"><span style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; outline: none;opacity: 1; text-decoration: none;padding:1px 6px"><b>Wöchentlich</b></span> &nbsp;<a target="_self" href="https://datawrapper.dwcdn.net/UbT7x/" style="background:#fff; color: #000; border: 1px solid #d4d6dd;box-shadow: 0 1px 3px 0 rgba(0,0,0,.05); border-radius: 0px; font-weight:400; cursor:pointer; outline: none;opacity: 1; text-decoration: none;padding:1px 6px">Monatlich</a></span>')
        dw.publish_chart(chart_id=dw_id, display=False)

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
        while ('Datum bis' not in df.columns) and (errors < 3):
            sleep(2)
            errors += 1
            # df = smard.requestSmardData(modulIDs=modules, timestamp_from_in_milliseconds=1625954400000)  # int(time.time()) * 1000) - (24*3600)*373000  = 1 year + last week
            df = smard.requestSmardData(
                modulIDs=modules, timestamp_from_in_milliseconds=1420059600000)  # first week of 2021
        if ('Datum bis' in df.columns):
            # fix wrong decimal
            df = df.replace('-', '', regex=False)
            df = df.rename(columns={'Datum von': 'Datum'})
            df.drop('Datum bis', axis=1, inplace=True)
            df.to_csv('./data/smard_fixed.tsv', sep='\t',
                      encoding='utf-8', index=False)
            df = pd.read_csv('./data/smard_fixed.tsv', sep='\t', thousands='.', decimal=',',
                             index_col=None, dtype={'Datum': 'string'})

            # convert dates
            df['Datum'] = pd.to_datetime(df['Datum'], format="%d.%m.%Y %H:%M")

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
