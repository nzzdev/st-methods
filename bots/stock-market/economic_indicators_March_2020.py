
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


from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# TomTom

tomtom = pd.read_csv('https://raw.githubusercontent.com/ActiveConclusion/COVID19_mobility/master/tomtom_reports/tomtom_trafic_index.csv')
ch = tomtom[(tomtom.country == 'Switzerland') & (tomtom.date >= '2019-01-01')]
congestion_ch = ch[['date', 'congestion']].groupby('date').mean().rolling(7).mean()

update_chart(id='c77298787298e4fcae70369e03275be6', data = congestion_ch[(congestion_ch.index >= '2022-01-01')][['congestion']])

de = tomtom[(tomtom.country == 'Germany') & (tomtom.date >= '2019-01-01')]
congestion_de = de[['date', 'congestion']].groupby('date').mean().rolling(7).mean()

update_chart(id='5ac628c4bb388d36fb2f5cbc743f5f8b', data = congestion_de[(congestion_de.index >= '2022-01-01')][['congestion']])


# LKW

lkw = pd.read_excel('https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Industrie-Verarbeitendes-Gewerbe/Tabellen/Lkw-Maut-Fahrleistungsindex-Daten.xlsx?__blob=publicationFile', sheet_name = 'Daten')
lkw = lkw[4:]
new_header = lkw.iloc[0]
lkw = lkw[1:]
lkw.columns = new_header
lkw = lkw[['Datum', 'gleitender 7-Tage-Durchschnitt KSB']]
lkw['Datum'] = pd.to_datetime(lkw['Datum'])

lkw_2022 = lkw.loc[lkw['Datum'] >= '2022-01-01'].copy()
lkw_2019 = lkw.loc[(lkw['Datum'].dt.date >= date(2022, 1, 1) - timedelta(366) - timedelta(2*365)) &
                (lkw['Datum'].dt.date <= date(2022, 12, 31) - timedelta(366) - timedelta(2*365))
                ].copy()

lkw_2019['Datum'] = lkw_2019['Datum'].dt.date + timedelta(366) + timedelta(2*365)
lkw_2022['Datum'] = lkw_2022['Datum'].dt.date

lkw_2019.rename(columns = {'gleitender 7-Tage-Durchschnitt KSB': '2019'}, inplace = True)
lkw_2022.rename(columns = {'gleitender 7-Tage-Durchschnitt KSB': '2022'}, inplace = True)

lkw = lkw_2019.merge(lkw_2022, on = 'Datum', how = 'outer')

update_chart(id='5ac628c4bb388d36fb2f5cbc7441bfc7', data = lkw)


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

update_chart(id='6aa31459fbbb1211b5ec05508a5413ca', data = zh)


# Energie

url = 'https://www.tcs.ch/de/camping-reisen/reiseinformationen/wissenswertes/fahrkosten-gebuehren/benzinpreise.php'

# Opens a website and read its
# binary contents (HTTP Response Body)
#def url_get_contents(url):

	# Opens a website and read its
	# binary contents (HTTP Response Body)

	#making request to the website
	#req = urllib.request.Request(url=url)
	#f = urllib.request.urlopen(req)

	#reading contents of the website
	#return f.read()

# defining the html contents of a URL.
#xhtml = url_get_contents(url).decode('utf-8')

# Defining the HTMLTableParser object
#p = HTMLTableParser()

# feeding the html contents in the
# HTMLTableParser object
#p.feed(xhtml)

#benzin = pd.DataFrame(p.tables[2]).dropna()
#benzin.columns = benzin.iloc[0]
#benzin = benzin[1:]
#benzin = benzin[benzin.Reiseziel != 'Russland']

#benzin['95'] = pd.to_numeric(benzin['95']).round(2)
#benzin['98'] = pd.to_numeric(benzin['98']).round(2)
#benzin.loc[benzin['95'].isna(), '95'] = benzin['98']
#benzin = benzin[['Reiseziel', '95']]
#benzin.rename(columns = {'95': 'Benzinpreis'}, inplace = True)
#benzin.sort_values(by = 'Benzinpreis', ascending = False, inplace = True)

#update_chart(id = '4359e80ee2738a55d5f04f1409ffebf1', data = benzin)



session = requests_html.HTMLSession()
r = session.get(url)
price_95 = r.html.xpath('//*[@id="blockContentcontentInner"]/div[1]/div/div/div[3]/div/div[1]/table/tbody/tr[1]/td[2]/div/text()')
price_95 = pd.to_numeric(price_95[0])

adac = 'https://www.adac.de/news/aktueller-spritpreis/'
page = requests.get(adac)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(class_ = "sc-bQFuvY dJfhdt")

element = results.find_all("li", class_="sc-eBhrFy iKCSre")[0]
text = element.find("b").text.strip()
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

update_chart(id = '1dda540238574eac80e865faa0d4aaba', data = fuel_prices)
update_chart(id = '5ac628c4bb388d36fb2f5cbc745073c6', data = fuel_prices_de)

fuel_prices.to_csv('./Benzinpreise.csv', index = False)
fuel_prices_de.to_csv('./Benzinpreise_de.csv', index = False)


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

update_chart(id = 'b1717dcaee838699497b647ebbc25935', data = oil_price)
update_chart(id = '5ac628c4bb388d36fb2f5cbc746a7cb6', data = oil_price_de)

oil_price.to_csv('./oil_price.csv', index = False)
oil_price_de.to_csv('./oil_price_de.csv', index = False)


# Stock market data

tickers = ["EURCHF=X", "KE=F", "TTF=F", "^GDAXI", "EURUSD=X"] #Subtitute for the tickers you want
df = yf.download(tickers,  start = "2019-01-01" , end = date.today())

euro = df['Close']['EURCHF=X'][df.index >= '2022-01-01'].reset_index().dropna()
update_chart(id = '1dda540238574eac80e865faa0dcab83', data = euro)

dollar = df['Close']['EURUSD=X'][df.index >= '2022-01-01'].reset_index().dropna()
update_chart(id = '5ac628c4bb388d36fb2f5cbc744a628c', data = dollar)

dax = df['Close']['^GDAXI'][df.index >= '2022-01-01'].reset_index().dropna()
update_chart(id = 'a78c9d9de3230aea314700dc582d873d', data = dax)

wheat = df['Close']['KE=F'][df.index >= '2022-01-01'].reset_index().dropna()
wheat['2019'] = df['Close']['KE=F'][(df.index >= '2019-01-01') & (df.index <= '2019-12-31')].mean()
wheat.rename(columns={wheat.columns[1]: '2022'}, inplace = True)
wheat = wheat[['Date', '2019', '2022']]

update_chart(id = 'b1717dcaee838699497b647ebbceda21', data = wheat)


gas = df['Close']['TTF=F'][df.index >= '2022-01-01'].reset_index().dropna()
gas['2019'] = df['Close']['TTF=F'][(df.index >= '2019-01-01') & (df.index <= '2019-12-31')].mean()
gas.rename(columns={gas.columns[1]: '2022'}, inplace = True)
gas = gas[['Date', '2019', '2022']]

update_chart(id = '1dda540238574eac80e865faa0ddbafc', data = gas)


smi_old = pd.read_csv('./SMI.csv')

url = 'https://www.marketwatch.com/investing/index/smi?countrycode=ch'
page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(class_ = "table__cell u-semi").text.strip()
close = pd.to_numeric(results.replace(',',''))

data = {'Date': (date.today() - timedelta(1)).strftime('%Y-%m-%d'), 
        'Close': close}
smi= pd.DataFrame(data, index=[0])
smi = smi_old.append(smi)
smi.drop_duplicates(subset = 'Date', keep = 'last', inplace = True)

update_chart(id = '1dda540238574eac80e865faa0dc2348', data = smi)
smi.to_csv('./SMI.csv', index = False)

kurs = euro['EURCHF=X'].tail(1).values
benzin_de = benzin.copy()
benzin_de['Benzinpreis'] = round((benzin_de['Benzinpreis']/kurs), 2)
#update_chart(id = 'a78c9d9de3230aea314700dc5855b330', data = benzin_de)


# Unternehmen, die Russland verlassen

url = 'https://som.yale.edu/story/2022/over-450-companies-have-withdrawn-russia-some-remain'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
a = soup.find_all('div', class_ = 'text-long')

data = {'type': ['Suspendierung des Russlandgeschäfts',
        'Endgültiger Rückzug aus Russland',
        'Zurückhalten von Russlandinvestitionen',
       'Reduzierung des Russlandgeschäfts'],
       'number': [pd.to_numeric(re.findall(r'\d+', a[7].text))[0], 
                  pd.to_numeric(re.findall(r'\d+', a[8].text))[0],
                  pd.to_numeric(re.findall(r'\d+', a[5].text))[0],
                  pd.to_numeric(re.findall(r'\d+', a[6].text))[0]]} 

df = pd.DataFrame(data = data)
df = df.sort_values(by = 'number', ascending = False)
update_chart(id = '6aa31459fbbb1211b5ec05508a665b9e', data = df)


# BIP Indikator

url = "https://www.seco.admin.ch/dam/seco/de/dokumente/Wirtschaft/Wirtschaftslage/indikatoren/wwa_publish.xls.download.xls/wwa_publish.xls"

file = msoffcrypto.OfficeFile (open ('/Users/florianseliger/Downloads/wwa_publish-2.xls', 'rb')) # read the original file
file.load_key (password = 'VelvetSweatshop') # Fill in the password, if it can be opened directly, the default password is 'VelvetSweatshop'
file.decrypt (open ('/Users/florianseliger/Downloads/decrypted.xls', 'wb'))

bip = pd.read_excel('/Users/florianseliger/Downloads/decrypted.xls', sheet_name = 'rel_preCovid')
bip = bip[3:]
bip.rename(columns = {bip.columns[0]: 'year', bip.columns[1]: 'W', bip.columns[2]: 'Index'}, inplace = True)

bip.loc[bip['W'] < 10 , 'KW'] = bip['year'].astype(str) + '-W0' + bip['W'].astype(int).astype(str)
bip.loc[bip['W'] >= 10 , 'KW'] = bip['year'].astype(str) + '-W' + bip['W'].astype(int).astype(str)
bip =  bip[['KW', 'Index']]

update_chart(id = 'c366afc02f262094669128cd054faf78', data = bip)
