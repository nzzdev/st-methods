import json
import os
import io
from time import sleep
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from user_agent import generate_user_agent
import numpy as np


if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *

        # read data for gas imports
        # https://www.bruegel.org/publications/datasets/european-natural-gas-imports/
        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # url = 'https://infogram.com/1pk6j01vz3dzdkc9z0er3rz7kpb3yekm3x0'  # 2022 data, see version from 24.10.2023 for old script
        urlnew = 'https://infogram.com/83b2e7a1-a4b0-47eb-acff-5530f94e6247'
        urllng = 'https://infogram.com/fb29e40e-29d2-4d11-a87c-41f497270031'
        respnew = download_data(urlnew, headers=fheaders)
        resplng = download_data(urllng, headers=fheaders)
        htmlnew = respnew.text
        htmllng = resplng.text

        # soup = BeautifulSoup(html, features='html.parser')
        soupnew = BeautifulSoup(htmlnew, features='html.parser')
        souplng = BeautifulSoup(htmllng, features='html.parser')

        # s = soup.findAll('script')
        snew = soupnew.findAll('script')
        slng = souplng.findAll('script')
        full_script_new = None
        full_script_lng = None

        # get all json data from infogram graph for 2024
        for i in range(len(snew)):
            if snew[i].contents:
                if 'window.infographicData' in snew[i].contents[0]:
                    full_script_new = snew[i].contents[0]
                    break

        full_script_new = full_script_new.lstrip('window.infographicData=')
        full_script_new = full_script_new.rstrip(';')

        full_data_new = json.loads(full_script_new)

        """
        # get charts for each country/type for 2024
        df_list_new = list()
        for data in full_data_new['elements'][2]['data']:
            headers = ['KW', 'Minimum', 'Maximum', '2022', '2023', '2024']
            del data[0]  # delete headers
            dfnew = pd.DataFrame(data, columns=headers)
            df_list_new.append(dfnew)
        """

        # get all json data from infogram graph for LNG
        for i in range(len(slng)):
            if slng[i].contents:
                if 'window.infographicData' in slng[i].contents[0]:
                    full_script_lng = slng[i].contents[0]
                    break

        full_script_lng = full_script_lng.lstrip('window.infographicData=')
        full_script_lng = full_script_lng.rstrip(';')

        full_data_lng = json.loads(full_script_lng)

        # get charts for each country/type for LNG
        df_list_lng = list()
        for data in full_data_lng['elements']['content']['content']['entities']['3a41ab1a-9ccc-40b3-a1d3-225d07a8eeb8bac6ef8b-2f7e-487e-ae9f-69e8a6bd2593']['props']['chartData']['data']:
            headers = ['KW', 'America', 'Africa',
                       'Middle East', 'Russia', 'Other']
            del data[0]  # delete headers
            del data[0]
            df_lng_new = pd.DataFrame(data, columns=headers)
            df_list_lng.append(df_lng_new)

        ########
        # LNG #
        ########
        # clean values

        # replace commas, delete strings and replace 'None' with NaN
        df_lng_new['America'] = df_lng_new['America'].astype(str).str.replace(
            '{.*?xa0 ', '', regex=True)
        df_lng_new['Africa'] = df_lng_new['Africa'].astype(str).str.replace(
            '{.*?xa0 ', '', regex=True)
        df_lng_new['Middle East'] = df_lng_new['Middle East'].astype(str).str.replace(
            '{.*?xa0 ', '', regex=True)
        df_lng_new['Russia'] = df_lng_new['Russia'].astype(str).str.replace(
            '{.*?xa0 ', '', regex=True)
        df_lng_new['Other'] = df_lng_new['Other'].astype(str).str.replace(
            '{.*?xa0 ', '', regex=True)

        df_lng_new['America'] = df_lng_new['America'].str.replace(
            '\'}', '', regex=False)
        df_lng_new['Africa'] = df_lng_new['Africa'].str.replace(
            '\'}', '', regex=False)
        df_lng_new['Middle East'] = df_lng_new['Middle East'].str.replace(
            '\'}', '', regex=False)
        df_lng_new['Russia'] = df_lng_new['Russia'].str.replace(
            '\'}', '', regex=False)
        df_lng_new['Other'] = df_lng_new['Other'].str.replace(
            '\'}', '', regex=False)
        df_lng_new['America'] = df_lng_new['America'].str.replace(
            '{\'value\': \'', '', regex=False)
        df_lng_new['Africa'] = df_lng_new['Africa'].str.replace(
            '{\'value\': \'', '', regex=False)
        df_lng_new['Middle East'] = df_lng_new['Middle East'].str.replace(
            '{\'value\': \'', '', regex=False)
        df_lng_new['Russia'] = df_lng_new['Russia'].str.replace(
            '{\'value\': \'', '', regex=False)
        df_lng_new['Other'] = df_lng_new['Other'].str.replace(
            '{\'value\': \'', '', regex=False)

        df_lng_new['America'] = df_lng_new['America'].str.replace(
            ',', '', regex=False)
        df_lng_new['Africa'] = df_lng_new['Africa'].str.replace(
            ',', '', regex=False)
        df_lng_new['Middle East'] = df_lng_new['Middle East'].str.replace(
            ',', '', regex=False)
        df_lng_new['Russia'] = df_lng_new['Russia'].str.replace(
            ',', '', regex=False)
        df_lng_new['Other'] = df_lng_new['Other'].str.replace(
            ',', '', regex=False)

        df_lng_new['America'] = df_lng_new['America'].apply(
            pd.to_numeric, errors='coerce').astype(float)
        df_lng_new['Africa'] = df_lng_new['Africa'].apply(
            pd.to_numeric, errors='coerce').astype(float)
        df_lng_new['Middle East'] = df_lng_new['Middle East'].apply(
            pd.to_numeric, errors='coerce').astype(float)
        df_lng_new['Russia'] = df_lng_new['Russia'].apply(
            pd.to_numeric, errors='coerce').astype(float)
        df_lng_new['Other'] = df_lng_new['Other'].apply(
            pd.to_numeric, errors='coerce').astype(float)
        df_lng_new['KW'] = df_lng_new['KW'].apply(
            pd.to_numeric, errors='coerce').astype(str)
        df_lng_new['KW'] = df_lng_new['KW'].str.extract(
            r'(\d{2}\/\d{4})')
        df_lng_new['KW'] = df_lng_new['KW'].astype(str).str.replace(
            '/', '-', regex=False)

        # rename and rearrange columns
        df_lng_new.rename(columns={'KW': 'Datum', 'America': 'USA', 'Africa': 'Afrika',
                          'Middle East': 'Mittlerer Osten', 'Russia': 'Russland', 'Other': 'Sonstige'}, inplace=True)
        df_lng_new = df_lng_new[['Datum', 'Russland',
                                 'USA', 'Afrika', 'Mittlerer Osten', 'Sonstige']]

        # add one month to date and create string for chart notes
        # old date fix
        # df_lng_new.set_index('Datum', inplace=True)
        # lngdate = df_lng_new['USA'].replace(r'^\s*$', np.nan, regex=True).last_valid_index()  # replace empty strings and check last non NaN value
        # lngdate = pd.to_datetime(lngdate, format='%m-%Y') + pd.DateOffset(months=1)
        df_lng_new['Datum'] = pd.to_datetime(
            df_lng_new['Datum'], errors='coerce')
        lngdate = df_lng_new['Datum'].max() + pd.DateOffset(months=1)
        df_lng_new['Datum'].replace({None: lngdate}, inplace=True)
        df_lng_new.set_index('Datum', inplace=True)
        month_str = lngdate.strftime('%-d. %-m. %Y')
        notes_chart_lng = '¹ USA mit Trinidad und Tobago. Der grösste Exporteur im Mittleren Osten ist Katar; in Afrika exportieren Nigeria und Algerien am meisten.<br>Stand: ' + month_str

        # replace NaN with empty strings
        df_lng_new = df_lng_new.fillna('')

        # run Q function
        #update_chart(id='1203f969609d721f3e48be4f2689fc53', data=df_russia_new, notes=notes_chart_new)
        # update_chart(id='4acf1a0fd4dd89aef4abaeefd04f9c8c',data=df_lng, notes=notes_chart) # for old LNG script see version from 24.10.2023
        update_chart(id='6c02e1d1daabb23cfaaae686241d6e4e',
                     data=df_lng_new, notes=notes_chart_lng)
        ### update_chart(id='78215f05ea0a73af28c0bb1c2c89f896',data=df_de, notes=notes_chart_de)

        # Nord stream 1 to DE Bundesnetzagentur
        try:
            url = 'https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081248'
            # url = 'https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=591576'  # new
            resp = download_data(url, headers=fheaders)
            csv_file = resp.text
            # read csv
            df_ns = pd.read_csv(io.StringIO(csv_file), encoding='utf-8', sep=';', decimal=',', index_col=None)
            # check if data is corrupted
            errors = 0
            while (len(df_ns) < 730) and (errors < 3):
                sleep(2)
                errors += 1
                resp = download_data(url, headers=fheaders)
                csv_file = resp.text
                df_ns = pd.read_csv(io.StringIO(csv_file), encoding='utf-8', sep=';', decimal=',', index_col=None)
            if (len(df_ns) >= 730) and (not pd.isna(df_ns.iloc[-1, -2])) and df_ns.iloc[-1, -1] > 100: # check for errors (no value in LNG, value to little in "Gesamt" etc)
                # save tsv
                # drop last row that is almost always incomplete
                df_ns.drop(df_ns.tail(1).index,inplace=True)
                df_ns.to_csv('./data/lng_imports.tsv', sep='\t', encoding='utf-8', index=False)
        except:
            pass
        # read old tsv
        df_ns = pd.read_csv('./data/lng_imports.tsv', sep='\t', index_col=None)

        # clean dataframe for NS1 and total imports
        df_total = df_ns.copy()
        df_total = df_total.drop(
            df_total.columns[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]], axis=1)
        df_ns = df_ns.drop(
            df_ns.columns[[1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12]], axis=1)

        # convert date string to datetime
        df_total[df_total.columns[0]] = pd.to_datetime(
            df_total[df_total.columns[0]], format='%d.%m.%Y')
        df_ns[df_ns.columns[0]] = pd.to_datetime(
            df_ns[df_ns.columns[0]], format='%d.%m.%Y')

        # set date as index
        df_total = df_total.set_index(df_total.columns[0])
        df_ns = df_ns.set_index(df_ns.columns[0])

        # convert total imports to terrawatts
        df_total = df_total.div(1000)

        # change column order
        df_total = df_total[['Deutschland Import', 'LNG']]
        df_total = df_total.rename(
            columns={'Deutschland Import': 'Gesamt-Importe', 'LNG': 'Direkt-Importe LNG'})

        # convert GWh to million m3 according to calorific value of Russian gas
        df_ns = (df_ns / 10.3).round(1)

        # create dynamic chart title
        if df_ns['Russland'][-1] > 0:
            chart_title = 'Über Nord Stream 1 fliesst kaum noch russisches Gas'
        else:
            chart_title = 'Über Nord Stream 1 fliesst kein russisches Gas mehr'

        # old
        # title_twh = df_total[df_total.columns[0]].iloc[-1].round(1).astype(float)
        # title_twh = title_twh.astype(str).replace('.', ',')
        # chart_title_total = f'Deutschland importiert derzeit {title_twh} TWh Gas am Tag'

        title_twh = (df_total[df_total.columns[1]].iloc[-1] /
                     df_total[df_total.columns[0]].iloc[-1]) * 100
        title_twh = title_twh.round(0).astype(int)
        chart_title_total = f'Anteil des direkt importierten LNG liegt derzeit bei {title_twh} Prozent'

        # get latest date for chart notes
        timecode = df_ns.index[-1]
        timecodestr = timecode.strftime('%-d. %-m. %Y')
        notes_chart_ns = 'Stand: ' + timecodestr
        notes_chart_total = '¹ inklusive möglicher Ringflüsse und Bestellungen aus anderen Staaten.<br>Stand: ' + timecodestr

        # rename columns and save clean csv for dashboard
        df_ns = df_ns.rename(columns={'nordstream1': 'Nord Stream 1'})
        df_ns.index = df_ns.index.rename('periodFrom')
        df_ns.to_csv('./data/pipelines_ns.tsv', sep='\t')

        # imports as percentage for dashboard
        df_dash = df_total.copy()
        df_dash['LNG'] = (df_dash[df_dash.columns[1]] /
                          df_dash[df_dash.columns[0]]) * 100
        df_dash = df_dash[['LNG']]
        df_dash.index.names = ['Datum']
        df_dash.to_csv('./data/german-imports.tsv', sep='\t', encoding='utf-8')

        # run Q function
        update_chart(id='78215f05ea0a73af28c0bb1c2c89f896',
                     data=df_ns, notes=notes_chart_ns, title=chart_title)
        update_chart(id='85c9e635bfeae3a127d9c9db90dfb2c5', data=df_total,
                     notes=notes_chart_total, title=chart_title_total)

    except:
        raise
