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
        pass_env = os.environ['VERIVOX_SNOWFLAKE_PASS']
        acc_env = os.environ['VERIVOX_SNOWFLAKE_ACC']

        con = snowflake.connector.connect(
            user=user_env,
            password=pass_env,
            account=acc_env,
            warehouse='NZZ_WH',
            database='NZZ',
            schema='NZZ'
        )

        cur = con.cursor()

        # execute a statement that will generate a result set
        cur.execute("USE ROLE NZZ_ROLE")
        cur.execute(
            "SELECT * FROM ELECTRICITY WHERE \"Datum\" = (SELECT MAX(\"Datum\") FROM ELECTRICITY)")

        # fetch the result set from the cursor and deliver as pandas dataframe
        df = cur.fetch_pandas_all()
        df.to_csv('./data/newest_electricity_data.csv')

        cur.execute(
            "SELECT * FROM GAS WHERE \"Datum\" = (SELECT MAX(\"Datum\") FROM GAS)")
        df = cur.fetch_pandas_all()
        df.to_csv('./data/newest_gas_data.csv')

        # read unzipped file and geojson as dataframe
        dfac = pd.read_csv('./data/newest_electricity_data.csv', index_col=None, usecols=[
                           'Postleitzahl', 'Anzahl Haushalte', 'Gesamtkosten (brutto) in EUR pro Jahr', 'Datum'], dtype={'Postleitzahl': 'string'})
        dfgas = pd.read_csv('./data/newest_gas_data.csv', index_col=None, usecols=[
                            'Postleitzahl', 'Anzahl Haushalte', 'Gesamtkosten (brutto) in EUR pro Jahr', 'Datum'], dtype={'Postleitzahl': 'string'})
        df21 = pd.read_csv('./data/gas-strom-0921.tsv',
                           sep='\t', index_col=None, dtype={'id': 'string'})
        dfavg = pd.read_csv(
            './data/gas-strom-bundesschnitt.tsv', sep='\t', index_col=None)

        # GeoJSON with postal codes
        gdf = gpd.read_file('./data/plz_vereinfacht_1.5.json')

        # current date
        dfac['Datum'] = pd.to_datetime(dfac['Datum'])
        dfgas['Datum'] = pd.to_datetime(dfgas['Datum'])
        time_dt = dfac['Datum'].iloc[-1]
        time_str = time_dt.strftime('%Y-%m-%d %H:%M:%SZ')
        time_str_notes = time_dt.strftime('%-d. %-m. %Y')

        # rename column headers
        dfac.rename(columns={'Postleitzahl': 'id', 'Anzahl Haushalte': 'hh',
                             'Gesamtkosten (brutto) in EUR pro Jahr': 'strom', 'Datum': 'datum'}, inplace=True)
        dfgas.rename(columns={'Postleitzahl': 'id', 'Anzahl Haushalte': 'hh',
                              'Gesamtkosten (brutto) in EUR pro Jahr': 'gas', 'Datum': 'datum'}, inplace=True)

        # replace missing household data with average of adjacent rows
        dfac['hh'].replace(0, np.nan, inplace=True)
        dfac['hh'].interpolate(inplace=True)
        dfgas['hh'].replace(0, np.nan, inplace=True)
        dfgas['hh'].interpolate(inplace=True)

        # calculate weighted mean for Germany
        meanac = np.average(
            dfac['strom'], weights=dfac['hh']).round(0).astype(int)
        meangas = np.average(
            dfgas['gas'], weights=dfgas['hh']).round(0).astype(int)

        # calculate weighted mean for duplicate zipcodes based on households
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
        dfavg['date'] = pd.to_datetime(dfavg['date'])
        datediff = time_dt - dfavg['date'].iloc[-1]

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
            notes_chart = '¹ Gewichteter Bundesdurchschnitt der jeweils günstigsten Tarife (ohne Grundversorgung).<br>Stand: ' + \
                str(time_str_notes)
            dfavg.to_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t')
            dfavg = dfavg.rolling(window=7).mean(
            ).dropna()  # 7-day mvg average
            dfavg = dfavg.applymap(str).reset_index(
                drop=False).T.reset_index().T.apply(list, axis=1).to_list()
            # update chart with averages
            update_chart(id='4acf1a0fd4dd89aef4abaeefd05b7aa7',
                         data=dfavg, notes=notes_chart)
        else:
            time_dt_notes = dfavg['date'].iloc[-1]
            time_str_notes = time_dt_notes.strftime('%-d. %-m. %Y')
            dfavg.set_index('date', inplace=True)
            #dfavg.index = dfavg.index.strftime('%Y-%m-%d')
            notes_chart = '¹ Gewichteter Bundesdurchschnitt der jeweils günstigsten Tarife (ohne Grundversorgung).<br>Stand: ' + \
                str(time_str_notes)
            dfavg = dfavg.rolling(window=7).mean(
            ).dropna()  # 7-day mvg average
            dfavg = dfavg.applymap(str).reset_index(
                drop=False).T.reset_index().T.apply(list, axis=1).to_list()
            update_chart(id='4acf1a0fd4dd89aef4abaeefd05b7aa7',
                         data=dfavg, notes=notes_chart)

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

        notes_chart = 'Die Zahlen beruhen auf dem jeweils günstigsten verfügbaren Neukunden-Tarif für eine vierköpfige Familie in einem Einfamilienhaus mit einem Jahresverbrauch von 20 MWh Gas bzw. 4 MWh Strom.<br>Stand: ' + \
            str(time_str_notes)

        # run function
        update_chart(id='4acf1a0fd4dd89aef4abaeefd02be69f',
                     files=file, data=data, notes=notes_chart)

    except:
        raise
