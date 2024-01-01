import pandas as pd
import os
from datetime import datetime, timedelta
from time import sleep
from user_agent import generate_user_agent
import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import numpy as np
from datawrapper import Datawrapper

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # Datawrapper API key
        dw_key = os.environ['DATAWRAPPER_API']
        dw = Datawrapper(access_token=dw_key)
        dw_id = 'R05oB'

        # retry if error
        logging.basicConfig(level=logging.INFO)
        s = requests.Session()
        retries = Retry(total=10, backoff_factor=1,
                        status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        # generate headers
        headers = generate_user_agent()

        # generate year and week number for url
        d = datetime.today()
        dold = datetime.today() - timedelta(7)
        dweek = (d.isocalendar().week) - 1
        dweek_old = (dold.isocalendar().week) - 1
        dweek = '{:02d}'.format(dweek)
        dweek_old = '{:02d}'.format(dweek_old)
        dyear = (d.isocalendar().year)
        dyear_old = (dold.isocalendar().year)
        dnotes = d - timedelta(days=d.weekday())  # last monday
        dnotes = dnotes.strftime('%-d. %-m. %Y')

        # on Mondays wait for proper weekly data from Bundesnetzagentur till 8 GMT (imports in smard-sources.py)
        if not (d.today().weekday() == 0 and d.hour < 7):
            # data source for current data
            url = f'https://www.energy-charts.info/charts/import_export_map/data/tcs_week_{dyear}_{dweek}.json'
            url_source = f'https://www.energy-charts.info/charts/import_export_map/chart.htm?l=de&c=DE&week={dweek}'

            # download JSON and convert to dataframe
            r = s.get(url, headers={'user-agent': headers,
                                    'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
            data = r.json()
            df = pd.json_normalize(data)
            df.columns = df.iloc[0]

            # drop first row with meta data and keep only first column with values
            df = df.iloc[1:]
            df = df.reset_index(drop=True)

            # clean-up
            renamec = {df.columns[0]: 'ID', df.columns[1]: 'Wert'}
            df = df.rename(columns=renamec)
            df = df.filter(['ID', 'Wert'])

            # clean-up for Datawrapper
            # replace ALPHA-2 codes with country names
            iso = {'AD': 'Andorra', 'AL': 'Albania', 'AT': 'Austria', 'AL': 'Albania', 'BA': 'Bosnia and Herz.', 'BE': 'Belgium', 'BG': 'Bulgaria', 'CH': 'Switzerland', 'CZ': 'Czech Rep.', 'DE': 'Germany', 'DE_LU': 'XX', 'DK': 'Denmark', 'EE': 'Estonia', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France', 'GR': 'Greece', 'HR': 'Croatia', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'IS': 'Iceland',
                   'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MD': 'Moldova', 'ME': 'Montenegro', 'MK': 'North Macedonia', 'MT': 'Malta', 'NIE': 'YY', 'NL': 'Netherlands', 'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'RS': 'Serbia', 'RU': 'RU', 'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia', 'TR': 'Turkey', 'UA': 'Ukraine', 'UA_W': 'ZZ', 'UK': 'United Kingdom', 'XK': 'Kosovo'}
            df['ID'] = df['ID'].map(iso)

            # drop empty rows and with less than 4 characters
            df = df[df['ID'].notna()]
            df = df[df['ID'].str.len() >= 3]

            # add missing countries and sort
            df2 = pd.DataFrame([('San Marino', np.nan), ('Monaco', np.nan),
                                ('Liechtenstein', np.nan)], columns=['ID', 'Wert'])
            df = pd.concat([df, df2])
            df = df.reset_index(drop=True)
            df = df.sort_values('ID')

            # create new dataframe with rounded values for Datawrapper
            dfr = df.copy()
            dfr['Wert'] = dfr['Wert'].round(0)

            # update chart
            dw_chart = dw.add_data(chart_id=dw_id, data=dfr)
            #dw.update_chart(chart_id=dw_id, title="Diese Länder importieren derzeit mehr Strom, als sie exportieren")
            date = {'annotate': {
                'notes': f'Negative Werte in Rot bedeuten Importe, positive Werte in Blau Exporte.<br><br>Stand: {dnotes}'}}
            labels = {'visualize': {'value-label-row': 'Wert'}}
            dw.update_metadata(chart_id=dw_id, properties=date)
            dw.update_metadata(chart_id=dw_id, properties=labels)
            dw.update_description(chart_id=dw_id, source_url=url_source,
                                  source_name='energy-charts.info/Entso-E', intro='Wöchentlicher grenzüberschreitender Stromhandel (Export-Import-Saldo), in GWh')
            dw.publish_chart(chart_id=dw_id, display=False)

            # create dataframe for dashboard
            df_de_new = df[df['ID'].str.contains(r'^Germany')].copy()
            df_de_new['ID'] = f'KW {dweek}'

            # data source for old data
            url = f'https://www.energy-charts.info/charts/import_export_map/data/tcs_week_{dyear_old}_{dweek_old}.json'

            # download JSON and convert to dataframe
            r = s.get(url, headers={'user-agent': headers,
                                    'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
            data = r.json()
            df = pd.json_normalize(data)
            df.columns = df.iloc[0]

            # drop first row with meta data and keep only first column with values
            df = df.iloc[1:]
            df = df.reset_index(drop=True)

            # clean-up
            renamec = {df.columns[0]: 'ID', df.columns[1]: 'Wert'}
            df = df.rename(columns=renamec)
            df = df.filter(['ID', 'Wert'])

            # replace ALPHA-2 codes with country names
            df['ID'] = df['ID'].map(iso)

            # drop empty rows and with less than 4 characters
            df = df[df['ID'].notna()]
            df = df[df['ID'].str.len() >= 3]

            # drop everything except Germany
            df = df[df['ID'] == 'Germany']
            df['ID'] = f'KW {dweek_old}'

            # concat old data to new
            df = pd.concat([df, df_de_new])
            df = df.rename({'Wert': 'value', 'ID': 'date'}, axis='columns')
            df = df.reset_index(drop=True)

            # save as csv for dashboard
            df.to_csv('./data/imports-countries-dash.csv')

        # clean-up for Q
        """
        # replace ALPHA-2 codes with country names
        iso = {'AD': 'Andorra', 'AL': 'Albania', 'AT': 'Austria', 'AL': 'Albania', 'BA': 'Bosnia and Herzegovina', 'BE': 'Belgium', 'BG': 'Bulgaria', 'CH': 'Switzerland', 'CZ': 'Czech Republic', 'DE': 'Germany', 'DE_LU': 'XX', 'DK': 'Denmark', 'EE': 'Estonia', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France', 'GR': 'Greece', 'HR': 'Croatia', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy', 'IS': 'Iceland',
               'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MD': 'Moldova', 'ME': 'Montenegro', 'MK': 'North Macedonia', 'MT': 'Malta', 'NIE': 'YY', 'NL': 'Netherlands', 'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania', 'RS': 'Serbia', 'RU': 'Russia', 'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia', 'TR': 'Turkey', 'UA': 'Ukraine', 'UA_W': 'ZZ', 'UK': 'United Kingdom', 'XK': 'Kosovo'}
        df['ID'] = df['ID'].map(iso)

        # drop empty rows and with less than 4 characters
        df = df[df['ID'].notna()]
        df = df[df['ID'].str.len() >= 3]

        # add missing countries and sort
        df2 = pd.DataFrame([('Vatican City', np.nan), ('San Marino', np.nan),
                           ('Monaco', np.nan), ('Liechtenstein', np.nan)], columns=['ID', 'Wert'])
        df = pd.concat([df, df2])
        df = df.reset_index(drop=True)
        df = df.sort_values('ID')
        """

        # create bins for Q
        """
        df3 = df[df['Wert'].notna()]
        bins = mapclassify.EqualInterval(df3["Wert"], k=6)
        print(bins)
        """

    except:
        raise
