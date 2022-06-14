
import pandas as pd
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json
import os
import sys
import openpyxl



sys.path.append(os.path.dirname((os.path.dirname(__file__))))

# Set Working Directory
os.chdir(os.path.dirname(__file__))


# Brot
url = 'https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
soup.find_all('a', class_ = 'pagination__page')

# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
bread = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    bread = bread.append(df)

bread.reset_index(drop = True, inplace = True)

bread['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

bread = bread[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]

date = date.today().strftime("%Y-%m-%d")

bread.to_excel(f'./output/bread_coop_' + date + '.xlsx', index = False)

#Milchprodukte
url = 'https://www.coop.ch/de/lebensmittel/milchprodukte-eier/c/m_0055?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
milk = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/milchprodukte-eier/c/m_0055?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    milk = milk.append(df)
    milk.reset_index(drop = True, inplace = True)

milk['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
milk = milk[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
milk.to_excel(f'./output/milk_coop_' + date + '.xlsx', index = False)

# Gemüse & Früchte
url = 'https://www.coop.ch/de/lebensmittel/fruechte-gemuese/c/m_0001?page=1&pageSize=60&q=%3AmostlyBought&sort=mostlyBought'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
vegi = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fruechte-gemuese/c/m_0001?page=' + str(i+1) + '&pageSize=60&q=%3AmostlyBought&sort=mostlyBought'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    vegi = vegi.append(df)
    vegi.reset_index(drop = True, inplace = True)
    
vegi['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
vegi = vegi[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
vegi.to_excel(f'./output/vegi_coop_' + date + '.xlsx', index = False)

# Fleisch
url = 'https://www.coop.ch/de/lebensmittel/fleisch-fisch/c/m_0087?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
meat = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fleisch-fisch/c/m_0087?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    meat = meat.append(df)
    meat.reset_index(drop = True, inplace = True)


meat['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
meat = meat[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
meat.to_excel(f'./output/meat_coop_' + date + '.xlsx', index = False)

# Vorräte
url = 'https://www.coop.ch/de/lebensmittel/vorraete/c/m_0140?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
provision = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/vorraete/c/m_0140?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    provision = provision.append(df)
    provision.reset_index(drop = True, inplace = True)

provision['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
provision = provision[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
provision.to_excel(f'./output/provision_coop_' + date + '.xlsx', index = False)
