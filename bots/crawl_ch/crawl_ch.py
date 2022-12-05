
import pandas as pd
from datetime import date, datetime as dt, timedelta
from bs4 import BeautifulSoup
import requests
import json
import os
from fake_useragent import UserAgent
import fnmatch



from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))



# Brot
url = 'https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=1'
ua_str = UserAgent().chrome
page = requests.get(url, headers={"User-Agent": ua_str})
soup = BeautifulSoup(page.content, "html.parser")

# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers={"User-Agent": ua_str})
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = dt.now().strftime("%Y-%m-%d %H:%M:%S")

products = products[['id', 'title', 'href', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]

date_today = date.today().strftime("%Y-%m-%d")
products.to_excel(f'./output/bread_coop_' + date_today + '.xlsx', index = False)

# Milch
url = 'https://www.coop.ch/de/lebensmittel/milchprodukte-eier/c/m_0055?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=1'
ua_str = UserAgent().chrome
page = requests.get(url, headers={"User-Agent": ua_str})
soup = BeautifulSoup(page.content, "html.parser")

# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/milchprodukte-eier/c/m_0055?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers={"User-Agent": ua_str})
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = dt.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/milk_coop_' + date_today + '.xlsx', index = False)

# Gemüse / Früchte
url = 'https://www.coop.ch/de/lebensmittel/fruechte-gemuese/c/m_0001?page=1&pageSize=60&q=%3AmostlyBought&sort=mostlyBought'
ua_str = UserAgent().chrome
page = requests.get(url, headers={"User-Agent": ua_str})
soup = BeautifulSoup(page.content, "html.parser")

# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fruechte-gemuese/c/m_0001?page=' + str(i+1) + '&pageSize=60&q=%3AmostlyBought&sort=mostlyBought'
    page = requests.get(url, headers={"User-Agent": ua_str})
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)
    
products['timestamp'] = dt.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/vegi_coop_' + date_today + '.xlsx', index = False)

# Fleisch
url = 'https://www.coop.ch/de/lebensmittel/fleisch-fisch/c/m_0087?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
ua_str = UserAgent().chrome
page = requests.get(url, headers={"User-Agent": ua_str})
soup = BeautifulSoup(page.content, "html.parser")

# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fleisch-fisch/c/m_0087?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers={"User-Agent": ua_str})
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)


products['timestamp'] = dt.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/meat_coop_' + date_today + '.xlsx', index = False)

# Vorräte
url = 'https://www.coop.ch/de/lebensmittel/vorraete/c/m_0140?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
ua_str = UserAgent().chrome
page = requests.get(url, headers={"User-Agent": ua_str})
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/vorraete/c/m_0140?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers={"User-Agent": ua_str})
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = dt.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/provision_coop_' + date_today + '.xlsx', index = False)

# Süsses & Snacks
url = 'https://www.coop.ch/de/lebensmittel/suesses-snacks/c/m_2506?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=1'
ua_str = UserAgent().chrome
page = requests.get(url, headers={"User-Agent": ua_str})
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/suesses-snacks/c/m_2506?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers={"User-Agent": ua_str})
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = dt.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/sweet_coop_' + date_today + '.xlsx', index = False)

# Getränke
url = 'https://www.coop.ch/de/lebensmittel/getraenke/c/m_2242?sort=mostlyBought&pageSize=60&page=1'
ua_str = UserAgent().chrome
page = requests.get(url, headers={"User-Agent": ua_str})
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/getraenke/c/m_2242?sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers={"User-Agent": ua_str})
    soup = BeautifulSoup(page.content, "html.parser")
    meta_json = str(soup.find_all("meta")[15])
    meta_json = meta_json.replace('<meta data-pagecontent-json=\'', '').replace('\'/>', '')
    data = json.loads(meta_json)
    
    # get prices from all products

    df = pd.DataFrame.from_dict(data['anchors'][0]['json']['elements'], orient = 'columns')

    products = pd.concat([products, df])
    products.reset_index(drop = True, inplace = True)

products['timestamp'] = dt.now().strftime("%Y-%m-%d %H:%M:%S")
products = products[['id', 'title', 'href', 'ratingAmount', 'ratingValue', 'brand', 'price', 'priceContext', 'priceContextHiddenText',	'priceContextPrice',	'priceContextAmount',	'udoCat', 'productAriaLabel',	'declarationIcons', 'timestamp']]
products.to_excel(f'./output/drinks_coop_' + date_today + '.xlsx', index = False)




### Preismonitor

today = dt.today()
past = today - timedelta(days = 28)

# data from today

df_t = pd.DataFrame()

for file in os.listdir(f'./output/'): 
    if fnmatch.fnmatch(file, '*coop_' + today.strftime('%Y-%m-%d') + '.xlsx'):
        
        print(file)

        df_ = pd.read_excel(f'./output/' + file)
        df_t = pd.concat([df_t, df_], ignore_index = True)

df_t = df_t.dropna(subset = 'price')

# exclude "Aktionen" and clean
df_t = df_t[~df_t['productAriaLabel'].str.contains('Aktion')]
df_t['title'] = df_t['title'].str.replace('\xa0', '')
df_t['title'] = df_t['title'].str.replace('&amp;', '&')

# only Prix Garantie
df_t = df_t[df_t['title'].str.contains('Prix Garantie')].copy()


# data from one month ago
week_day = past.isocalendar()[2]

# get starting date (Monday) for the respective week
start_date = past - timedelta(days=week_day-1) 

# Prints the list of dates in a current week
dates = [str((start_date + timedelta(days=i)).date()) for i in range(7)]
del dates[0]



food_drinks = ('drinks', 'sweet', 'provision', 'meat', 'vegi', 'milk', 'bread')

df_y = pd.DataFrame()
for i in food_drinks:
    try:
        df_ = pd.read_excel(f'./output/' + i + '_coop_' + past.strftime('%Y-%m-%d') + '.xlsx')
        df_y = pd.concat([df_y, df_], ignore_index = True)
    except:
        for j in dates:
            try:
                df_ = pd.read_excel(f'./output/' + i + '_coop_' + j + '.xlsx')
                df_y = pd.concat([df_y, df_], ignore_index = True)
            except:
                continue
            break
        
df_y = df_y.dropna(subset = 'price') 

# exclude "Aktionen" and clean
df_y = df_y[~df_y['productAriaLabel'].str.contains('Aktion')]
df_y['title'] = df_y['title'].str.replace('\xa0', '')
df_y['title'] = df_y['title'].str.replace('&amp;', '&')

# only Prix Garantie
df_y = df_y[df_y['title'].str.contains('Prix Garantie')].copy()

df_t = df_t[['id', 'title', 'price', 'priceContextAmount']].copy()
df_y = df_y[['id', 'title', 'price', 'priceContextAmount']].copy()
df_t.rename({'price': 'Neuer Preis'}, axis = 1, inplace = True)
df_y.rename({'price': 'Alter Preis'}, axis = 1, inplace = True)

df_t_y = df_t.merge(df_y, on = ['id', 'title', 'priceContextAmount'])
df_t_y.drop_duplicates(inplace = True)

df_t_y['Differenz'] = df_t_y['Neuer Preis'] - df_t_y['Alter Preis']
df_t_y['Differenz'] = df_t_y['Differenz'].round(1)
df_t_y = df_t_y[df_t_y['Differenz'] != 0]

df_t_y.loc[df_t_y['Differenz'] > 0, ''] = '↑' 
df_t_y.loc[df_t_y['Differenz'] < 0, ''] = '↓' 


df_t_y['title'] = df_t_y['title'].str.replace(' ca.', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Prix Garantie ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Betty Bossi ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Naturaplan ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Naturafarm ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' fettreduziert', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' Fettreduziert', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Delikatess-', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Delikatess ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Feiner ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Feine ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Hauchzarter ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Hauchzartes ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Saftige ', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' fein', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace(' grob', '', regex = False)
df_t_y['title'] = df_t_y['title'].str.replace('Arabica-Robusta-Mischung', '', regex = False)

# title fixes

bulkpacks = {'Apfelsaft': 'Apfelsaft 6l', 'Multivitaminsaft': 'Multivitaminsaft 6l', 'Orangensaft': 'Orangensaft 6l', 'Orangennektar': 'Orangennektar 9l', 
             'Hamburger': 'Hamburger 1kg', 'Chicken Nuggets': 'Chicken Nuggets 1kg', 'Cevapcici für Pfanne und Grill': 'Cevapcici 1kg', 'Hähnchenschenkel natur': 'Hähnchenschenkel natur 1kg', 
             'Sahnejoghurt nach griechischer Art': 'Sahnejoghurt griechische Art 1kg', 'Basmati Reis': 'Basmati Reis 1kg', 'Parboiled Spitzenreis Langkornreis': 'Parboiled Langkornreis 1kg', 
             'Blumenkohl': 'Blumenkohl 1kg', 'Rosenkohl': 'Rosenkohl 1kg', 'Brechbohnen': 'Brechbohnen 1kg', 'Weizenmehl Type': 'Weizenmehl'
            }

df_t_y['title'] = df_t_y['title'].astype(
    str).str.replace(r'\s\d.*', r'', regex=True)
df_t_y['title'] = df_t_y['title'].astype(
    str).str.replace(r'\smit\s.*', r'', regex=True)
df_t_y['title'] = df_t_y['title'].astype(
    str).str.replace(' ca.', '', regex=False)

# Fix for large quantities
df_t_y['title'] = df_t_y['title'].astype(str).replace(bulkpacks)

df_t_y.sort_values(by = ['Differenz'], inplace = True, ascending = False)
df_t_y = df_t_y[['', 'title', 'Alter Preis', 'Neuer Preis']].copy()
df_t_y.rename({'title': ''}, axis = 1, inplace = True)

update_chart(id = '8676bad64564b4740f74b6d5d0757a95',
                 data = df_t_y, notes=notes)

