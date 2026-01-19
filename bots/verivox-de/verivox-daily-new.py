import os
from datetime import timedelta
import json
import pandas as pd
import geopandas as gpd
import numpy as np
import subprocess
import snowflake.connector


def update_chart(id, title="", subtitle="", notes="", data="", files="", options=""):  # Q helper function
    # read qConfig file
    json_file = open('./q.config.json')
    qConfig = json.load(json_file)
    # update chart properties
    for item in qConfig.get('items'):
        for environment in item.get('environments'):
            if environment.get('id') == id:
                if title != '':
                    item.get('item').update({'title': title})
                if subtitle != '':
                    item.get('item').update({'subtitle': subtitle})
                if notes != '':
                    item.get('item').update({'notes': notes})
                if len(data) > 0:
                    item['item']['data'] = data
                if len(files) > 0:
                    item['item']['files'] = files
                print('Successfully updated item with id', id,
                      'on', environment.get('name'), 'environment')
                if options != '':
                    item.get('item').update({'options': options})

    # write qConfig file
    with open('./q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False,
                  indent=1, default=str)
    json_file.close()


if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        user_env = os.environ['VERIVOX_SNOWFLAKE_USER']
        acc_env = os.environ['VERIVOX_SNOWFLAKE_ACC'] # xy.eu-central-1
        private_key_file = os.environ['VERIVOX_SNOWFLAKE_KEY'] # path to private key
        # private_key_file = 'private_key.pem'
        private_key_file_pwd = os.environ.get('VERIVOX_SNOWFLAKE_KEY_PASS', '')

        con = snowflake.connector.connect(
            user=user_env,
            account=acc_env,
            private_key_file=private_key_file,
            private_key_file_pwd=private_key_file_pwd,
            warehouse='COMPUTE_WH',
            database='PRESS',
            schema='PRESS_PARTNERS'
        )

        cur = con.cursor()

        # execute a statement that will generate a result set
        cur.execute("USE ROLE PRESS_ROLE")
        cur.execute("SELECT * FROM ELECTRICITY_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS WHERE \"Datum\" = (SELECT MAX(\"Datum\") FROM ELECTRICITY_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS) ORDER BY \"Postleitzahl\", \"Ort\", \"Ortsteil\" ") # current data
        #cur.execute("SELECT * FROM ELECTRICITY_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS WHERE \"Datum\" = (SELECT DATEADD(DAY, -7, MAX(\"Datum\")) FROM ELECTRICITY_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS) ORDER BY \"Postleitzahl\", \"Ort\", \"Ortsteil\" ") # old data


        # fetch the result set from the cursor and deliver as pandas dataframe
        df = cur.fetch_pandas_all()
        df.to_csv('./data/newest_electricity_data.csv')

        cur.execute("SELECT * FROM GAS_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS WHERE \"Datum\" = (SELECT MAX(\"Datum\") FROM GAS_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS) ORDER BY \"Postleitzahl\", \"Ort\", \"Ortsteil\" ") # current data
        #cur.execute("SELECT * FROM GAS_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS WHERE \"Datum\" = (SELECT DATEADD(DAY, -7, MAX(\"Datum\")) FROM GAS_PRICE_GUARANTEE_12_MONTHS_WITHOUT_BONUS) ORDER BY \"Postleitzahl\", \"Ort\", \"Ortsteil\" ") # old data
        df = cur.fetch_pandas_all()
        df.to_csv('./data/newest_gas_data.csv')

        # read csv files and geojson as dataframe
        dfac = pd.read_csv('./data/newest_electricity_data.csv', index_col=None, usecols=[
                           'Postleitzahl', 'Anzahl Haushalte', 'Gesamtkosten (brutto) in EUR pro Jahr (ohne Boni)', 'Datum'], dtype={'Postleitzahl': 'string'})
        dfgas = pd.read_csv('./data/newest_gas_data.csv', index_col=None, usecols=[
                            'Postleitzahl', 'Anzahl Haushalte', 'Gesamtkosten (brutto) in EUR pro Jahr (ohne Boni)', 'Datum'], dtype={'Postleitzahl': 'string'})
        df21 = pd.read_csv('./data/gas-strom-1120.tsv',
                           sep='\t', index_col=None, dtype={'id': 'string'})
        dfavg = pd.read_csv(
            './data/gas-strom-bundesschnitt.tsv', sep='\t', index_col=None)
        dfpop = pd.read_csv('./data/plz_einwohner.tsv',
                            sep='\t', index_col=None, dtype={'plz': 'string'})

        # normalize PLZ/population lookup and build an interpolator for missing PLZs
        dfpop['plz'] = dfpop['plz'].astype('string').str.strip()
        if 'einwohner' in dfpop.columns:
            dfpop['einwohner'] = pd.to_numeric(dfpop['einwohner'], errors='coerce')
        else:
            raise ValueError("plz_einwohner.tsv must contain a column named 'einwohner'")

        # numeric PLZ for interpolation (keep original string for exact matches)
        dfpop['plz_int'] = pd.to_numeric(dfpop['plz'], errors='coerce')
        dfpop = dfpop.dropna(subset=['plz_int', 'einwohner']).copy()
        dfpop['plz_int'] = dfpop['plz_int'].astype(int)
        dfpop = dfpop.sort_values('plz_int')

        _plz_ints = dfpop['plz_int'].to_numpy()
        _pops = dfpop['einwohner'].to_numpy()

        def _pop_for_plz(plz_str: str):
            """Return population for PLZ.
            - exact match if present in dfpop
            - otherwise linear interpolation between nearest lower/upper PLZ by numeric code
            - if only one neighbor exists, fall back to that neighbor
            """
            if plz_str is None:
                return np.nan
            plz_str = str(plz_str).strip()

            exact = dfpop.loc[dfpop['plz'] == plz_str, 'einwohner']
            if not exact.empty:
                return float(exact.iloc[0])

            try:
                plz_int = int(plz_str)
            except ValueError:
                return np.nan

            # find insertion position
            pos = np.searchsorted(_plz_ints, plz_int)

            # lower and upper neighbors
            lower_idx = pos - 1
            upper_idx = pos

            has_lower = lower_idx >= 0
            has_upper = upper_idx < len(_plz_ints)

            if has_lower and has_upper:
                x0, y0 = _plz_ints[lower_idx], _pops[lower_idx]
                x1, y1 = _plz_ints[upper_idx], _pops[upper_idx]
                if x1 == x0:
                    return float(y0)
                # linear interpolation
                return float(y0 + (y1 - y0) * (plz_int - x0) / (x1 - x0))
            if has_lower:
                return float(_pops[lower_idx])
            if has_upper:
                return float(_pops[upper_idx])
            return np.nan

        # GeoJSON with postal codes
        gdf = gpd.read_file('./data/plz_vereinfacht_1.5-min.json')

        dfac['Datum'] = pd.to_datetime(dfac['Datum'])
        dfgas['Datum'] = pd.to_datetime(dfgas['Datum'])

        # Snapshot date for the PLZ map/card must reflect the newest Snowflake delivery,
        # not the bundled national time series (dfavg).
        snapshot_dt = max(pd.Timestamp(dfac['Datum'].max()), pd.Timestamp(dfgas['Datum'].max()))
        snapshot_dt = snapshot_dt.normalize()
        time_dt = snapshot_dt.to_pydatetime()
        time_str = snapshot_dt.strftime('%Y-%m-%d %H:%M:%SZ')
        time_str_notes = snapshot_dt.strftime('%-d.\u2009%-m.\u2009%Y')

        # dfavg is only for the national-series chart; keep it sorted for later.
        dfavg['date'] = pd.to_datetime(dfavg['date'])
        dfavg = dfavg.sort_values('date').reset_index(drop=True)

        # rename column headers
        dfac.rename(columns={'Postleitzahl': 'id', 'Anzahl Haushalte': 'hh',
                             'Gesamtkosten (brutto) in EUR pro Jahr (ohne Boni)': 'strom', 'Datum': 'datum'}, inplace=True)
        dfgas.rename(columns={'Postleitzahl': 'id', 'Anzahl Haushalte': 'hh',
                              'Gesamtkosten (brutto) in EUR pro Jahr (ohne Boni)': 'gas', 'Datum': 'datum'}, inplace=True)

        # get household estimates for postal codes with missing data
        # electricity
        old_plz = 0
        sumnan = pop = sumhh = 1
        for i, x in enumerate(dfac['hh']):
            if x == 0:
                plz = dfac.loc[i, 'id']
                if old_plz != plz:
                    pop_val = _pop_for_plz(plz)
                    if pd.isna(pop_val):
                        # if we cannot get population at all, fall back to a conservative estimate
                        # (keep hh at 0 rather than crashing)
                        dfac.loc[i, 'hh'] = 0
                        old_plz = plz
                        continue
                    pop = pd.Series([pop_val])
                    sumhh = dfac[dfac['id'] == plz]['hh'].sum()
                    sumnan = dfac[(dfac['id'] == plz)].count()['id']
                if sumnan == 0:
                    # nothing to distribute; keep at 0
                    dfac.loc[i, 'hh'] = 0
                    old_plz = plz
                    continue
                # average persons per household 2021
                res = ((pop / 2.02) - sumhh) / sumnan
                if res.empty or pd.isna(res.iloc[0]):
                    dfac.loc[i, 'hh'] = 0
                else:
                    dfac.loc[i, 'hh'] = max(int(res.iloc[0]), 0)
                old_plz = plz
        # gas
        old_plz = 0
        sumnan = pop = sumhh = 1
        for i, x in enumerate(dfgas['hh']):
            if x == 0:
                plz = dfgas.loc[i, 'id']
                if old_plz != plz:
                    pop_val = _pop_for_plz(plz)
                    if pd.isna(pop_val):
                        dfgas.loc[i, 'hh'] = 0
                        old_plz = plz
                        continue
                    pop = pd.Series([pop_val])
                    sumhh = dfgas[dfgas['id'] == plz]['hh'].sum()
                    sumnan = dfgas[(dfgas['id'] == plz)].count()['id']
                if sumnan == 0:
                    # nothing to distribute; keep at 0
                    dfgas.loc[i, 'hh'] = 0
                    old_plz = plz
                    continue
                # average persons per household 2021
                res = ((pop / 2.02) - sumhh) / sumnan
                if res.empty or pd.isna(res.iloc[0]):
                    dfgas.loc[i, 'hh'] = 0
                else:
                    dfgas.loc[i, 'hh'] = max(int(res.iloc[0]), 0)
                old_plz = plz

        # calculate weighted mean for Germany
        meanac = np.average(
            dfac['strom'], weights=dfac['hh']).round(0).astype(int)
        meangas = np.average(
            dfgas['gas'], weights=dfgas['hh']).round(0).astype(int)

        # calculate weighted mean for duplicate zipcodes based on households
        dfac['hh'].replace(0, 1, inplace=True)
        dfgas['hh'].replace(0, 1, inplace=True)
        dfac = (
            dfac.groupby('id')
            .apply(lambda x: np.average(x['strom'], weights=x['hh']))
            .reset_index()
            .rename(columns={0: 'strom'})
        )
        dfgas = (
            dfgas.groupby('id')
            .apply(lambda x: np.average(x['gas'], weights=x['hh']))
            .reset_index()
            .rename(columns={0: 'gas'})
        )

        # merge gas and electricity and append current average for Germany
        #df = dfac.join(dfgas.set_index('id'), on='id')
        df = dfac.merge(dfgas, on='id', how='outer')
        # New national-series point? Compare Snowflake snapshot day vs latest day stored in dfavg.
        datediff = snapshot_dt.to_pydatetime() - pd.Timestamp(dfavg['date'].max()).normalize().to_pydatetime()

        if datediff >= timedelta(days=1):  # check if there's new data
            dfavg2 = pd.DataFrame()
            dfavg2['date'] = [time_dt]
            dfavg2['Gas'] = [meangas]
            dfavg2['Strom'] = [meanac]
            #dfavg = dfavg.append(dfavg2.tail(1))
            dfavg = pd.concat([dfavg, dfavg2], ignore_index=True)
            dfavg.set_index('date', inplace=True)

            # check if there are Sundays missing
            datediff = dfavg.index[-1] - dfavg.index[-2]
            if datediff > timedelta(days=1):
                dfavg = dfavg.asfreq('D')  # add rows for missing days
                dfavg.interpolate(inplace=True)  # fill NaN with values
                dfavg = dfavg.round(0).astype(int)

            #dfavg.index = dfavg.index.strftime('%Y-%m-%d')
            # "Stand" for the national-series chart is the newest date in dfavg (after appending/interpolation)
            stand_series_dt = pd.Timestamp(dfavg.index.max()).normalize()
            notes_chart = '¹ Im Vergleich zu den durchschnittlichen Kosten im Jahr 2020.<br>² Gewichteter Bundesdurchschnitt der jeweils günstigsten Tarife (Preisgarantie mindestens 12 Monate, ohne Boni).<br>Stand: ' + \
                str(stand_series_dt.strftime('%-d.\u2009%-m.\u2009%Y'))
            dfavg.to_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t')
            gas_new = dfavg['Gas'].iloc[-1]
            ac_new = dfavg['Strom'].iloc[-1]
            gas_old = 931  # average 2020 (with bonus: 842)
            ac_old = 1082  # average 2020 (with bonus: 947)
            title_costs_diff = round(
                (gas_new + ac_new) - (gas_old + ac_old), -1)
            dfavg = dfavg.rolling(window=7).mean(
            ).dropna()  # 7-day mvg average
            dfavg = dfavg[~(dfavg.index < '2021-01-01')]
            # title_chart = f'20 MWh Gas kosten {int(gas_new.round(-1))} Euro im Jahr, 4 MWh Strom {int(ac_new.round(-1))} Euro'
            if title_costs_diff >= 0:
                title_chart = f'Energie kostet eine vierköpfige Familie {int(title_costs_diff)} Euro mehr als vor der Krise¹'
            else:
                title_chart = f'Energie kostet eine vierköpfige Familie {int(title_costs_diff)} Euro weniger als vor der Krise¹'
            dfavg = dfavg.applymap(str).reset_index(
                drop=False).T.reset_index().T.apply(list, axis=1).to_list()
            # update chart with averages
            update_chart(id='4acf1a0fd4dd89aef4abaeefd05b7aa7',
                         data=dfavg, notes=notes_chart, title=title_chart)
        else:
            dfavg.set_index('date', inplace=True)
            stand_series_dt = pd.Timestamp(dfavg.index.max()).normalize()
            notes_chart = '¹ Im Vergleich zu den durchschnittlichen Kosten im Jahr 2020.<br>² Gewichteter Bundesdurchschnitt der jeweils günstigsten Tarife (Preisgarantie mindestens 12 Monate, ohne Boni).<br>Stand: ' + \
                str(stand_series_dt.strftime('%-d.\u2009%-m.\u2009%Y'))
            gas_new = dfavg['Gas'].iloc[-1]
            ac_new = dfavg['Strom'].iloc[-1]
            gas_old = 931  # average 2020 (with bonus: 842)
            ac_old = 1082  # average 2020 (with bonus: 947)
            title_costs_diff = round(
                (gas_new + ac_new) - (gas_old + ac_old), -1)
            dfavg = dfavg.rolling(window=7).mean(
            ).dropna()  # 7-day mvg average
            dfavg = dfavg[~(dfavg.index < '2021-01-01')]
            # title_chart = f'20 MWh Gas kosten {int(gas_new.round(-1))} Euro im Jahr, 4 MWh Strom {int(ac_new.round(-1))} Euro'
            if title_costs_diff >= 0:
                title_chart = f'Energie kostet eine vierköpfige Familie {int(title_costs_diff)} Euro mehr als vor der Krise¹'
            else:
                title_chart = f'Energie kostet eine vierköpfige Familie {int(title_costs_diff)} Euro weniger als vor der Krise¹'
            dfavg = dfavg.applymap(str).reset_index(
                drop=False).T.reset_index().T.apply(list, axis=1).to_list()
            update_chart(id='4acf1a0fd4dd89aef4abaeefd05b7aa7',
                         data=dfavg, notes=notes_chart, title=title_chart)

        # merge dataframes, then join geometry with verivox data and save
        df = df.merge(df21, on='id', how='outer')
        df.strom = df.strom.round(0).astype(float)
        df.gas = df.gas.round(0).astype(float)
        df = gdf.set_index('id').join(df.set_index('id'))
        #df = df.to_crs(4326)
        df.to_file('./data/nzz-gas-strom.geojson', driver='GeoJSON')

        # run mapshaper and pass arguments as list to avoid shell=True
        simplified = subprocess.Popen(['mapshaper', './data/nzz-gas-strom.geojson', '-proj', 'crs="EPSG:4326"', '-o',
                                      'format=topojson', './data/de-postcode-geographic-1-5.json'], stdout=subprocess.PIPE)
        output = simplified.stdout.read()

        # prepare some data for q.config.json
        data = [[
            "lastUpdatedAt",
            "MeanAC",
            "MeanGas"
        ],
            [
            str(time_str),
            str(meanac),
            str(meangas)
        ]]
        file = [{
            "loadSyncBeforeInit": False,
            "file": {
                "path": "./data/de-postcode-geographic-1-5.json"
            }
        }]

        notes_chart = 'Die Zahlen beruhen auf dem jeweils günstigsten Neukunden-Tarif (Preisgarantie mindestens 12 Monate, ohne Boni) für eine vierköpfige Familie in einem Einfamilienhaus mit einem Jahresverbrauch von 20 MWh Gas bzw. 4 MWh Strom.<br>Stand: ' + \
            str(time_str_notes)

        # run function
        update_chart(id='4acf1a0fd4dd89aef4abaeefd02be69f',
                     files=file, data=data, notes=notes_chart)

    except:
        raise
