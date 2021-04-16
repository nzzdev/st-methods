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
        # set source data
        url = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'germany_vaccinations_timeseries_v2.tsv'), 'wb') as f:
            f.write(download_data(url).read())

        # read relevant columns
        df = pd.read_csv('./data/germany_vaccinations_timeseries_v2.tsv', delimiter='\t', encoding='utf-8',
                         usecols=['date', 'indikation_pflegeheim_erst', 'indikation_pflegeheim_voll'])

        # extract last row (=today), reset index and delete old df
        df2 = df.iloc[[-1]].reset_index(drop=True)
        del [[df]]
        gc.collect()

        # get date for chart notes and add one day
        timestamp_str = df2.loc[0, 'date']
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # delete date value
        df2.loc[0, 'date'] = ''

        # rename first column and set as index
        df2 = df2.rename(columns={'date': '', 'indikation_pflegeheim_erst': 'erste Dose',
                         'indikation_pflegeheim_voll': 'vollständig geimpft'}).set_index('')

        # show date in chart notes
        notes_chart = 'Laut dem Statistischen Bundesamt (StBA) lebten in Deutschland im Jahr 2019 rund 820 000 Menschen in Pflege- und Altersheimen. In die Statistik zu «geimpften Pflegeheimbewohnern» des RKI fliessen allerdings inzwischen auch Zahlen von geimpften Menschen ein, die gemäss der Definition des StBA keine Pflegeheimbewohner sind.<br>Stand: ' + \
            timestamp_str

        # insert id and subtitle manually and run function
        updateChart(id='b4b5354dc92073edbdccdff477de959a',
                    data=df2, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
