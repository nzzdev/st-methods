
import pandas as pd
import requests_html
from datetime import date, datetime, timedelta
import re
import yfinance as yf
from bs4 import BeautifulSoup
from html_table_parser.parser import HTMLTableParser
import msoffcrypto
import requests
import urllib.request
import os
import sys

sys.path.append(os.path.dirname((os.path.dirname(__file__))))
from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# TomTom

tomtom = pd.read_csv('https://raw.githubusercontent.com/ActiveConclusion/COVID19_mobility/master/tomtom_reports/tomtom_trafic_index.csv')
ch = tomtom[(tomtom.country == 'Switzerland') & (tomtom.date >= '2019-01-01')]
congestion_ch = ch[['date', 'congestion']].groupby('date').mean().rolling(7).mean()
data = congestion_ch[(congestion_ch.index >= '2022-01-01')][['congestion']] 
update_chart(id='c77298787298e4fcae70369e03275be6', data = data)

de = tomtom[(tomtom.country == 'Germany') & (tomtom.date >= '2019-01-01')]
congestion_de = de[['date', 'congestion']].groupby('date').mean().rolling(7).mean()
data = congestion_de[(congestion_de.index >= '2022-01-01')][['congestion']]
update_chart(id='5ac628c4bb388d36fb2f5cbc743f5f8b', data = data)


# LKW

lkw = pd.read_excel('https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Industrie-Verarbeitendes-Gewerbe/Tabellen/Lkw-Maut-Fahrleistungsindex-Daten.xlsx?__blob=publicationFile', sheet_name = 'Daten')
lkw = lkw[4:]
new_header = lkw.iloc[0]
lkw = lkw[1:]
lkw.columns = new_header
lkw = lkw[['Datum', 'gleitender 7-Tage-Durchschnitt KSB']]
lkw['Datum'] = pd.to_datetime(lkw['Datum'])
lkw = lkw.rename_axis(None, axis=1)

lkw_2022 = lkw.loc[lkw['Datum'] >= '2022-01-01'].copy()
lkw_2019 = lkw.loc[(lkw['Datum'].dt.date >= date(2022, 1, 1) - timedelta(366) - timedelta(2*365)) &
                (lkw['Datum'].dt.date <= date(2022, 12, 31) - timedelta(366) - timedelta(2*365))
                ].copy()

lkw_2019['Datum'] = lkw_2019['Datum'].dt.date + timedelta(366) + timedelta(2*365)
lkw_2022['Datum'] = lkw_2022['Datum'].dt.date

lkw_2019.rename(columns = {'gleitender 7-Tage-Durchschnitt KSB': '2019'}, inplace = True)
lkw_2022.rename(columns = {'gleitender 7-Tage-Durchschnitt KSB': '2022'}, inplace = True)

lkw = lkw_2019.merge(lkw_2022, on = 'Datum', how = 'outer')
lkw.set_index('Datum', inplace =True)
lkw.index = pd.to_datetime(lkw.index).strftime('%Y-%m-%d')

update_chart(id='5ac628c4bb388d36fb2f5cbc7441bfc7', data = lkw[['2019', '2022']])


# Flugdaten

zh = pd.read_csv('https://raw.githubusercontent.com/KOF-ch/economic-monitoring/master/data/ch.zrh_airport.departures.csv')

zh['time'] = pd.to_datetime(zh['time'])
zh = zh.loc[(zh['rnwy'] == 'all') & (zh['route'] == 'total') & (zh['time'] >= '2019-01-01') & (zh['time'].dt.date <= date.today()) ]
zh = zh[['time', 'value']]
zh = zh.set_index('time')
zh = zh.rolling(7).mean().reset_index()
zh_2022 = zh.loc[zh['time'] >= '2022-01-01'].copy()
zh_2019 = zh.loc[(zh['time'].dt.date >= date(2022, 1, 1) - timedelta(366) - timedelta(2*365)) &
                (zh['time'].dt.date <= date(2022, 12, 31) - timedelta(366) - timedelta(2*365))
                ].copy()
zh_2019['time'] = zh_2019['time'].dt.date + timedelta(366) + timedelta(2*365)
zh_2022['time'] = zh_2022['time'].dt.date
zh_2019.rename(columns = {'value': '2019'}, inplace = True)
zh_2022.rename(columns = {'value': '2022'}, inplace = True)
zh = zh_2019.merge(zh_2022, on = 'time', how = 'outer')
zh.set_index('time', inplace = True)
zh.index = pd.to_datetime(zh.index).strftime('%Y-%m-%d')

update_chart(id='6aa31459fbbb1211b5ec05508a5413ca', data = zh[['2019', '2022']])

url = 'https://www.adv.aero/corona-pandemie/woechentliche-verkehrszahlen/'
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find('table', class_ = "alignleft")

data = []
rows = results.find_all('tr')
for row in rows:
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]
    data.append([ele for ele in cols if ele])

passagiere = pd.DataFrame(data[1:], columns = ['KW in 2022', '2019_datum', '2021_datum', '2022_datum', '2019', '2021', '2022', '%22/21', '%22/19'])
passagiere = passagiere[['KW in 2022', '2019', '2022']].copy()

passagiere['2019'] = pd.to_numeric(passagiere['2019'].str.replace('.', '', regex = False))
passagiere['2022'] = pd.to_numeric(passagiere['2022'].str.replace('.', '', regex = False))
passagiere['KW in 2022'] = pd.to_numeric(passagiere['KW in 2022'])
passagiere.loc[passagiere['KW in 2022'] < 10 , 'KW'] = '2022-W0' + passagiere['KW in 2022'].astype(str)
passagiere.loc[passagiere['KW in 2022'] >= 10 , 'KW'] = '2022-W' + passagiere['KW in 2022'].astype(str)

passagiere = passagiere[['KW', '2019', '2022']].copy()
passagiere.set_index('KW', inplace = True)

update_chart(id='7a53d2e458b7ba35c25526a2c21d3956', data = passagiere[['2019', '2022']])


# Sanktionen

timeline = pd.read_csv('https://raw.githubusercontent.com/correctiv/ru-sanctions-dashboard/main/src/data/sanctions_timeline_2014-2022.csv')
timeline.set_index('start', inplace = True)
timeline.index = pd.to_datetime(timeline.index).strftime('%Y-%m-%d')

update_chart(id='2a1327d75c83a9c4ea49f935dd3705ef', data = timeline[['sanction_id']])

origin = pd.read_csv('https://raw.githubusercontent.com/correctiv/ru-sanctions-dashboard/main/src/data/recent_origin_aggregation_table.csv')
origin = origin.iloc[1: , :]
cols = origin.iloc[:, 1:].columns.tolist()
origin['start'] = pd.to_datetime(origin.start)

origin[cols] = origin[cols].apply(pd.to_numeric, errors='coerce')

origin['all'] = origin.iloc[:,1:].sum(axis = 1)
origin = origin[['start', 'all']].sort_values(by = 'start')

origin.set_index('start', inplace = True)
origin.index = pd.to_datetime(origin.index).strftime('%Y-%m-%d')

update_chart(id='85c353bb11cc62672a227f886950b782', data = origin[['all']])



# Energie

url = 'https://www.tcs.ch/de/camping-reisen/reiseinformationen/wissenswertes/fahrkosten-gebuehren/benzinpreise.php'

# Opens a website and read its binary contents (HTTP Response Body)
def url_get_contents(url):

	#making request to the website
        req = urllib.request.Request(url=url)
        f = urllib.request.urlopen(req)

	#reading contents of the website
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
benzin['98'] = pd.to_numeric(benzin['98']).round(2)
benzin.loc[benzin['95'].isna(), '95'] = benzin['98']
benzin = benzin[['Reiseziel', '95']]
benzin.rename(columns = {'95': 'Benzinpreis'}, inplace = True)
benzin.sort_values(by = 'Benzinpreis', ascending = False, inplace = True)
benzin.set_index('Reiseziel', inplace = True)

#update_chart(id = '4359e80ee2738a55d5f04f1409ffebf1', data = benzin[['Benzinpreis']])



session = requests_html.HTMLSession()
r = session.get(url)
price_95 = r.html.xpath('//*[@id="blockContentcontentInner"]/div[1]/div/div/div[3]/div/div[1]/table/tbody/tr[1]/td[2]/div/text()')
price_95 = pd.to_numeric(price_95[0])

adac = 'https://www.adac.de/news/aktueller-spritpreis/'
page = requests.get(adac)

soup = BeautifulSoup(page.content, "html.parser")

try:
        text = soup.find_all('b')[6].text.strip()
        price_e10 = pd.to_numeric(re.findall(r'\d+\,\d+', text)[0].replace(',','.'))
except IndexError:
        text = soup.find_all('b')[5].text.strip()
        price_e10 = pd.to_numeric(re.findall(r'\d+\,\d+', text)[0].replace(',','.'))

fuel_prices_old = pd.read_csv('./Benzinpreise.csv')
fuel_prices_old_de = pd.read_csv('./Benzinpreise_de.csv')

data = {'date': date.today().strftime('%Y-%m-%d'), 
        '2019': 1.6,
        '2022': price_95
        }

fuel_prices = pd.DataFrame(data, index=[0])

fuel_prices = fuel_prices_old.append(fuel_prices)

fuel_prices.drop_duplicates(subset = 'date', keep = 'last', inplace = True)

data = {'Date': date.today().strftime('%Y-%m-%d'), 
        '2019': 1.4005,
        '2022': price_e10
        }

fuel_prices_de = pd.DataFrame(data, index=[0])

fuel_prices_de = fuel_prices_old_de.append(fuel_prices_de)

fuel_prices_de.drop_duplicates(subset = 'Date', keep = 'last', inplace = True)

fuel_prices.set_index('date', inplace =True)
fuel_prices_de.set_index('Date', inplace =True)
fuel_prices.index = pd.to_datetime(fuel_prices.index).strftime('%Y-%m-%d')
fuel_prices_de.index = pd.to_datetime(fuel_prices_de.index).strftime('%Y-%m-%d')

update_chart(id = '1dda540238574eac80e865faa0d4aaba', data = fuel_prices[['2019', '2022']])
update_chart(id = '5ac628c4bb388d36fb2f5cbc745073c6', data = fuel_prices_de[['2019', '2022']])

fuel_prices.to_csv(f'./Benzinpreise.csv')
fuel_prices_de.to_csv(f'./Benzinpreise_de.csv')


url = 'https://www.heizoel24.ch/heizoelpreise'
session = requests_html.HTMLSession()
r = session.get(url)

price = r.html.xpath('//*[@id="price-faq-acc-0"]/div/div/text()')[0]

url_de = 'https://www.heizoel24.de/heizoelpreise'
session = requests_html.HTMLSession()
r = session.get(url_de)

price_de = r.html.xpath('//*[@id="price-faq-acc-0"]/div/div/text()')[0]

price = pd.to_numeric(re.findall(r'\d+\,\d+', price)[0].replace(',','.'))
price_de = pd.to_numeric(re.findall(r'\d+\,\d+', price_de)[0].replace(',','.'))

oil_price_old = pd.read_csv('./oil_price.csv')
oil_price_old_de = pd.read_csv('./oil_price_de.csv')

data = {'Datum': date.today().strftime('%Y-%m-%d'), 
        '2019': 89.62,
        '2022': price}

oil_price = pd.DataFrame(data, index=[0])

oil_price = oil_price_old.append(oil_price)

oil_price.drop_duplicates(subset = 'Datum', keep = 'last', inplace = True)

data = {'Date': date.today().strftime('%Y-%m-%d'), 
        '2019': 65.77,
        '2022': price_de}

oil_price_de = pd.DataFrame(data, index=[0])

oil_price_de = oil_price_old_de.append(oil_price_de)

oil_price_de.drop_duplicates(subset = 'Date', keep = 'last', inplace = True)

oil_price.set_index('Datum', inplace = True)
oil_price_de.set_index('Date', inplace = True)
oil_price.index = pd.to_datetime(oil_price.index).strftime('%Y-%m-%d')
oil_price_de.index = pd.to_datetime(oil_price_de.index).strftime('%Y-%m-%d')

update_chart(id = 'b1717dcaee838699497b647ebbc25935', data = oil_price[['2019', '2022']])
update_chart(id = '5ac628c4bb388d36fb2f5cbc746a7cb6', data = oil_price_de[['2019', '2022']])

oil_price.to_csv(f'./oil_price.csv')
oil_price_de.to_csv(f'./oil_price_de.csv')


# Stock market data
tickers = ["EURCHF=X", "KE=F", "TTF=F", "^GDAXI", "EURUSD=X", "BTC-USD", "BZ=F"] #Subtitute for the tickers you want
df = yf.download(tickers,  start = "2019-01-01" , end = date.today())

euro = df['Close']['EURCHF=X'][df.index >= '2022-01-01'].to_frame().dropna()
euro = euro[['EURCHF=X']]
euro.index = euro.index.strftime('%Y-%m-%d')
update_chart(id = '1dda540238574eac80e865faa0dcab83', data = euro[['EURCHF=X']])

dollar = df['Close']['EURUSD=X'][df.index >= '2022-01-01'].to_frame().dropna()
dollar = dollar[['EURUSD=X']]
dollar.index = dollar.index.strftime('%Y-%m-%d')
update_chart(id = '5ac628c4bb388d36fb2f5cbc744a628c', data = dollar[['EURUSD=X']])

dax = df['Close']['^GDAXI'][df.index >= '2022-01-01'].to_frame().dropna()
dax = dax[['^GDAXI']]
dax.index = dax.index.strftime('%Y-%m-%d')
update_chart(id = 'a78c9d9de3230aea314700dc582d873d', data = dax[['^GDAXI']])

wheat = df['Close']['KE=F'][df.index >= '2022-01-01'].to_frame().dropna()
wheat['2019'] = df['Close']['KE=F'][(df.index >= '2019-01-01') & (df.index <= '2019-12-31')].mean()
wheat.rename(columns={wheat.columns[0]: '2022'}, inplace = True)
wheat = wheat[['2019', '2022']]
wheat.index = wheat.index.strftime('%Y-%m-%d')
update_chart(id = 'b1717dcaee838699497b647ebbceda21', data = wheat[['2019', '2022']])

gas = df['Close']['TTF=F'][df.index >= '2022-01-01'].to_frame().dropna()
gas['2019'] = df['Close']['TTF=F'][(df.index >= '2019-01-01') & (df.index <= '2019-12-31')].mean()
gas.rename(columns={gas.columns[0]: '2022'}, inplace = True)
gas = gas[['2019', '2022']]
gas.index = gas.index.strftime('%Y-%m-%d')
update_chart(id = '1dda540238574eac80e865faa0ddbafc', data = gas[['2019', '2022']])

gas2 = df['Close']['TTF=F'][df.index >= '2021-03-01'].to_frame().dropna()
gas2.rename(columns={'TTF=F': 'Kosten'}, inplace=True)
gas2 = gas2[['Kosten']]
timecode = gas2.index[-1]
timecode_str = timecode.strftime('%-d. %-m. %Y')
gas2.index = gas2.index.strftime('%Y-%m-%d')
notes_chart = 'Stand: ' + timecode_str
update_chart(id='4decc4d9f742ceb683fd78fa5937acfd', notes = notes_chart, data = gas2[['Kosten']])

oil = df['Close']['BZ=F'][df.index >= '2022-01-01'].to_frame().dropna()
oil['2019'] = df['Close']['BZ=F'][(df.index >= '2019-01-01') & (df.index <= '2019-12-31')].mean()
oil.rename(columns={oil.columns[0]: '2022'}, inplace = True)
oil = oil[['2019', '2022']]
oil.index = oil.index.strftime('%Y-%m-%d')
update_chart(id = 'c6aec0c9dea84bcdef43b980cd4a7e3f', data = oil[['2019', '2022']])

bitcoin = df['Close']["BTC-USD"].to_frame().dropna().round(1)
bitcoin = bitcoin[['BTC-USD']]
bitcoin.index = bitcoin.index.strftime('%Y-%m-%d')
update_chart(id = '3ae57b07ddc738d6984ae6d72c027d3d', data = bitcoin[['BTC-USD']])

month1 = date.today() -  pd.to_timedelta(30, unit='d')
bitcoin1m = bitcoin.loc[(pd.to_datetime(bitcoin.index) >= pd.to_datetime(month1))]
update_chart(id = '80a5f74298f588521786f9061c21d472', data = bitcoin1m[['BTC-USD']])


smi_old = pd.read_csv('./SMI.csv')

url = 'https://www.marketwatch.com/investing/index/smi?countrycode=ch'
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(class_ = "table__cell u-semi").text.strip()
close = pd.to_numeric(results.replace(',',''))

if date.today().weekday() == 0:
    date_ = (date.today() - timedelta(3)).strftime('%Y-%m-%d')
else:
    date_ = (date.today() - timedelta(1)).strftime('%Y-%m-%d')

data = {'Date': date_, 
        'Close': close}
smi= pd.DataFrame(data, index=[0])
smi = smi_old.append(smi)
smi.drop_duplicates(subset = 'Date', keep = 'last', inplace = True)
smi.set_index('Date', inplace = True)
smi.index = pd.to_datetime(smi.index).strftime('%Y-%m-%d')

update_chart(id = '1dda540238574eac80e865faa0dc2348', data = smi[['Close']])
smi.to_csv(f'./SMI.csv')

#kurs = euro['EURCHF=X'].tail(1).values
#benzin_de = benzin.copy()
#benzin_de['Benzinpreis'] = round((benzin_de['Benzinpreis']/kurs), 2)
#update_chart(id = 'a78c9d9de3230aea314700dc5855b330', data = benzin_de)


# Unternehmen, die Russland verlassen

url = 'https://som.yale.edu/story/2022/over-450-companies-have-withdrawn-russia-some-remain'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
a = soup.find_all('div', class_ = 'text-long')

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




df = pd.DataFrame(data = data)
df = df.sort_values(by = 'number', ascending = False)
df.set_index('type', inplace = True)

notes = 'Stand: ' + date.today().strftime('%d. %m. %Y')

update_chart(id = '6aa31459fbbb1211b5ec05508a665b9e', data = df[['number']], notes = notes)


# BIP Indikator

url = "https://www.seco.admin.ch/dam/seco/de/dokumente/Wirtschaft/Wirtschaftslage/indikatoren/wwa_publish.xls.download.xls/wwa_publish.xls"
r = requests.get(url)
open('temp.xls', 'wb').write(r.content)

file = msoffcrypto.OfficeFile (open ('temp.xls', 'rb')) # read the original file
file.load_key (password = 'VelvetSweatshop') # Fill in the password, if it can be opened directly, the default password is 'VelvetSweatshop'
file.decrypt (open ('./decrypted.xls', 'wb'))

bip = pd.read_excel('./decrypted.xls', sheet_name = 'rel_preCovid')
bip = bip[3:]
bip.rename(columns = {bip.columns[0]: 'year', bip.columns[1]: 'W', bip.columns[2]: 'Index'}, inplace = True)

bip.loc[bip['W'] < 10 , 'KW'] = bip['year'].astype(str) + '-W0' + bip['W'].astype(int).astype(str)
bip.loc[bip['W'] >= 10 , 'KW'] = bip['year'].astype(str) + '-W' + bip['W'].astype(int).astype(str)
bip =  bip[['KW', 'Index']]
bip.set_index('KW', inplace = True)

update_chart(id = 'c366afc02f262094669128cd054faf78', data = bip[['Index']])
