

import pandas as pd
import requests_html
from datetime import date, datetime, timedelta
import re
import yfinance as yf
from bs4 import BeautifulSoup
from html_table_parser.parser import HTMLTableParser
#import msoffcrypto
import requests
import urllib.request
import os
#import sys
from fake_useragent import UserAgent
from deep_translator import GoogleTranslator
from pandas_datareader import data as yahoo_data



from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))


# Monitoring Consumption Switzerland

consum_ch = pd.read_csv("https://drive.switch.ch/index.php/s/yLISs3KVE7ASE68/download?path=%2F1_OVERVIEW%20DATA&files=MCS_Overview_Data.csv")
consum_ch = consum_ch[consum_ch['TRANSACTIONS'] != 'ATM_DEPOSIT']
consum_ch['DATE'] = pd.to_datetime(consum_ch['DATE'], format = '%Y-%m-%d')

consum_ch['week'] = consum_ch['DATE'].dt.isocalendar().week
consum_ch['year'] = consum_ch['DATE'].dt.year
consum_ch.loc[(consum_ch.week == 52) & (consum_ch.year == 2022), 'year'] = '2021'
consum_ch.loc[(consum_ch.week == 53) & (consum_ch.year == 2021), 'year'] = '2020'

consum_ch = consum_ch[['week', 'year', 'AMOUNTCHF']].groupby(['week', 'year']).sum().reset_index()


consum_ch_2019 = consum_ch[(consum_ch['year'] == 2019) & (consum_ch['week'] >= 1) ][['week', 'AMOUNTCHF']]
consum_ch_2020 = consum_ch[(consum_ch['year'] == 2020) & (consum_ch['week'] >= 1) ][['week', 'AMOUNTCHF']]
consum_ch_2021 = consum_ch[(consum_ch['year'] == 2021) & (consum_ch['week'] >= 1) ][['week', 'AMOUNTCHF']]
consum_ch_2022 = consum_ch[(consum_ch['year'] == 2022) & (consum_ch['week'] >= 1) ][['week', 'AMOUNTCHF']]

consum_ch_2019.rename(columns = {'AMOUNTCHF': '2019'}, inplace = True)
consum_ch_2020.rename(columns = {'AMOUNTCHF': '2020'}, inplace = True)
consum_ch_2021.rename(columns = {'AMOUNTCHF': '2021'}, inplace = True)
consum_ch_2022.rename(columns = {'AMOUNTCHF': '2022'}, inplace = True)


q_data = consum_ch_2020.merge(consum_ch_2021, on = 'week')
q_data = q_data.merge(consum_ch_2022, on = 'week', how = 'outer')
q_data['KW'] = '2022-W' + q_data['week'].astype(str)
q_data = q_data[['KW', '2020', '2021', '2022']]

update_chart(id='909e73515b8785336ef65c05d0fa36c7', data=q_data)


# Zurich traffic

zurich_2022 = pd.read_csv(
    'https://data.stadt-zuerich.ch/dataset/sid_dav_verkehrszaehlung_miv_od2031/download/sid_dav_verkehrszaehlung_miv_OD2031_2022.csv')
zurich_2022['date'] = zurich_2022['MessungDatZeit'].str[:10]
zurich_2022['date'] = pd.to_datetime(zurich_2022['date'], format='%Y-%m-%d')
zurich_2022.set_index('date', inplace=True)
zurich_2022 = zurich_2022.groupby(zurich_2022.index)[
    'AnzFahrzeuge'].sum().rolling(30).mean().reset_index()

zurich_2019 = pd.read_csv(
    'https://data.stadt-zuerich.ch/dataset/sid_dav_verkehrszaehlung_miv_od2031/download/sid_dav_verkehrszaehlung_miv_OD2031_2019.csv')
zurich_2019['date'] = zurich_2019['MessungDatZeit'].str[:10]
zurich_2019['date'] = pd.to_datetime(zurich_2019['date'], format='%Y-%m-%d')
zurich_2019.set_index('date', inplace=True)
zurich_2019 = zurich_2019.groupby(zurich_2019.index)[
    'AnzFahrzeuge'].sum().rolling(30).mean().reset_index()

zurich_2022['month'] = zurich_2022['date'].dt.month
zurich_2019['month'] = zurich_2019['date'].dt.month
zurich_2022['day'] = zurich_2022['date'].dt.day
zurich_2019['day'] = zurich_2019['date'].dt.day

zurich_2022.rename(columns = {'AnzFahrzeuge': '2022'}, inplace = True)
zurich_2019.rename(columns = {'AnzFahrzeuge': '2019'}, inplace = True)
zurich_2019 = zurich_2019[['month', 'day', '2019']]

to_q = zurich_2019.merge(zurich_2022, on = ['day', 'month'])
to_q = to_q[['date', '2019', '2022']]

notes = 'Fahrzeuge können mehrfach gezählt werden.'
update_chart(id='5b6e24348e8d8ddd990c10892047973d', data=to_q, notes = notes)


# Mobis

#mobis = pd.read_csv(
 #   'https://ivtmobis.ethz.ch/mobis/covid19/reports/data/kilometers_by_transport_mode.csv')
#mobis['date'] = pd.to_datetime(mobis['week_start'])
#mobis['pc_change'] = mobis['pc_change']*100
#mobis = mobis[(mobis['Mode'] == 'Car') & (
 #   mobis['date'] >= '2022-01-01')][['date', 'pc_change']]

#update_chart(id='bb539ba7d067f90f4fb7622d10044d91', data=mobis)


# LKW

lkw = pd.read_excel('https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Industrie-Verarbeitendes-Gewerbe/Tabellen/Lkw-Maut-Fahrleistungsindex-Daten.xlsx?__blob=publicationFile', sheet_name='Daten')
lkw = lkw[4:]
new_header = lkw.iloc[0]
lkw = lkw[1:]
lkw.columns = new_header
lkw = lkw[['Datum', 'gleitender 7-Tage-Durchschnitt KSB']]
lkw['Datum'] = pd.to_datetime(lkw['Datum'])
lkw = lkw.rename_axis(None, axis=1)

lkw_2022 = lkw.loc[lkw['Datum'] >= '2022-01-01'].copy()
lkw_2019 = lkw.loc[(lkw['Datum'].dt.date >= date(2022, 1, 1) - timedelta(366) - timedelta(2*365)) &
                   (lkw['Datum'].dt.date <= date(2022, 12, 31) -
                    timedelta(366) - timedelta(2*365))
                   ].copy()

lkw_2019['Datum'] = lkw_2019['Datum'].dt.date + \
    timedelta(366) + timedelta(2*365)
lkw_2022['Datum'] = lkw_2022['Datum'].dt.date

lkw_2019.rename(
    columns={'gleitender 7-Tage-Durchschnitt KSB': '2019'}, inplace=True)
lkw_2022.rename(
    columns={'gleitender 7-Tage-Durchschnitt KSB': '2022'}, inplace=True)

lkw = lkw_2019.merge(lkw_2022, on='Datum', how='outer')
#lkw.set_index('Datum', inplace=True)
#lkw.index = pd.to_datetime(lkw.index).strftime('%Y-%m-%d')

update_chart(id='5ac628c4bb388d36fb2f5cbc7441bfc7', data=lkw)


# Flugdaten

zh = pd.read_csv(
    'https://raw.githubusercontent.com/KOF-ch/economic-monitoring/master/data/ch.zrh_airport.departures.csv')

zh['time'] = pd.to_datetime(zh['time'])
zh = zh.loc[(zh['rnwy'] == 'all') & (zh['route'] == 'total') & (
    zh['time'] >= '2019-01-01') & (zh['time'].dt.date <= date.today())]
zh = zh[['time', 'value']]
zh = zh.set_index('time')
zh = zh.rolling(7).mean().reset_index()
zh_2022 = zh.loc[zh['time'] >= '2022-01-01'].copy()
zh_2019 = zh.loc[(zh['time'].dt.date >= date(2022, 1, 1) - timedelta(366) - timedelta(2*365)) &
                 (zh['time'].dt.date <= date(2022, 12, 31) -
                  timedelta(366) - timedelta(2*365))
                 ].copy()
zh_2019['time'] = zh_2019['time'].dt.date + timedelta(366) + timedelta(2*365)
zh_2022['time'] = zh_2022['time'].dt.date
zh_2019.rename(columns={'value': '2019'}, inplace=True)
zh_2022.rename(columns={'value': '2022'}, inplace=True)
zh = zh_2019.merge(zh_2022, on='time', how='outer')
#zh.set_index('time', inplace=True)
#zh.index = pd.to_datetime(zh.index).strftime('%Y-%m-%d')

update_chart(id='6aa31459fbbb1211b5ec05508a5413ca', data=zh)

url = 'https://www.adv.aero/corona-pandemie/woechentliche-verkehrszahlen/'
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find('table', class_="alignleft")

data = []
rows = results.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])

passagiere = pd.DataFrame(data[1:], columns=['KW in 2022', '2019_datum',
                          '2021_datum', '2022_datum', '2019', '2021', '2022', '%22/21', '%22/19'])
passagiere = passagiere[['KW in 2022', '2019', '2022']].copy()

passagiere['2019'] = pd.to_numeric(
    passagiere['2019'].str.replace('.', '', regex=False))
passagiere['2022'] = pd.to_numeric(
    passagiere['2022'].str.replace('.', '', regex=False))
passagiere['KW in 2022'] = pd.to_numeric(passagiere['KW in 2022'])
passagiere.loc[passagiere['KW in 2022'] < 10,
               'KW'] = '2022-W0' + passagiere['KW in 2022'].astype(str)
passagiere.loc[passagiere['KW in 2022'] >= 10,
               'KW'] = '2022-W' + passagiere['KW in 2022'].astype(str)

passagiere = passagiere[['KW', '2019', '2022']].copy()
#passagiere.set_index('KW', inplace=True)

update_chart(id='7a53d2e458b7ba35c25526a2c21d3956',
             data=passagiere)


# Sanktionen

timeline = pd.read_csv(
    'https://raw.githubusercontent.com/correctiv/ru-sanctions-dashboard/main/src/data/sanctions_timeline_2014-2022.csv')
#timeline.set_index('start', inplace=True)
#timeline.index = pd.to_datetime(timeline.index).strftime('%Y-%m-%d')

update_chart(id='2a1327d75c83a9c4ea49f935dd3705ef',
             data=timeline)

origin = pd.read_csv(
    'https://raw.githubusercontent.com/correctiv/ru-sanctions-dashboard/main/src/data/recent_origin_aggregation_table.csv')
origin = origin.iloc[1:, :]
cols = origin.iloc[:, 1:].columns.tolist()
origin['start'] = pd.to_datetime(origin.start)

origin[cols] = origin[cols].apply(pd.to_numeric, errors='coerce')

origin['all'] = origin.iloc[:, 1:].sum(axis=1)
origin = origin[['start', 'all']].sort_values(by='start')

#origin.set_index('start', inplace=True)
#origin.index = pd.to_datetime(origin.index).strftime('%Y-%m-%d')

update_chart(id='85c353bb11cc62672a227f886950b782', data=origin)


# Energie

url = 'https://www.tcs.ch/de/camping-reisen/reiseinformationen/wissenswertes/fahrkosten-gebuehren/benzinpreise.php'

# Opens a website and read its binary contents (HTTP Response Body)

def url_get_contents(url):

    # making request to the website
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)

    # reading contents of the website
    return f.read()


# defining the html contents of a URL.
xhtml = url_get_contents(url).decode('utf-8')

# Defining the HTMLTableParser object
p = HTMLTableParser()

# feeding the html contents in the HTMLTableParser object
p.feed(xhtml)

benzin = pd.DataFrame(p.tables[2]).dropna()
benzin.columns = benzin.iloc[0]
benzin = benzin[1:]
benzin = benzin[benzin.Reiseziel != 'Russland']

benzin['95'] = pd.to_numeric(benzin['95']).round(2)
benzin['Diesel'] = pd.to_numeric(benzin['Diesel']).round(2)
benzin['95-E10'] = pd.to_numeric(benzin['95-E10']).round(2)
benzin.loc[benzin['95'].isna(), '95'] = benzin['95-E10']
benzin.rename(columns={'95': 'Benzin'}, inplace=True)

benzin_table = benzin[['Reiseziel', 'Benzin', 'Diesel']]
benzin_table.sort_values(by='Benzin', ascending=False, inplace=True)
benzin_table.rename_axis(None, axis=1, inplace = True)

notes = "Es gibt teilweise einen grossen Verzug bei den Preismeldungen. Die Preise sind daher nicht immer tagesaktuell und als Grössenordnung zu verstehen. Für Finnland wird der Preis für einen Liter bleifrei 98 ausgewiesen."
notes_2 = "Es gibt teilweise einen grossen Verzug bei den Preismeldungen. Die Preise sind daher nicht immer tagesaktuell und als Grössenordnung zu verstehen."

update_chart(id = '4359e80ee2738a55d5f04f1409ffebf1', data = benzin_table, notes = notes)
update_chart(id = '5d54f8c74468704fbcb15b97cb56c6c5', data = benzin_table, notes = notes_2)


session = requests_html.HTMLSession()
r = session.get(url)
price_95 = r.html.xpath(
    '//*[@id="blockContentcontentInner"]/div[1]/div/div/div[3]/div/div[1]/table/tbody/tr[1]/td[2]/div/text()')
price_95 = pd.to_numeric(price_95[0])

#adac = 'https://www.adac.de/news/aktueller-spritpreis/'
#page = requests.get(adac)

#soup = BeautifulSoup(page.content, "html.parser")

#text = soup.find_all('b')[1].text.strip()
# price_e10 = pd.to_numeric(re.findall(
#       r'\d+\,\d+', text)[0].replace(',', '.'))


fuel_prices_old = pd.read_csv('./Benzinpreise.csv')
#fuel_prices_old_de = pd.read_csv('./Benzinpreise_de.csv')

data = {'date': date.today().strftime('%Y-%m-%d'),
        'Jahresdurchschnitt 2019': 1.6,
        '2022': price_95
        }

fuel_prices = pd.DataFrame(data, index=[0])

fuel_prices = pd.concat([fuel_prices_old, fuel_prices], ignore_index=True)

fuel_prices.drop_duplicates(subset='date', keep='last', inplace=True)

# data = {'Date': date.today().strftime('%Y-%m-%d'),
#       'Jahresdurchschnitt 2019': 1.4005,
#      '2022': price_e10
#     }

#fuel_prices_de = pd.DataFrame(data, index=[0])

#fuel_prices_de = pd.concat([fuel_prices_old_de, fuel_prices_de])

#fuel_prices_de.drop_duplicates(subset='Date', keep='last', inplace=True)

#fuel_prices.set_index('date', inplace=True)
#fuel_prices_de.set_index('Date', inplace=True)
#fuel_prices.index = pd.to_datetime(fuel_prices.index).strftime('%Y-%m-%d')
# fuel_prices_de.index = pd.to_datetime(
#   fuel_prices_de.index).strftime('%Y-%m-%d')

title_price = str(price_95).replace('.', ',')

title = "Benzin kostet im Schnitt " + title_price + " Franken pro Liter"

# Workaround @simonhuwiler:
# - Jahresdurchschnitt entfernen
# - 2022 umbenennen in "Benzinpreis"
df_tmp = fuel_prices.copy()
df_tmp.rename(columns={'2022': 'Benzinpreis'}, inplace=True)
df_tmp = df_tmp[['date', 'Benzinpreis']]

update_chart(id='1dda540238574eac80e865faa0d4aaba',
             data = df_tmp, title = title)
# update_chart(id='5ac628c4bb388d36fb2f5cbc745073c6',
#            data=fuel_prices_de[['Jahresdurchschnitt 2019', '2022']])

fuel_prices.to_csv(f'./Benzinpreise.csv', index=False)
# fuel_prices_de.to_csv(f'./Benzinpreise_de.csv')


url = 'https://www.heizoel24.ch/heizoelpreise'
session = requests_html.HTMLSession()
r = session.get(url)

price = r.html.xpath('//*[@id="price-faq-acc-0"]/div/div/text()')[0]

url_de = 'https://www.heizoel24.de/heizoelpreise'
session = requests_html.HTMLSession()
r = session.get(url_de)

price_de = r.html.xpath('//*[@id="price-faq-acc-0"]/div/div/text()')[0]

price = pd.to_numeric(re.findall(r'\d+\,\d+', price)[0].replace(',', '.'))
price_de = pd.to_numeric(re.findall(
    r'\d+\,\d+', price_de)[0].replace(',', '.'))

oil_price_old = pd.read_csv('./oil_price.csv')
oil_price_old_de = pd.read_csv('./oil_price_de.csv')


data = {'Datum': date.today().strftime('%Y-%m-%d'),
        'Jahresdurchschnitt 2019': 89.62,
        '2022': price}

oil_price = pd.DataFrame(data, index=[0])

oil_price = pd.concat([oil_price_old, oil_price], ignore_index=True)

oil_price.drop_duplicates(subset='Datum', keep='last', inplace=True)

data = {'Date': date.today().strftime('%Y-%m-%d'),
        'Jahresdurchschnitt 2019': 65.77,
        '2022': price_de}

oil_price_de = pd.DataFrame(data, index=[0])

oil_price_de = pd.concat([oil_price_old_de, oil_price_de], ignore_index=True)

oil_price_de.drop_duplicates(subset='Date', keep='last', inplace=True)

#oil_price.set_index('Datum', inplace=True)
#oil_price_de.set_index('Date', inplace=True)
#oil_price.index = pd.to_datetime(oil_price.index).strftime('%Y-%m-%d')
#oil_price_de.index = pd.to_datetime(oil_price_de.index).strftime('%Y-%m-%d')

# Update @simonhuwiler: Auskommentiert gemäss Florian.
# # Achtung, auch aus q.config entfernt!
# update_chart(id='b1717dcaee838699497b647ebbc25935',
#              data=oil_price)
# update_chart(id='5ac628c4bb388d36fb2f5cbc746a7cb6',
#              data=oil_price_de)

oil_price.to_csv(f'./oil_price.csv', index=False)
oil_price_de.to_csv(f'./oil_price_de.csv', index=False)


# Stock market data
tickers = ["EURCHF=X", "KE=F", "^GDAXI", "EURUSD=X","BTC-USD", "BZ=F"]  # Subtitute for the tickers you want
df = yf.download(tickers,  start="2019-01-01", end=date.today())

euro = df['Close']['EURCHF=X'][df.index >=
                               '2022-01-01'].to_frame().dropna().reset_index(level=0)

#euro.index = euro.index.strftime('%Y-%m-%d')
update_chart(id='1dda540238574eac80e865faa0dcab83', data=euro)

dollar = df['Close']['EURUSD=X'][df.index >=
                                 '2022-01-01'].to_frame().dropna().reset_index(level=0)
#dollar.index = dollar.index.strftime('%Y-%m-%d')
update_chart(id='5ac628c4bb388d36fb2f5cbc744a628c', data=dollar)

dax = df['Close']['^GDAXI'][df.index >=
                            '2022-01-01'].to_frame().dropna().reset_index(level=0)
#dax.index = dax.index.strftime('%Y-%m-%d')
update_chart(id='a78c9d9de3230aea314700dc582d873d', data=dax)

wheat = df['Close']['KE=F'][df.index >=
                            '2022-01-01'].to_frame().dropna().reset_index(level=0)
wheat['Jahresdurchschnitt 2019'] = df['Close']['KE=F'][(
    df.index >= '2019-01-01') & (df.index <= '2019-12-31')].mean()
# Update 3. Januar 2022 @simonhuwiler: 2022 umbenannt in "Weizenpreis", Jahresdurchschnitt entfernt
wheat.rename(columns={wheat.columns[1]: 'Weizenpreis'}, inplace=True)
wheat = wheat[['Date', 'Weizenpreis']]
#wheat = wheat[['Date', 'Jahresdurchschnitt 2019', '2022']]
#wheat.index = wheat.index.strftime('%Y-%m-%d')
update_chart(id='b1717dcaee838699497b647ebbceda21',
             data=wheat)




from market_ids import *

url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getHistoricalChartDataAsJson=&marketId=' + market_id + '&historicalSpan=3'
resp = requests.get(url)
json_file = resp.text
full_data = json.loads(json_file)

# create dataframe and format date column
df_gas = pd.DataFrame(full_data['bars'], columns=['Datum', 'Kosten'])
df_gas['Datum'] = pd.to_datetime(df_gas['Datum'])
df_gas.set_index('Datum', inplace=True)
df_gas = df_gas['Kosten'][df_gas.index >= '2022-01-01'].to_frame().dropna()
df_gas.rename(columns={df_gas.columns[0]: '2022'}, inplace=True)
df_gas = df_gas.reset_index(level=0)

# create date for chart notes
#timecode = df_gas.index[-1]
#timecode_str = timecode.strftime('%-d. %-m. %Y')
#notes_chart = 'Stand: ' + timecode_str

# convert DatetimeIndex
#df_gas.index = df_gas.index.strftime('%Y-%m-%d')

# run Q function
update_chart(id='1dda540238574eac80e865faa0ddbafc', data=df_gas)

date_today = date.today().strftime("%m/%d/%Y")



oil = df['Close']['BZ=F'][df.index >=
                         '2022-01-01'].to_frame().dropna().reset_index(level=0)
oil['Jahresdurchschnitt 2019'] = df['Close']['BZ=F'][(
    df.index >= '2019-01-01') & (df.index <= '2019-12-31')].mean()
oil.rename(columns={oil.columns[1]: '2022'}, inplace=True)
oil = oil[['Date', 'Jahresdurchschnitt 2019', '2022']]

update_chart(id='c6aec0c9dea84bcdef43b980cd4a7e3f', data=oil)

bitcoin = df['Close']["BTC-USD"].to_frame().dropna().round(1).reset_index(level=0)
#bitcoin.index = bitcoin.index.strftime('%Y-%m-%d')
update_chart(id='3ae57b07ddc738d6984ae6d72c027d3d', data=bitcoin)

month1 = date.today() - pd.to_timedelta(30, unit='d')
bitcoin1m = bitcoin.loc[(pd.to_datetime(bitcoin.Date)
                         >= pd.to_datetime(month1))]
update_chart(id='80a5f74298f588521786f9061c21d472',
             data=bitcoin1m)


smi = pd.read_csv('https://www.six-group.com/exchanges/downloads/indexdata/hsmi.csv', sep = ';', skiprows = 4)
smi['DATE'] = pd.to_datetime(smi['DATE'], format = '%d.%m.%Y')
smi.sort_values(by = 'DATE', ascending = True, inplace = True)
smi = smi[['DATE', 'Close']]
smi = smi[smi['DATE'] >= '2022-01-01']

smi.rename(columns={smi.columns[1]: '2022'}, inplace=True)

#smi_old = pd.read_csv('./SMI.csv')

#url = 'https://www.marketwatch.com/investing/index/smi?countrycode=ch''
#page = requests.get(url)

#soup = BeautifulSoup(page.content, "html.parser")
#results = soup.find(class_="table__cell u-semi").text.strip()
#close = pd.to_numeric(results.replace(',', ''))

#if date.today().weekday() == 0:
 #   date_ = (date.today() - timedelta(3)).strftime('%Y-%m-%d')
#else:
 #   date_ = (date.today() - timedelta(1)).strftime('%Y-%m-%d')

#data = {'Date': date_,
 #       'Close': close}
#smi = pd.DataFrame(data, index=[0])
#smi = pd.concat([smi_old, smi], ignore_index=True)
#smi.drop_duplicates(subset='Date', keep='last', inplace=True)
#smi.set_index('Date', inplace=True)
#smi.index = pd.to_datetime(smi.index).strftime('%Y-%m-%d')

update_chart(id='1dda540238574eac80e865faa0dc2348', data=smi)
#smi.to_csv(f'./SMI.csv', index=False)

# Benzinpreistabelle D

#kurs = euro['EURCHF=X'].tail(1).values
#benzin_de = benzin.copy()
#benzin_de['Benzin'] = round((benzin_de['Benzin']/kurs), 2)
#benzin_de['Diesel'] = round((benzin_de['Diesel']/kurs), 2)

eu = pd.read_excel('https://ec.europa.eu/energy/observatory/reports/latest_prices_raw_data.xlsx')
eu = eu.loc[(eu['Product Name'] == 'Euro-super 95') | (eu['Product Name'] == 'Automotive gas oil')].copy()
eu['Weekly price with taxes'] = round(pd.to_numeric(eu['Weekly price with taxes'].str.replace(',', '')) / 1000, 2)
eu = eu[['Country Name', 'Product Name', 'Weekly price with taxes']]
eu = eu.pivot(index='Country Name', columns='Product Name', values='Weekly price with taxes').reset_index()
eu.rename(columns = {'Euro-super 95': 'Benzin', 'Automotive gas oil': 'Diesel'}, inplace = True)

eu['Reiseziel'] = eu['Country Name'].apply(lambda x: GoogleTranslator(source='auto', target='de').translate(x))
#eu = pd.concat([benzin_de[benzin_de['Reiseziel'] == 'Schweiz'][['Reiseziel', 'Benzin', 'Diesel']], eu])
eu.sort_values(by='Benzin', ascending=False, inplace=True)
eu.rename_axis(None, axis=1, inplace = True)
eu.drop(columns=['Country Name'], inplace = True)

Reiseziele = [
'Niederlande',
'Belgien',
'Dänemark',
'Grossbritannien',
'Spanien',
'Österreich',
'Italien',
'Luxemburg',
'Tschechien',
'Frankreich',
'Polen' ]

eu = eu[['Reiseziel', 'Benzin', 'Diesel']]
eu_2 = eu.loc[eu['Reiseziel'].isin(Reiseziele)]

update_chart(id = 'a78c9d9de3230aea314700dc5855b330', data = eu, notes = notes_2)
update_chart(id = '9f87a00d3791c108c1b6c0edb4a392dd', data = eu_2, notes = notes_2)

# Unternehmen, die Russland verlassen

url = 'https://som.yale.edu/story/2022/over-450-companies-have-withdrawn-russia-some-remain'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
a = soup.find_all('div', class_='text-long')

data = {'type': ['Suspendierung des Russland-Geschäfts',
        'Endgültiger Rückzug aus Russland',
                 'Zurückhalten von Russland-Investitionen',
                 'Reduzierung des Russland-Geschäfts',
                 'Festhalten am Russland-Geschäft'],
        'number': [pd.to_numeric(re.findall(r'\d+', a[6].text))[0],
                   pd.to_numeric(re.findall(r'\d+', a[7].text))[0],
                   pd.to_numeric(re.findall(r'\d+', a[4].text))[0],
                   pd.to_numeric(re.findall(r'\d+', a[5].text))[0],
                   pd.to_numeric(re.findall(r'\d+', a[3].text))[0]
                   ]}


df = pd.DataFrame(data=data)
df = df.sort_values(by='number', ascending=False)
#df.set_index('type', inplace=True)

notes = 'Stand: ' + date.today().strftime('%d. %m. %Y')

update_chart(id='6aa31459fbbb1211b5ec05508a665b9e',
             data=df, notes=notes)

table = soup.find_all('table', class_ = 'responsive-enabled')
df = {}
for j in range(0, 5):
    all_ = []
    for i in table[j].find_all('td'):
        all_.append(i.text)

    firms = []
    countries = []
    for i in range(0, len(all_), 4):
        firms.append(all_[i])

    for i in range(3, len(all_), 4):
        countries.append(all_[i])

    firms = [i.strip() for i in firms]
    countries = [i.strip() for i in countries]

    df[j] = pd.DataFrame({'firm': firms, 'country': countries})

df[0]['status'] = 'Festhalten am Russland-Geschäft'
df[1]['status'] = 'Zurückhalten von Russland-Investitionen'
df[2]['status'] = 'Reduzierung des Russland-Geschäfts'
df[3]['status'] = 'Suspendierung des Russland-Geschäfts'
df[4]['status'] = 'Endgültiger Rückzug aus Russland'

list_ = pd.concat([df[0], df[1]])
list_ = pd.concat([list_, df[2]])
list_ = pd.concat([list_, df[3]])
list_ = pd.concat([list_, df[4]])


update_chart(id = '83caf1c1cfcfaf76da2c577a9e7f4f4a', data = list_[['firm', 'status']][list_['country'] == 'Switzerland'].groupby('status').count().reset_index().sort_values(by = 'firm', ascending = False), notes = notes)

update_chart(id = '8676bad64564b4740f74b6d5d04f4bf4', data = list_[['firm', 'status']][list_['country'] == 'Germany'].groupby('status').count().reset_index().sort_values(by = 'firm', ascending = False), notes = notes)


# BIP Indikator

#url = "https://www.seco.admin.ch/dam/seco/de/dokumente/Wirtschaft/Wirtschaftslage/indikatoren/wwa_publish.xls.download.xls/wwa_publish.xls"
#r = requests.get(url)
#open('temp.xls', 'wb').write(r.content)

# file = msoffcrypto.OfficeFile(open('temp.xls', 'rb'))  # read the original file
# Fill in the password, if it can be opened directly, the default password is 'VelvetSweatshop'
# file.load_key(password='VelvetSweatshop')
#file.decrypt(open('./decrypted.xls', 'wb'))

#bip = pd.read_excel('./decrypted.xls', sheet_name='rel_preCovid')
#bip = bip[3:]
#bip.rename(columns={bip.columns[0]: 'year', bip.columns[1]: 'W', bip.columns[2]: 'Index'}, inplace=True)

# bip.loc[bip['W'] < 10, 'KW'] = bip['year'].astype(
#   str) + '-W0' + bip['W'].astype(int).astype(str)
# bip.loc[bip['W'] >= 10, 'KW'] = bip['year'].astype(
#   str) + '-W' + bip['W'].astype(int).astype(str)
#bip = bip[['KW', 'Index']]
#bip.set_index('KW', inplace=True)


bip = pd.read_csv(
    "https://www.seco.admin.ch/dam/seco/de/dokumente/Wirtschaft/Wirtschaftslage/indikatoren/wwa.csv.download.csv/wwa.csv")
bip = bip.loc[bip['structure'] == 'seco_wwa_pre_covid'][['date', 'value']]
update_chart(id='c366afc02f262094669128cd054faf78', data=bip)


# Bitcoin energy

url = 'https://api.everviz.com/gsheet?googleSpreadsheetKey=1bLjXWHG4IXO8_CyMKRl1tSN8hTn3AFOlxfBISyQ6zM0&worksheet=A1:ZZ'
ua_str = UserAgent(verify_ssl=False).chrome

r = requests.get(url, headers={"User-Agent": ua_str})
data = r.json()

df = pd.json_normalize(data,  record_path=['values'])
df.columns = df.iloc[0]

df = df[1:].reset_index(drop=True)
df = df.transpose().copy()
df.columns = df.iloc[0]

df = df[1:]
df.iloc[:, 0] = pd.to_numeric(df.iloc[:, 0])
df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
df.reset_index(level=0, inplace=True)
df.rename(columns={0: 'Date'}, inplace=True)
# drop index name
#df.columns.name = None
# set new index
#df.set_index('Date', inplace=True)
df['Date'] = pd.to_datetime(df['Date'])
df = df[['Date', 'Estimated TWh per Year']]

update_chart(id='b6873820afc5a1492240edc1b101cdd9',
             data=df)


# 10 largest crypto currencies

#url = 'https://coinmarketcap.com/'

#page = requests.get(url)

#soup = BeautifulSoup(page.content, "html.parser")

#results = soup.find_all('table')

#market_cap = []
#for i in range(0, 10):
 #   market_cap.append(re.sub(
  #    "[^0-9]", "", results[0].find_all('span', class_='sc-b2299d0c-0 bcJsCG')[i].text.strip()))

#crypto = []
#for i in range(0, 10):
 #   crypto.append(results[0].find_all(
  #     'p', class_ = 'sc-e225a64a-0 ePTNty')[i].contents[0].text.strip())


#df = pd.DataFrame(data={'crypto': crypto, 'market_cap': market_cap})





tickers = ['BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD', 'USDC-USD', 'BUSD-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'MATIC-USD',
           'DOT-USD', 'DAI-USD', 'LTC-USD', 'WTRX-USD', 'SHIB-USD', 'HEX-USD', 'SOL-USD', 'TRX-USD', 'UNI7083-USD',
           'LEO-USD', 'STETH-USD', 'WBTC-USD','AVAX-USD', 'LINK-USD', 'ATOM-USD', 'ETC-USD', 'XMR-USD', 'XLM-USD',
           'BCH-USD', 'TON11419-USD']

df = yahoo_data.get_quote_yahoo(tickers)['marketCap']
df = df.head(10).copy().to_frame()

df.loc[df.index == 'BTC-USD', 'currency'] = 'Bitcoin'
df.loc[df.index == 'ETH-USD', 'currency'] = 'Ethereum'
df.loc[df.index == 'USDT-USD', 'currency'] = 'Tether'
df.loc[df.index == 'BNB-USD', 'currency'] = 'BNB'
df.loc[df.index == 'USDC-USD', 'currency'] = 'USD Coin'
df.loc[df.index == 'BUSD-USD', 'currency'] = 'Binance USD'
df.loc[df.index == 'XRP-USD', 'currency'] = 'XRP'
df.loc[df.index == 'DOGE-USD', 'currency'] = 'Dogecoin'
df.loc[df.index == 'ADA-USD', 'currency'] = 'Cardano'
df.loc[df.index == 'MATIC-USD', 'currency'] = 'Polygon'
df.loc[df.index == 'DOT-USD', 'currency'] = 'Polkadot'
df.loc[df.index == 'DAI-USD', 'currency'] = 'Dai'
df.loc[df.index == 'LTC-USD', 'currency'] = 'Litecoin'
df.loc[df.index == 'SHIB-USD', 'currency'] = 'Shiba Inu'
df.loc[df.index == 'TRX-USD', 'currency'] = 'Tron'
df.loc[df.index == 'SOL-USD', 'currency'] = 'Solana'
df.loc[df.index == 'UNI7083-USD', 'currency'] = 'Uniswap'
df.loc[df.index == 'AVAX-USD', 'currency'] = 'Avalanche'
df.loc[df.index == 'LINK-USD', 'currency'] = 'Chainlink'
df.loc[df.index == 'LEO-USD', 'currency'] = 'UNUS SED LEO'
df.loc[df.index == 'WBTC-USD', 'currency'] = 'Wrapped Bitcoin'
df.loc[df.index == 'ATOM-USD', 'currency'] = 'Cosmos'
df.loc[df.index == 'ETC-USD', 'currency'] = 'Ethereum Classic'
df.loc[df.index == 'XMR-USD', 'currency'] = 'Monero'
df.loc[df.index == 'XLM-USD', 'currency'] = 'Stellar'
df.loc[df.index == 'TON11419-USD', 'currency'] = 'Toncoin'
df.loc[df.index == 'BCH-USD', 'currency'] = 'Bitcoin Cash'


df = df[['currency','marketCap']].sort_values(by = ['marketCap'], ascending = False)


# defining the html contents of a URL.
#xhtml = url_get_contents(url).decode('latin-1')

# Defining the HTMLTableParser object
#p = HTMLTableParser()

# feeding the html contents in the HTMLTableParser object
#p.feed(xhtml)

#df = pd.DataFrame(p.tables[0]).dropna()
#df.columns = df.iloc[0]
#df = df[1:]
#df[["Name", "Name_1", "Name_2"]] = df["Name"].str.split("(\d)", n=1, expand=True)

#df[["Market Cap1", "Market Cap"]] = df["Market Cap"].str.split(expand = True)

#df['Market Cap'] = df['Market Cap'].str.replace(r'\D', '', regex=True)

#df = df[['Name', 'Market Cap']].copy()

#df.rename_axis(None, axis=1, inplace = True)

notes = 'Stand: ' + date.today().strftime('%d. %m. %Y')

update_chart(id='9640becc888e8a5d878819445105edce',
                 data=df, notes=notes)
    


# More stock market data

tickers = ["CSGN.SW"]  # Subtitute for the tickers you want
df_1 = yf.download(tickers,  period = "1y", interval = "1d")
df_1 = df_1['Close'].to_frame().dropna().reset_index(level = 0)

update_chart(id='9039ce8be0b7e1650165751c47d993d4',
                 data=df_1)





