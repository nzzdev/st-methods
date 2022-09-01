import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
import os
from datetime import datetime, date, timedelta
from time import sleep
import pandas as pd
import math


def update_chart(id, title="", subtitle="", notes="", data=pd.DataFrame(), options=""):  # Q helper function
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
        from helpers import *

        headers = {
            'sec-fetch-mode': 'cors',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'referer': 'https://agsi.gie.eu/historical/DE',
            'authority': 'agsi.gie.eu',
            'sec-fetch-site': 'same-origin',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # create dates
        today = date.today()
        todaystr = today.strftime('%Y-%m-%d')
        endstr = '2022-01-01'

        # calculate number of pages needed
        start = datetime.strptime(todaystr, "%Y-%m-%d") + timedelta(days=300)
        end = datetime.strptime(endstr, "%Y-%m-%d")
        pages = (end - start) / timedelta(days=300)
        pages = abs(int(math.floor(pages)))  # round and remove negative sign
        futurestr = start.strftime('%Y-%m-%d')

        # retry if error
        logging.basicConfig(level=logging.INFO)
        s = requests.Session()
        retries = Retry(total=10, backoff_factor=1,
                        status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        # create header and get data from 2022
        header = (f"Datum,2022"+'\n')
        with open(f'./data/{todaystr}-gasspeicher.csv', 'w') as file:
            file.write(header)
            for n in range(1, pages):
                params = (
                    ('country', 'DE'),
                    ('from', endstr),
                    ('to', futurestr),
                    ('page', n),
                    ('size', '300'),  # max. 300
                )
                response = s.get(
                    'https://agsi.gie.eu/api', headers=headers, params=params)
                json_response = json.loads(response.content)
                sleep(1)

                # write csv file
                for level in json_response['data']:
                    file.write(
                        level['gasDayStart'] +
                        ',' +
                        level['full'] +
                        '\n')
                # original query
                # https://agsi.gie.eu/api?country=DE&from=2013-04-15&to=2022-05-16&page=1&size=300

        # retrieve data from 2011-2022
        dfnew = pd.read_csv(
            f'./data/{todaystr}-gasspeicher.csv', index_col=None)
        dfold = pd.read_csv(
            './data/gas-storage-2011-2021.tsv', sep='\t', index_col=None)

        # convert date column to datetime
        dfold['Datum'] = pd.to_datetime(dfold['Datum'])
        dfnew['Datum'] = pd.to_datetime(dfnew['Datum'])
        dfnew = dfnew.sort_values(by='Datum', ascending=True)

        # get latest date for chart notes
        timecode = dfnew['Datum'].iloc[-1]
        timecodestr = timecode.strftime('%-d. %-m. %Y')

        # merge dataframes and convert datetime to string
        df = dfold.merge(dfnew, on='Datum', how='left')
        df.rename(columns={'Min': ''}, inplace=True)
        df['2022'].fillna('', inplace=True)
        df.set_index('Datum', inplace=True)

        # temporary fix for wrong storage data
        df.at['2022-08-20 00:00:00', '2022'] = 79.55
        #df.index = df.index.strftime('%Y-%m-%d')

        notes_chart = '¹ Maximum/Minimum der Füllstände 2011-2021.<br>Stand: ' + timecodestr
        # banker's rounding
        title_perc = dfnew['2022'].iloc[-1].round(
            1).astype(str).replace('.', ',')
        title = f'Gasspeicher zu {title_perc} Prozent gefüllt'

        # run function
        #update_chart(id='cc9eff02ba0867d71af4fbc25304797b', data=df, title=title, notes=notes_chart)

    except:
        raise
