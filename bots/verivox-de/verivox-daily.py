import os
import io
from regex import R
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
import pandas as pd
import geopandas as gpd
import numpy as np
import subprocess
import zipfile


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
        json.dump(qConfig, json_file, ensure_ascii=False, indent=1)
    json_file.close()

    # write qConfig file
    with open('./q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False, indent=1)
    json_file.close()


if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # MOVEit Transfer API
        base_uri = 'https://app.verivox.de/'
        token_path = '/webadmin/api/v1/token'
        uri_path = '/webadmin/api/v1/tasks'
        api_endpoint = base_uri + token_path
        tasks_url = base_uri + uri_path
        username = os.environ['VERIVOX_USERNAME']
        password = os.environ['VERIVOX_PASSWORD']

        payload = {'username': username,
                   'password': password, 'grant_type': 'password'}

        # is this a self signed cert enable this to ignore SSL errors
        requests.packages.urllib3.disable_warnings()

        # retry if error
        logging.basicConfig(level=logging.INFO)
        s = requests.Session()
        retries = Retry(total=10, backoff_factor=1,
                        status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        # connect to API
        r = s.post(api_endpoint, data=payload, verify=False)

        # auth token to be used by successive requests
        my_token = r.json()['access_token']

        # get all file names
        page = 1
        files = []
        while True:
            tasks_url = 'https://app.verivox.de/api/v1/files'
            task = s.get(tasks_url, headers={
                'Content-Type': 'application/json;charset=UTF-8', 'Authorization': 'Bearer {}'.format(my_token)}, verify=False, params={'page': page, 'perPage': '200'})
            if task.status_code == 404:
                print("No more pages")
                break
            else:
                task = json.loads(task.content)
                files += task['items']
                page += 1

        # generate file names ('Strom_Zeit_online_kw15_2.zip' etc.)
        strom_names = []
        gas_names = []
        spacetime = 10
        day = datetime.today()
        for i in range(spacetime):
            ending = str(day.isocalendar().week) + '_' + \
                str(day.isocalendar().weekday) + '.zip'
            strom_names.append('Strom_Zeit_online_kw' + ending)
            gas_names.append('Gas_Zeit_online_kw' + ending)
            day = day - timedelta(days=1)

        # get file ids
        gas_item = None
        strom_item = None
        for i in range(spacetime):
            for item in files:
                if strom_item == None and item['name'] == strom_names[i]:
                    strom_item = item
                elif gas_item == None and item['name'] == gas_names[i]:
                    gas_item = item
            if gas_item != None and strom_item != None:
                break

        # download and extract
        tasks_url = 'https://app.verivox.de/api/v1/files/' + \
            str(gas_item['id']) + '/download'
        new_task = s.get(tasks_url, headers={
            'Content-Type': 'application/json;charset=UTF-8', 'Authorization': 'Bearer {}'.format(my_token)}, verify=False)
        z = zipfile.ZipFile(io.BytesIO(new_task.content))
        z.extractall('./data/')

        tasks_url = 'https://app.verivox.de/api/v1/files/' + \
            str(strom_item['id']) + '/download'
        new_task = s.get(tasks_url, headers={
            'Content-Type': 'application/json;charset=UTF-8', 'Authorization': 'Bearer {}'.format(my_token)}, verify=False)
        z = zipfile.ZipFile(io.BytesIO(new_task.content))
        z.extractall('./data/')

        # read unzipped file and geojson as dataframe
        dfac = pd.read_csv('./data/Strom_Zeit_online_4000.csv', encoding='ISO-8859-1', sep=';', decimal=',', index_col=None, usecols=[
            'Postleitzahl', 'Anzahl Haushalte', 'Gesamtkosten (Brutto) in EUR pro Jahr', 'Exportdatum'], dtype={'Postleitzahl': 'string'})
        dfgas = pd.read_csv('./data/Gas_Zeit_online_20000.csv', encoding='ISO-8859-1', sep=';', decimal=',', index_col=None, usecols=[
            'Postleitzahl', 'Anzahl Haushalte', 'Gesamtkosten (Brutto) in EUR pro Jahr', 'Exportdatum'], dtype={'Postleitzahl': 'string'})
        df21 = pd.read_csv('./data/gas-strom-0921.tsv',
                           sep='\t', index_col=None, dtype={'id': 'string'})
        dfavg = pd.read_csv(
            './data/gas-strom-bundesschnitt.tsv', sep='\t', index_col=None)

        # GeoJSON with postal codes
        gdf = gpd.read_file('./data/plz_vereinfacht_1.5.json')

        # current date
        time_str = (dfac.iat[0, 3])
        time_dt = datetime.strptime(time_str, '%d.%m.%y')
        time_str = time_dt.strftime(
            '%Y-%m-%dT%H:%M:%SZ')  # %Y-%m-%dT%H:%M:%S.%fZ
        time_str_notes = time_dt.strftime('%-d. %-m. %Y')

        # rename column headers
        dfac.rename(columns={'Postleitzahl': 'id', 'Anzahl Haushalte': 'hh',
                             'Gesamtkosten (Brutto) in EUR pro Jahr': 'strom', 'Exportdatum': 'datum'}, inplace=True)
        dfgas.rename(columns={'Postleitzahl': 'id', 'Anzahl Haushalte': 'hh',
                              'Gesamtkosten (Brutto) in EUR pro Jahr': 'gas', 'Exportdatum': 'datum'}, inplace=True)

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
        if time_dt > dfavg['date'].iloc[-1]:  # check if there's new data
            dfavg2 = pd.DataFrame()
            dfavg2['date'] = [time_dt]
            dfavg2['Gas'] = [meangas]
            dfavg2['Strom'] = [meanac]
            #dfavg = dfavg.append(dfavg2.tail(1))
            dfavg = pd.concat([dfavg, dfavg2], ignore_index=True)
            dfavg.set_index('date', inplace=True)
            dfavg.index = dfavg.index.strftime('%Y-%m-%d')
            notes_chart = '¹ Gewichteter Bundesdurchschnitt.<br>Stand: ' + \
                str(time_str_notes)
            dfavg.to_csv('./data/gas-strom-bundesschnitt.tsv', sep='\t')
            dfavg = dfavg.applymap(str).reset_index(
                drop=False).T.reset_index().T.apply(list, axis=1).to_list()
            # update chart with averages
            update_chart(id='4acf1a0fd4dd89aef4abaeefd05b7aa7',
                         data=dfavg, notes=notes_chart)
            print(dfavg)
        else:
            dfavg.set_index('date', inplace=True)
            dfavg.index = dfavg.index.strftime('%Y-%m-%d')
            dfavg = dfavg.applymap(str).reset_index(
                drop=False).T.reset_index().T.apply(list, axis=1).to_list()
            update_chart(id='4acf1a0fd4dd89aef4abaeefd05b7aa7', data=dfavg)

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

        # delete all csv and geojson files
        dir = 'data/'
        extracted = os.listdir(dir)
        for item in extracted:
            if item.endswith('.csv') or item.endswith('.geojson'):
                os.remove(os.path.join(dir, item))

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

        notes_chart = 'Die Daten zeigen den jeweils günstigsten verfügbaren Tarif für eine vierköpfige Familie im Einfamilienhaus mit einem Jahresverbrauch von 20 MWh Gas bzw. 4 MWh Strom.<br>Stand: ' + \
            str(time_str_notes)

        # run function
        update_chart(id='4acf1a0fd4dd89aef4abaeefd02be69f',
                     files=file, data=data, notes=notes_chart)

    except:
        raise
