import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
import locale
import os
from datetime import date, timedelta
from time import sleep
import pandas as pd


def update_chart(id, title="", subtitle="", notes="", data=pd.DataFrame(), options="", asset_groups=[], files=[]):  # Q helper function
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
                if options != '':
                    item.get('item').update({'options': options})

    # write qConfig file
    with open('./q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False,
                  indent=1, default=str)
    json_file.close()


if __name__ == '__main__':
    try:
        cookies = {
            '_rdfa': 's%3A6fbe6e4f-b105-41e1-b706-6ceb05000f59.kg9sN4xIYpIRcilnxLgJZ7yqzO2ABojmSm1Gzy3HMrc',
            'optimizelyEndUserId': 'oeu1571411829743r0.8517103064407519',
            'AMCVS_65BE20B35350E8DE0A490D45%40AdobeOrg': '1',
            'ecid': 'sea_google_ls_nonbr_milka-[mar-0002|bm|lm]_milka-kaufen-[mar-0002|eco-0012|1|bm|lm]_text-ad_833898230_43028178719',
            'trbo_usr': '1c0854b37e993a19cf919e3cead78156',
            'mf_2d859e38-92a3-4080-8117-c7e82466e45a': '-1',
            '_fbp': 'fb.1.1571411834470.1081952992',
            'icVarSave': 'TC%2042%20Treatment%20Random%2CTC45%20Treatment',
            's_cc': 'true',
            'ken_gclid': 'CjwKCAjwxaXtBRBbEiwAPqPxcNgeH3ccV9kjh8idQDoCSc3xwLjG0ReGjCnbBeQyQkHz2h1pVbx6VRoCXDsQAvD_BwE',
            'cto_lwid': 'abc4dd35-f42e-44fd-9d3d-8ee2b4f01c8c',
            'sto__vuid': '317fa2090832e63c6a88f410d2437c09',
            'myReweCookie': '%7B%22customerZip%22%3A%2210247%22%2C%22customerLocation%22%3A%2252.51604592808167%2C13.465546337768295%22%2C%22deliveryMarketId%22%3A%22231006%22%2C%22serviceType%22%3A%22DELIVERY%22%7D',
            'marketsCookie': '%7B%22online%22%3A%7B%22wwIdent%22%3A%22231006%22%2C%22marketZipCode%22%3A%2213089%22%2C%22serviceTypes%22%3A%5B%22PARCEL%22%2C%22DELIVERY%22%5D%2C%22customerZipCode%22%3A%2210247%22%7D%2C%22stationary%22%3A%7B%7D%7D',
            '_gcl_aw': 'GCL.1571411845.CjwKCAjwxaXtBRBbEiwAPqPxcNgeH3ccV9kjh8idQDoCSc3xwLjG0ReGjCnbBeQyQkHz2h1pVbx6VRoCXDsQAvD_BwE',
            'mfCookie': '-1',
            'cookie-consent': '1',
            'MRefererUrl': 'https%3A%2F%2Fwww.google.com%2F',
            'AMCV_65BE20B35350E8DE0A490D45%40AdobeOrg': '1075005958%7CMCIDTS%7C18199%7CMCMID%7C68984298103318409563185344066719227243%7CMCAAMLH-1572985682%7C6%7CMCAAMB-1572985682%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1572388082s%7CNONE%7CvVersion%7C4.4.1',
            'c_dslv_s': '11',
            's_vnum': '1572562800740%26vn%3D2',
            's_invisit': 'true',
            'sto__session': '1572380885541',
            'c_dslv': '1572380922284',
            's_ppn': 'rewe-de%3Asuche',
            'trbo_sess_3723808811': '%7B%22firstClickTime%22%3A1572380883%2C%22lastClickTime%22%3A1572380923%2C%22pageViewCount%22%3A2%2C%22sessionDuration%22%3A40%7D',
            'perfTimings': 'event180=0.04%2Cevent181=0.00%2Cevent182=0.00%2Cevent183=0.00%2Cevent184=0.50%2Cevent185=0.03%2Cevent186=3.79%2Cevent187=0.06%2Cevent188=5.13%2Cevent189%3Brewe-de:suche',
            'perfLoad': '5.13',
            '_derived_epik': 'dj0yJnU9ZHdKbEtVdFJ5dVBEZ08yUEJQMDVHczdMVlh0bzFhNzMmbj04WjRqU1ZOQVIzVEF4MVFFZWMzcDN3Jm09NyZ0PUFBQUFBRjI0b1Bz',
            'mtc': 's%3AIJzxk40H3Y8CGzgfvZKF8gJMVy8iMTMxMjdkLWVKZ2t2ckNmTW5wVFlkdmNqY3BKME05QnhwNCIi6gKKBsIE7AG6BMADWJwFtgRcngK%2BAuYFnAakBqwGqgYABsgD4gKoBAA%3D.RJNwL9jE5BtuIUnIZQlX701ZkcSswAW9scvTCJBbrOE',
            '_afid': '4502757903888691750',
            'trbo_session': '3723810860',
            'trbo_us_1c0854b37e993a19cf919e3cead78156': '%7B%22saleCount%22%3A0%2C%22sessionCount%22%3A2%2C%22brandSessionCount%22%3A1%2C%22pageViewCountTotal%22%3A3%2C%22sessionDurationTotal%22%3A10%2C%22externalUserId%22%3A%22%22%2C%22userCreateTime%22%3A1571411834%7D',
            'trbo_sess_3723810860': '%7B%22firstClickTime%22%3A1572381080%2C%22lastClickTime%22%3A1572381080%2C%22pageViewCount%22%3A1%2C%22sessionDuration%22%3A0%7D',
            'c_lpv_a': '1572381081513|seo_google_nn_nn_nn_nn_nn_nn_nn',
            'rstp': 'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJhZXMxOTIiOiIyYjkwYWQ3MDdlMmQ5MGUyYTljNzJiZTAzNjgwZTdkMDczMzc3OTNjMmEyNTI2NzkzODc5Y2I5ZGMwYzM4MWI4YzMzNzA0NWE0ODZmMWYyZTczY2IwZjJjM2IxODRmYTE0MjU1YjQxYmVmM2M5M2Y4YzI2MDQzODllZWRjNGE3ZjgyYWQwZWNhMjY3ZjAzOTBjZmJiMDE1ZGY1ZTQ2ZmJhZjQ3ZDg3YzdkMDEyMzM1OWJjOWQxNGVlNjZkOTc5NjIwZjJiMzJlMjQ0NzkzOTk1MTIzMzU2MjEzZmNlZDZlMWNmMGFmZTUxOTAzYjkwNmY1MjFhMjY3ODNmYjBlODNhMTk3OWMxMWQ4Y2JjZDc3Yzc3ZTAxNjM2ZjcwNjg1NGM3ZDk5NzVhNDZkOWVjZjdiYjBhOTJlZWVhNzk0NjUzNGI5NTE3ZDVkZmU2Mjg0ZTRmOTkxOTI0NWU2NjYyMjk1MmY0MTgwOWE1ZjgxZWI5ZWE3ZjdiYmEzZWNiZWE4NjA3NDU0OTY3MzkwM2U1MmJmOTg3ZDI4ZmY0MTBlYTA1OGNmMjIzODNjZDZiZjM4OGIwYTZkNjg3YzFjY2JlNzBjZDNlOWI2OGE5ZjVhZjNlM2YzNGYwYTQzODA4YjYzYTJkNmQ2YWYwM2Q3ZjlhNTdjOWNlMDgyZWE0MmExYTk2NCIsImlhdCI6MTU3MjM4MTA4MSwiZXhwIjoxNTcyMzgxNjgxfQ.9Pwhf0LU7rCkV6IgqUjyLfRiez8SWMEvisficIifvHRmB9QHRfe7SdH3zTMqxOxtZc8Io9ITshCo2Si6owRwgw',
            'sto__count': '1',
            's_nr': '1572381123119-Repeat',
            's_sq': 'rewrewededev%3D%2526c.%2526a.%2526activitymap.%2526page%253Dproduktliste%2526link%253D2%2526region%253Dsearch-service-content%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c',
        }

        headers = {
            'sec-fetch-mode': 'cors',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'accept': 'application/vnd.rewe.productlist+json',
            'referer': 'https://shop.rewe.de/productList?search=k%C3%A4se',
            'authority': 'shop.rewe.de',
            'sec-fetch-site': 'same-origin',
        }

        today = date.today()
        yesterday = date.today() - timedelta(days=1)
        todaynice = today.strftime('%-d.%-m.')

        # retry if error
        logging.basicConfig(level=logging.INFO)
        s = requests.Session()
        retries = Retry(total=10, backoff_factor=1,
                        status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        header = (f"Datum;ID;Marke;Name;Preis;Gewicht"+'\n')
        brands = ['ja!', 'REWE Beste Wahl', 'REWE', 'REWE Bio']

        # set working directory and locale
        os.chdir(os.path.dirname(__file__))
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
        if not os.path.exists('data'):
            os.makedirs('data')

        ################
        # Preismonitor #
        ################

        past = today - timedelta(days=30)
        df_t = pd.read_csv('./data/' + today.strftime('%Y-%m-%d') +
                           '-rewe.csv', sep=';', on_bad_lines='skip')
        df_t = df_t[df_t['Marke'] == 'ja!']

        df_y = pd.read_csv('https://raw.githubusercontent.com/nzzdev/st-methods/master/bots/crawl-rewe-de/data/' +
                           past.strftime('%Y-%m-%d') + '-rewe.csv', sep=';', on_bad_lines='skip')
        df_y = df_y[df_y['Marke'] == 'ja!']

        df_t = df_t.dropna(subset='Preis')
        df_y = df_y.dropna(subset='Preis')
        df_t['Preis'] = df_t['Preis']/100
        df_y['Preis'] = df_y['Preis']/100

        df_t = df_t[['ID', 'Name', 'Preis', 'Gewicht']]
        df_y = df_y[['ID', 'Name', 'Preis', 'Gewicht']]
        df_t.rename({'Preis': 'Neuer Preis'}, axis=1, inplace=True)
        df_y.rename({'Preis': 'Alter Preis'}, axis=1, inplace=True)

        df_t_y = df_t.merge(df_y, on=['ID', 'Name'])

        df_t_y['Differenz'] = (((df_t_y['Neuer Preis'] - df_t_y['Alter Preis']) /
                               df_t_y['Alter Preis'])*100).round(0).astype(int)
        df_t_y['Differenz'] = df_t_y['Differenz']
        df_t_y = df_t_y[df_t_y['Differenz'] != 0]
        df_t_y.sort_values(by=['Differenz'], inplace=True, ascending=False)

        df_t_y.loc[df_t_y['Differenz'] > 0, ''] = ' ↑ '
        df_t_y.loc[df_t_y['Differenz'] < 0, ''] = ' ↓ '
        #df_t_y.loc[df_t_y['Differenz'] > 0, ''] = ' ↑ '
        #df_t_y.loc[df_t_y['Differenz'] < 0, ''] = ' ↓ '
        #df_t_y['Neuer Preis'] = df_t_y['Neuer Preis'].apply(lambda x: f'➚ +{x}%' if x >= 0 else f'➘ -{x}%')
        #df_t_y['Alter Preis'] = df_t_y['Alter Preis'].apply(lambda x: f'➚ +{x}%' if x >= 0 else f'➘ -{x}%')

        # drop pseudo duplicates (like "Joghurt")
        df_t_y = df_t_y.drop_duplicates(subset='Name', keep='first')

        df_t_y.sort_values(by=['Differenz'], inplace=True, ascending=False)
        #df_t_y['Veränderung'] = '»'
        df_t_y = df_t_y[['', 'Name', 'Alter Preis', 'Neuer Preis']]
        #df_t_y.rename({'Veränderung': ''}, axis = 1, inplace = True)

        # title fixes
        df_t_y['Name'] = df_t_y['Name'].astype(
            str).str.replace(r'[Jj]a!\s', r'', regex=True)
        df_t_y['Name'] = df_t_y['Name'].astype(
            str).str.replace(r'\s\d.*', r'', regex=True)
        df_t_y['Name'] = df_t_y['Name'].astype(
            str).str.replace(r'\smit\s.*', r'', regex=True)
        df_t_y['Name'] = df_t_y['Name'].astype(
            str).str.replace(' ca.', '', regex=False)

        # Fix for large quantities
        #df_t_y['Name'] = df_t_y['Name'].astype(str).replace(bulkpacks)

        #df_t_y.rename({'Differenz': '%'}, axis = 1, inplace = True)
        df_t_y.set_index('', inplace=True)
        df_t_y.rename({'Name': ' '}, axis=1, inplace=True)

        notes_chart = '¹ Die Preise der Rewe-Eigenmarke entsprechen in der Regel den Aldi-Preisen.<br>Stand: ' + todaynice

        # run Q function
        update_chart(id='83caf1c1cfcfaf76da2c577a9efa0cfa',
                     data=df_t_y, notes=notes_chart)
    except:
        raise
