
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
print(page.text)
print(page)
soup = BeautifulSoup(page.content, "html.parser")
soup.find_all('a', class_ = 'pagination__page')

# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]

date = date.today().strftime("%Y-%m-%d")

products.to_excel(f'./output/bread_coop_' + date + '.xlsx', index = False)

#Milchprodukte
url = 'https://www.coop.ch/de/lebensmittel/milchprodukte-eier/c/m_0055?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/milchprodukte-eier/c/m_0055?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/milk_coop_' + date + '.xlsx', index = False)

# Gemüse & Früchte
url = 'https://www.coop.ch/de/lebensmittel/fruechte-gemuese/c/m_0001?page=1&pageSize=60&q=%3AmostlyBought&sort=mostlyBought'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fruechte-gemuese/c/m_0001?page=' + str(i+1) + '&pageSize=60&q=%3AmostlyBought&sort=mostlyBought'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)
    
products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/vegi_coop_' + date + '.xlsx', index = False)

# Fleisch
url = 'https://www.coop.ch/de/lebensmittel/fleisch-fisch/c/m_0087?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fleisch-fisch/c/m_0087?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)


products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/meat_coop_' + date + '.xlsx', index = False)

# Vorräte
url = 'https://www.coop.ch/de/lebensmittel/vorraete/c/m_0140?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/vorraete/c/m_0140?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/provision_coop_' + date + '.xlsx', index = False)

# Süsses & Snacks
url = 'https://www.coop.ch/de/lebensmittel/suesses-snacks/c/m_2506?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/suesses-snacks/c/m_2506?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/sweet_coop_' + date + '.xlsx', index = False)

# Getränke
url = 'https://www.coop.ch/de/lebensmittel/getraenke/c/m_2242?sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/getraenke/c/m_2242?sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/drinks_coop_' + date + '.xlsx', index = False)

# Haushalt
url = 'https://www.coop.ch/de/haushalt-tier/haushalt-kueche/c/m_0298?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/haushalt-kueche/c/m_0298?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel', 'timestamp']]
products.to_excel(f'./output/house_coop_' + date + '.xlsx', index = False)



# Reinigen
url = 'https://www.coop.ch/de/haushalt-tier/reinigung-putzen/c/m_0279?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/reinigung-putzen/c/m_0279?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel', 'timestamp']]
products.to_excel(f'./output/clean_coop_' + date + '.xlsx', index = False)



# Toilettenpapier
url = 'https://www.coop.ch/de/haushalt-tier/toiletten-haushaltpapier/c/m_0288?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/toiletten-haushaltpapier/c/m_0288?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel', 'timestamp']]
products.to_excel(f'./output/toilet_coop_' + date + '.xlsx', index = False)


# Büro
url = 'https://www.coop.ch/de/haushalt-tier/buero-papeterie/c/m_0314?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/buero-papeterie/c/m_0314?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel', 'timestamp']]
products.to_excel(f'./output/office_coop_' + date + '.xlsx', index = False)

# Elektro
url = 'https://www.coop.ch/de/haushalt-tier/elektroartikel-batterien/c/m_0324?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/elektroartikel-batterien/c/m_0324?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel', 'timestamp']]
products.to_excel(f'./output/electronics_' + date + '.xlsx', index = False)

# Bekleidung
url = 'https://www.coop.ch/de/haushalt-tier/bekleidung/c/m_4145?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/bekleidung/c/m_4145?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'quantity', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'timestamp']]
products.to_excel(f'./output/clothes_' + date + '.xlsx', index = False)


