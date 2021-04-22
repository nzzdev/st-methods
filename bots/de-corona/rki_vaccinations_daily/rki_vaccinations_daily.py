import os
import pandas as pd
import gc
import json
from datetime import datetime, timedelta
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def download_data(url):  # function for data download
    try:
        return urlopen(url)
    except HTTPError as e:
        if e.code == 429:  # too many requests
            sleep(5)
            try:
                return urlopen(url)
            except HTTPError as e:
                print('Script failed twice (IP blacklisted?):', e.reason)
        elif e.code == 500:  # internal server error
            sleep(20)
            try:
                return urlopen(url)
            except HTTPError as e:
                print('Script failed twice (check source):', e.reason)
        else:
            print('Other HTTP error:', e.reason)
    except URLError as e:
        print('Other URL error:', e.reason)


def updateChart(id, title="", subtitle="", notes="", data=pd.DataFrame()):  # Q helper function
    # read qConfig file
    json_file = open('../q.config.json')
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
                if data.size > 0:
                    # reset_index() and T (for transpose) are used to bring column names into the first row
                    transformed_data = data.applymap(str).reset_index(
                        drop=False).T.reset_index().T.apply(list, axis=1).to_list()
                    if 'table' in item.get('item').get('data'):
                        item.get('item').get('data').update(
                            {'table': transformed_data})
                    else:
                        item.get('item').update({'data': transformed_data})
                print('Successfully updated item with id', id,
                      'on', environment.get('name'), 'environment')
    # write qConfig file
    with open('../q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False, indent=1)
    json_file.close()


if __name__ == '__main__':
    try:
        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # set source data
        url = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'germany_vaccinations_timeseries_v2.tsv'), 'wb') as f:
            f.write(download_data(url).read())

        # read relevant columns
        df = pd.read_csv('./data/germany_vaccinations_timeseries_v2.tsv', delimiter='\t', encoding='utf-8',
                         usecols=['date', 'dosen_erst_differenz_zum_vortag', 'dosen_zweit_differenz_zum_vortag'])

        # rearrange columns
        # df2 = df2[['date', 'impf_quote_voll', 'impf_quote_erst', 'Ziel']]

        # get date for chart notes and add one day
        timestamp_str = df['date'].iloc[-1]
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # rename first column and set as index
        df = df.rename(columns={'date': '', 'dosen_erst_differenz_zum_vortag': 'Erstimpfungen',
                       'dosen_zweit_differenz_zum_vortag': 'Zweitimpfungen'}).set_index('')

        # change date format
        df.index = pd.to_datetime(
            df.index, format='%Y-%m-%d').strftime('%d.%m.%Y')

       # show date in chart notes
        notes_chart = 'Stand: ' + \
            timestamp_str
        print
        # insert id and subtitle manually and run function
        updateChart(id='dd4b1de66b3907bb65164669b0d3353f',
                    data=df, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
