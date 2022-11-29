
import pandas as pd
from datetime import date, datetime as dt
from bs4 import BeautifulSoup
import requests
import json
import os
from fake_useragent import UserAgent



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

