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

        url = 'https://infogram.com/1pk6j01vz3dzdkc9z0er3rz7kpb3yekm3x0'  # 2022 data
        urlnew = 'https://infogram.com/83b2e7a1-a4b0-47eb-acff-5530f94e6247'
        resp = download_data(url, headers=fheaders)
        respnew = download_data(urlnew, headers=fheaders)
        html = resp.text
        htmlnew = respnew.text

        soup = BeautifulSoup(html, features='html.parser')
        soupnew = BeautifulSoup(htmlnew, features='html.parser')

        s = soup.findAll('script')
        snew = soupnew.findAll('script')
        full_script = None
        full_script_new = None

        # get all json data from infogram graph for 2022
        for i in range(len(s)):
            if s[i].contents:
                if 'window.infographicData' in s[i].contents[0]:
                    full_script = s[i].contents[0]
                    break

        full_script = full_script.lstrip('window.infographicData=')
        full_script = full_script.rstrip(';')

        full_data = json.loads(full_script)

        # get charts for each country/type for 2022
        df_list = list()
        for data in full_data['elements'][2]['data']:
            headers = data.pop(0)
            df = pd.DataFrame(data, columns=headers)
            df_list.append(df)

        df_total = df_list[0]
        df_russia = df_list[1]
        df_norway = df_list[2]
        df_lng = df_list[3]
        df_algeria = df_list[4]

        # get all json data from infogram graph for 2023
        for i in range(len(snew)):
            if snew[i].contents:
                if 'window.infographicData' in snew[i].contents[0]:
                    full_script_new = snew[i].contents[0]
                    break

        full_script_new = full_script_new.lstrip('window.infographicData=')
        full_script_new = full_script_new.rstrip(';')

        full_data_new = json.loads(full_script_new)

        # get charts for each country/type for 2023
        df_list_new = list()
        for data in full_data_new['elements'][2]['data']:
            headers = ['KW', 'Minimum', 'Maximum', '2021', '2022', '2023']
            del data[0]  # delete headers
            dfnew = pd.DataFrame(data, columns=headers)
            df_list_new.append(dfnew)

        # format week numbers as date values and drop column '2021'
        df_russia.iloc[:, 0] = '2022-W' + df_russia.iloc[:, 0].astype(str)
        df_lng.iloc[:, 0] = '2022-W' + df_lng.iloc[:, 0].astype(str)
        df_russia.drop(df_russia.columns[3], axis=1, inplace=True)
        df_lng.drop(df_lng.columns[3], axis=1, inplace=True)

        # replace commas and 'None' string with NaN and drop last row (KW53)
        cols = ['Minimum', 'Maximum', '2022']
        df_lng[cols] = df_lng[cols].replace(',', '', regex=True)
        df_russia[cols] = df_russia[cols].replace(',', '', regex=True)
        # df_lng[cols] = df_lng[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        # df_russia[cols] = df_russia[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        df_lng.drop(df_lng.tail(1).index, inplace=True)
        df_russia.drop(df_russia.tail(1).index, inplace=True)

        # add means (2015-2020) and EU goal to dataframes
        mean = [1378.4, 1397.4, 1279.5, 1426.7, 1265.9, 1373.7, 1376.8, 1373.1, 1537.4, 1506.3, 1464.8, 1572.2, 1504.6, 1603.7, 1554.5, 1557.7, 1588.3, 1588.5, 1561.5, 1495.8, 1492.1, 1349.8, 1244, 1250, 1197,
                1222.2, 1252.1, 1296, 1309.3, 1294.7, 1174.3, 1084.6, 1104.4, 1198.9, 1226.5, 1232, 1182.4, 1178.5, 1155.4, 1191, 1255.1, 1396.4, 1282.7, 1499.9, 1547.2, 1530.6, 1622.4, 1714.2, 1631.5, 1581.2, 1435.3, 1253]
        df_lng = df_lng.assign(mean=mean)
        mean = [3328, 3094.3, 3088.1, 3014.6, 2911.4, 3038.8, 3027.1, 3011, 2963.7, 3070.3, 3170.8, 3136.5, 3098.3, 3157.6, 3179.3, 3213.6, 3236.8, 3218.9, 3307.9, 3264.1, 3201.4, 3148.8, 3188, 3236.1, 3230.7, 3268.5,
                3268.9, 3109.5, 2955.5, 2872.1, 3359.9, 3133.8, 3076.9, 3129.1, 3294.7, 3335.8, 3217.8, 3258.2, 3325.1, 3267.8, 3339.5, 3385.6, 3451.4, 3416.2, 3431.7, 3502.2, 3575.8, 3556.3, 3520.5, 3548.2, 3513.1, 3422.2]
        df_russia = df_russia.assign(mean=mean)

        # old EU goal with mean instead 2021
        # eugoal = [1131.52, 1052.062, 1049.954, 1024.964, 989.876, 1033.192, 1029.214, 1023.74, 1007.658, 1043.902, 1078.072, 1066.41, 1053.422, 1073.584, 1080.962, 1092.624, 1100.512, 1094.426, 1124.686, 1109.794, 1088.476, 1070.592, 1083.92, 1100.274, 1098.438, 1111.29, 1111.426, 1057.23, 1004.87, 976.514, 1142.366, 1065.492, 1046.146, 1063.894, 1120.198, 1134.172, 1094.052, 1107.788, 1130.534, 1111.052, 1135.43, 1151.104, 1173.476, 1161.508, 1166.778, 1190.748, 1215.772, 1209.142, 1196.97, 1206.388, 1194.454, 1163.548]

        eugoal = [1118.702, 1040.366, 1073.278, 1067.872, 1073.074, 1081.948, 1082.594, 975.834, 916.13, 1055.394, 1044.718, 1076.95, 1086.096, 1067.294, 1037.17, 1050.226, 1070.014, 1076.678, 1081.302, 1082.9, 1082.662, 1100.954, 1075.658, 1046.01, 1091.332,
                  1003.612, 1054.068, 934.218, 712.64, 829.056, 1041.59, 932.518, 904.026, 924.596, 1018.062, 947.512, 914.362, 979.098, 998.376, 873.732, 886.754, 876.962, 857.888, 855.61, 755.99, 885.326, 940.712, 946.458, 953.462, 961.622, 943.058, 874.616]
        eugoalmean = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000,
                      1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]
        num2021 = [3290, 3060, 3157, 3141, 3156, 3182, 3184, 2870, 2694, 3104, 3073, 3168, 3194, 3139, 3051, 3089, 3147, 3167, 3180, 3185, 3184, 3238, 3164, 3077, 3210,
                   2952, 3100, 2748, 2096, 2438, 3064, 2743, 2659, 2719, 2994, 2787, 2689, 2880, 2936, 2570, 2608, 2579, 2523, 2517, 2224, 2604, 2767, 2784, 2804, 2828, 2774, 2572]
        num2022 = [1746, 1796, 1757, 1943, 2208, 2024, 1922, 2323, 2621, 2606, 2268, 2411, 2529, 2313, 2083, 1931, 1895, 2262, 1998, 1784, 1664, 1602, 1513,
                   1110, 851, 1055, 1059, 609, 923, 947, 836, 845, 853, 849, 656, 587, 599, 573, 532, 521, 558, 536, 435, 407, 496, 593, 598, 657, 709, 727, 564, 526]
        df_russia = df_russia.assign(eugoal=eugoal)

        # rearrange and rename columns
        df_lng = df_lng[['country', 'Minimum', 'Maximum', 'mean', '2022']]
        df_lng.rename(columns={'country': 'Datum', 'Minimum': '',
                      'Maximum': 'Höchst-/Tiefststand¹', 'mean': '5-Jahres-Mittel'}, inplace=True)
        df_russia = df_russia[['country', 'Minimum',
                               'Maximum', 'mean', '2022', 'eugoal']]
        df_russia.rename(columns={'country': 'Datum', 'Minimum': '', 'Maximum': 'Höchst-/Tiefststand¹',
                         'mean': '5-Jahres-Mittel', 'eugoal': 'EU-Ziel'}, inplace=True)

        # set week number as index and create date for chart notes
        df_lng.set_index('Datum', inplace=True)
        df_russia.set_index('Datum', inplace=True)
        weekno = df_russia['2022'].replace(
            r'^\s*$', np.nan, regex=True).last_valid_index()  # replace empty strings and check last non NaN value
        weekno_dt = datetime.strptime(
            weekno + '-1', '%Y-W%W-%w') + timedelta(days=7)  # get monday from next week
        weekno_str = weekno_dt.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Maximum/Minimum der Importe 2015–2020.<br>Stand: ' + weekno_str

        # replace NaN with empty strings for Q
        df_lng.fillna('', inplace=True)
        df_russia.fillna('', inplace=True)

        ########
        # 2023 #
        ########
        # get values for Russia 2023
        df_russia_new = df_list_new[1].copy()
        # replace commas, delete strings and replace 'None' with NaN
        df_russia_new['Minimum'] = df_russia_new['Minimum'].astype(str).str.replace(
            '{.*?xa0 ', '', regex=True)
        df_russia_new['Maximum'] = df_russia_new['Maximum'].astype(str).str.replace(
            '{.*?xa0 ', '', regex=True)
        df_russia_new['Minimum'] = df_russia_new['Minimum'].str.replace(
            '\'}', '', regex=False)
        df_russia_new['Maximum'] = df_russia_new['Maximum'].str.replace(
            '\'}', '', regex=False)
        df_russia_new['Minimum'] = df_russia_new['Minimum'].str.replace(
            ',', '', regex=False)
        df_russia_new['Maximum'] = df_russia_new['Maximum'].str.replace(
            ',', '', regex=False)
        df_russia_new['Minimum'] = df_russia_new['Minimum'].apply(
            pd.to_numeric, errors='coerce').astype(float)
        df_russia_new['Maximum'] = df_russia_new['Maximum'].apply(
            pd.to_numeric, errors='coerce').astype(float)
        df_russia_new['2023'] = df_russia_new['2023'].apply(
            pd.to_numeric, errors='coerce').astype(str)
        df_russia_new['2023'] = df_russia_new['2023'].str.replace(
            ',', '', regex=False)
        df_russia_new['KW'] = df_russia_new['KW'].apply(
            pd.to_numeric, errors='coerce').astype(str)
        df_russia_new['2023'] = df_russia_new['2023'].str.extract(
            r'(\d+)').astype(float)
        df_russia_new['KW'] = df_russia_new['KW'].str.extract(
            r'(\d+)').astype(int)
        df_russia_new = df_russia_new[['KW', '2023']]

        # fix date
        df_russia_new.iloc[:, 0] = '2023-W' + \
            df_russia_new.iloc[:, 0].astype(str)

        # drop last KW row and add mean and EU goal
        df_russia_new = df_russia_new.drop(df_russia_new.tail(1).index)
        #df_russia_new = df_russia_new.assign(mean=mean)
        #df_russia_new = df_russia_new.assign(eugoal=eugoal)

        # rename and rearrange columns
        df_russia_new = df_russia_new.assign(num2021=num2021)
        df_russia_new = df_russia_new.assign(num2022=num2022)
        df_russia_new = df_russia_new[[
            'KW', 'num2021', 'num2022', '2023']]
        df_russia_new.rename(
            columns={'KW': 'Datum', 'num2021': '2021', 'num2022': '2022'}, inplace=True)

        # set week number as index and create date for chart notes
        df_russia_new.set_index('Datum', inplace=True)
        weekno = df_russia_new['2023'].replace(
            r'^\s*$', np.nan, regex=True).last_valid_index()  # replace empty strings and check last non NaN value
        weekno_dt = datetime.strptime(
            weekno + '-1', '%Y-W%W-%w') + timedelta(days=7)  # get monday from next week
        weekno_str = weekno_dt.strftime('%-d. %-m. %Y')
        notes_chart_new = 'EU-Ziel: Reduktion der Lieferungen bis Ende 2022 auf ungefähr 1000 Mio. m³.<br>Stand: ' + weekno_str

        # replace NaN with empty strings
        df_russia_new.fillna('', inplace=True)

        # run Q function
        update_chart(id='1203f969609d721f3e48be4f2689fc53',
                     data=df_russia_new, notes=notes_chart_new)
        update_chart(id='4acf1a0fd4dd89aef4abaeefd04f9c8c',
                     data=df_lng, notes=notes_chart)
        #update_chart(id='78215f05ea0a73af28c0bb1c2c89f896',data=df_de, notes=notes_chart_de)

        # Nord stream 1 to DE Bundesnetzagentur
        url = 'https://www.bundesnetzagentur.de/_tools/SVG/js2/_functions/csv_export.html?view=renderCSV&id=1081248'
        resp = download_data(url, headers=fheaders)
        csv_file = resp.text

        # read csv
        df_ns = pd.read_csv(io.StringIO(csv_file), encoding='utf-8',
                            sep=';', decimal=',', index_col=None)

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
        df_dash.to_csv('./data/german-imports.csv')

        # run Q function
        update_chart(id='78215f05ea0a73af28c0bb1c2c89f896',
                     data=df_ns, notes=notes_chart_ns, title=chart_title)
        update_chart(id='85c9e635bfeae3a127d9c9db90dfb2c5', data=df_total,
                     notes=notes_chart_total, title=chart_title_total)

        """
        # OLD
        # create dates for Russian gas flows in Germany
        today = date.today()
        yesterday = today - timedelta(days=1)
        todaystr = today.strftime('%Y-%m-%d')
        yesterdaystr = yesterday.strftime('%Y-%m-%d')
        startstr = '2022-02-01'

        # read data for Russiand gas flows in Germany
        url = f'https://transparency.entsog.eu/api/v1/aggregateddata.csv?forceDownload=true&from={startstr}&to={yesterdaystr}&indicator=Physical%20Flow&periodType=day&timezone=CET&limit=-1&delimiter=comma&countryKey=DE&directionKey=entry&pointsNames=Mallnow,VIP%20Waidhaus|Waidhaus%20(OGE),Greifswald%20/%20OPAL,Greifswald%20/%20NEL'

        url_jamal = f'https://transparency.entsog.eu/api/v1/aggregateddata.csv?forceDownload=true&from={startstr}&to={yesterdaystr}&indicator=Physical%20Flow&periodType=day&timezone=CET&limit=-1&delimiter=comma&countryKey=DE&directionKey=entry&pointsNames=Mallnow'

        url_megal = f'https://transparency.entsog.eu/api/v1/aggregateddata.csv?forceDownload=true&from={startstr}&to={yesterdaystr}&indicator=Physical%20Flow&periodType=day&timezone=CET&limit=-1&delimiter=comma&countryKey=DE&directionKey=entry&pointsNames=VIP%20Waidhaus|Waidhaus%20(OGE)'

        url_nstream = f'https://transparency.entsog.eu/api/v1/aggregateddata.csv?forceDownload=true&from={startstr}&to={yesterdaystr}&indicator=Physical%20Flow&periodType=day&timezone=CET&limit=-1&delimiter=comma&countryKey=DE&directionKey=entry&pointsNames=Greifswald%20/%20OPAL,Greifswald%20/%20NEL'

        # duplicate flows Megal pipeline/Waidhaus (exit to Czechia until March 31st)
        url_exit1 = f'https://transparency.entsog.eu/api/v1/aggregateddata.csv?forceDownload=true&from={startstr}&to=2022-03-31&indicator=Physical%20Flow&periodType=day&timezone=CET&limit=-1&delimiter=comma&countryKey=DE&directionKey=exit&pointsNames=Brandov%20/%20OPAL'

        # duplicate flows Megal pipeline/Waidhaus (exit to Czechia from April 1st)
        url_exit2 = f'https://transparency.entsog.eu/api/v1/aggregateddata.csv?forceDownload=true&from=2022-04-01&to={yesterdaystr}&indicator=Physical%20Flow&periodType=day&timezone=CET&limit=-1&delimiter=comma&countryKey=DE&directionKey=exit&pointsNames=Brandov-OPAL%20(DE)'

        # save data
        with open(os.path.join('data', 'gas_de.csv'), 'wb') as f:
            f.write(download_data(url, headers=fheaders).content)
        with open(os.path.join('data', 'gas_jamal.csv'), 'wb') as f:
            f.write(download_data(url_jamal, headers=fheaders).content)
        with open(os.path.join('data', 'gas_megal.csv'), 'wb') as f:
            f.write(download_data(url_megal, headers=fheaders).content)
        with open(os.path.join('data', 'gas_nstream.csv'), 'wb') as f:
            f.write(download_data(url_nstream, headers=fheaders).content)
        with open(os.path.join('data', 'gas_de_exit1.csv'), 'wb') as f:
            f.write(download_data(url_exit1, headers=fheaders).content)
        with open(os.path.join('data', 'gas_de_exit2.csv'), 'wb') as f:
            f.write(download_data(url_exit2, headers=fheaders).content)

        # read data
        df_de = pd.read_csv('./data/gas_de.csv',
                            encoding='utf-8', usecols=['periodFrom', 'value'])
        df_jamal = pd.read_csv('./data/gas_jamal.csv',
                               encoding='utf-8', usecols=['periodFrom', 'value'])
        df_megal = pd.read_csv('./data/gas_megal.csv',
                               encoding='utf-8', usecols=['periodFrom', 'value'])
        df_nstream = pd.read_csv('./data/gas_nstream.csv',
                                 encoding='utf-8', usecols=['periodFrom', 'value'])
        df_exit1 = pd.read_csv('./data/gas_de_exit1.csv',
                               encoding='utf-8', usecols=['periodFrom', 'value'])
        df_exit2 = pd.read_csv('./data/gas_de_exit2.csv',
                               encoding='utf-8', usecols=['periodFrom', 'value'])

        # rename columns
        df_jamal = df_jamal.rename(columns={'value': 'Jamal'})
        df_megal = df_megal.rename(columns={'value': 'Megal'})
        df_nstream = df_nstream.rename(columns={'value': 'Nord Stream 1'})

        # convert dates to DatetimeIndex and sum values
        df_de['periodFrom'] = pd.to_datetime(
            df_de['periodFrom'], dayfirst=True)
        df_de.set_index(df_de['periodFrom'], inplace=True)
        df_de = df_de.resample("D").sum()

        df_jamal['periodFrom'] = pd.to_datetime(
            df_jamal['periodFrom'], dayfirst=True)
        df_jamal.set_index(df_jamal['periodFrom'], inplace=True)
        df_jamal = df_jamal.resample("D").sum()

        df_megal['periodFrom'] = pd.to_datetime(
            df_megal['periodFrom'], dayfirst=True)
        df_megal.set_index(df_megal['periodFrom'], inplace=True)
        df_megal = df_megal.resample("D").sum()

        df_nstream['periodFrom'] = pd.to_datetime(
            df_nstream['periodFrom'], dayfirst=True)
        df_nstream.set_index(df_nstream['periodFrom'], inplace=True)
        df_nstream = df_nstream.resample("D").sum()

        df_exit1['periodFrom'] = pd.to_datetime(
            df_exit1['periodFrom'], dayfirst=True)
        df_exit1.set_index(df_exit1['periodFrom'], inplace=True)
        df_exit1 = df_exit1.resample("D").sum()
        df_exit2['periodFrom'] = pd.to_datetime(
            df_exit2['periodFrom'], dayfirst=True)
        df_exit2.set_index(df_exit2['periodFrom'], inplace=True)
        df_exit2 = df_exit2.resample("D").sum()

        # join dataframes with duplicate flows and subtract
        df_exit = pd.concat([df_exit1, df_exit2], join='outer', axis=0)
        df_de['value'] = df_de['value'] - df_exit['value']
        df_megal['Megal'] = df_megal['Megal'] - df_exit['value']

        # drop NaN
        df_de = df_de[df_de['value'].notna()]
        df_jamal = df_jamal[df_jamal['Jamal'].notna()]
        df_megal = df_megal[df_megal['Megal'].notna()]
        df_nstream = df_nstream[df_nstream['Nord Stream 1'].notna()]

        # convert kWh to million m3 according to calorific value of Russian gas
        df_de['value'] = (df_de['value'] / 10300000).round(1)
        df_jamal['Jamal'] = (df_jamal['Jamal'] / 10300000).round(1)
        df_megal['Megal'] = (df_megal['Megal'] / 10300000).round(1)
        df_nstream['Nord Stream 1'] = (
            df_nstream['Nord Stream 1'] / 10300000).round(1)

        # join dataframes for pipeline chart
        df_de2 = pd.concat([df_jamal, df_megal, df_nstream],
                           join='outer', axis=1)

        # replace negative numbers with zero
        df_de = df_de.clip(lower=0)
        df_de2 = df_de2.clip(lower=0)

        # create date for chart notes
        timecode = df_de.index[-1]
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart_de = 'Stand: ' + timecode_str

        # convert DatetimeIndex to string
        # df_de.index = df_de.index.strftime('%Y-%m-%d')
        # END OLD
        """

    except:
        raise
