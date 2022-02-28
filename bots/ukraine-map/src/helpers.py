import pandas as pd
import json
#import gspread
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from time import sleep


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


def download_sheet(sh, name):  # function for sheet download
    try:
        wsh = sh.worksheet(name)
        return wsh
    except gspread.exceptions.APIError as e:
        if e.response.status_code == 429:
            sleep(5)
            try:
                wsh = sh.worksheet(name)
                return wsh
            except gspread.exceptions.APIError as e:
                print('Script failed twice (blacklisted?):', e)
        elif e.response.status_code > 499:
            sleep(20)
            try:
                wsh = sh.worksheet(name)
                return wsh
            except gspread.exceptions.APIError as e:
                print('Script failed twice (check source):', e)
        else:
            print('Other HTTP error:', e)
    except gspread.exceptions.APIError as e:
        print('Other URL error:', e)


def update_chart(id, title="", subtitle="", notes="", data=pd.DataFrame(), asset_groups=[], files=[]):  # Q helper function
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
                if len(asset_groups) > 0:
                    groups = []
                    for g in asset_groups:
                        groups.append({
                            'assets': [{"path": f} for f in g['files']],
                            'name': g['name']
                        })
                    item['item']['assetGroups'] = groups

                if len(files) > 0:
                    item['item']['files'] = files

                print('Successfully updated item with id', id,
                      'on', environment.get('name'), 'environment')
    # write qConfig file
    with open('./q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False, indent=1)
    json_file.close()

"""

"assetGroups": [
        {
          "assets": [
            {
            "path": "./data/test.json"
            }
          ],
          "name": "data"
        }
      ]
"""