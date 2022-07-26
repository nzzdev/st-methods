import json
import os
from datetime import datetime, timedelta
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from user_agent import generate_user_agent

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *

        # read data for gas imports
        # https://www.bruegel.org/publications/datasets/european-natural-gas-imports/
        fheaders = {'user-agent': generate_user_agent()}
        url = 'https://infogram.com/1pk6j01vz3dzdkc9z0er3rz7kpb3yekm3x0'
        resp = download_data(url, headers=fheaders)
        html = resp.text

        soup = BeautifulSoup(html, features='html.parser')

        s = soup.findAll('script')
        full_script = None

        # get all json data from infogram graph
        for i in range(len(s)):
            if s[i].contents:
                if 'window.infographicData' in s[i].contents[0]:
                    full_script = s[i].contents[0]
                    break

        full_script = full_script.lstrip('window.infographicData=')
        full_script = full_script.rstrip(';')

        full_data = json.loads(full_script)

        # get charts for each country/type
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

        # format week numbers as date values and drop column '2021'
        df_russia.iloc[:, 0] = '2022-W' + df_russia.iloc[:, 0].astype(str)
        df_lng.iloc[:, 0] = '2022-W' + df_lng.iloc[:, 0].astype(str)
        df_russia.drop(df_russia.columns[3], axis=1, inplace=True)
        df_lng.drop(df_lng.columns[3], axis=1, inplace=True)

        # replace 'None' string with NaN and drop last row (KW53)
        cols = ['Minimum', 'Maximum', '2022']
        df_lng[cols] = df_lng[cols].apply(
            pd.to_numeric, errors='coerce', axis=1)
        df_russia[cols] = df_russia[cols].apply(
            pd.to_numeric, errors='coerce', axis=1)
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
        weekno = df_russia['2022'].last_valid_index()  # last non NaN value
        weekno_dt = datetime.strptime(
            weekno + '-1', '%Y-W%W-%w') + timedelta(days=7)  # get monday from next week
        weekno_str = weekno_dt.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Maximum/Minimum der Importe 2015–2020.<br>Stand: ' + weekno_str

        # replace NaN with empty strings for Q
        df_lng.fillna('', inplace=True)
        df_russia.fillna('', inplace=True)

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
        #df_de.index = df_de.index.strftime('%Y-%m-%d')
        # END OLD
        """

        url_de = 'https://static.dwcdn.net/data/kCrqD.csv'
        resp = download_data(url_de, headers=fheaders)
        csv_file = resp.content
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'pipelines_de.csv'), 'wb') as f:
            f.write(csv_file)

        # read csv and convert to datetime, add one day
        df_new = pd.read_csv('./data/pipelines_de.csv',
                             encoding='utf-8', index_col='periodFrom')
        df_new_sum = pd.read_csv(
            './data/pipelines_de.csv', encoding='utf-8', index_col='periodFrom')

        # rename columns
        df_new = df_new.rename(columns={
                               df_new.columns[0]: 'Mallnow', df_new.columns[1]: 'Waidhaus', df_new.columns[2]: 'Greifswald (Nord Stream 1)'})

        # calculate sum of all pipelines and drop columns
        df_new_sum['Summe'] = df_new_sum.sum(axis=1)
        df_new_sum = df_new_sum[['Summe']]

        # convert kWh to million m3 according to calorific value of Russian gas
        df_new = (df_new / 10.3).round(1)
        df_new_sum = (df_new_sum / 10.3).round(1)

        # convert dates to DatetimeIndex and sum values
        df_new.index = pd.to_datetime(df_new.index)
        df_new_sum.index = pd.to_datetime(df_new_sum.index)

        # create date for chart notes
        timecode = df_new.index[-1]
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart_de = 'Stand: ' + timecode_str

        # convert DatetimeIndex to string
        df_new.index = df_new.index.strftime('%Y-%m-%d')
        df_new_sum.index = df_new_sum.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(id='1203f969609d721f3e48be4f2689fc53',
                     data=df_russia, notes=notes_chart)
        update_chart(id='4acf1a0fd4dd89aef4abaeefd04f9c8c',
                     data=df_lng, notes=notes_chart)
        #update_chart(id='78215f05ea0a73af28c0bb1c2c89f896',data=df_de, notes=notes_chart_de)
        update_chart(id='78215f05ea0a73af28c0bb1c2c89f896',
                     data=df_new_sum, notes=notes_chart_de)
        update_chart(id='d0be298e35165ab925d7292335b3d00e',
                     data=df_new, notes=notes_chart_de)

    except:
        raise
