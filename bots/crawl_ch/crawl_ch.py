
import pandas as pd
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json
import os
import sys
#import openpyxl
# from requests_ip_rotator import ApiGateway



sys.path.append(os.path.dirname((os.path.dirname(__file__))))

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# Headers for HTTP_Request
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'de-DE,de;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "macOS",
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    'origin': 'https://www.coop.ch',
    # 'cookie': 'JSESSIONID=E4360E293731FFAB8F4FFB36E0BFCB39; language=de; insiemeLBcookie=!RDp7diw1q4ltpHzdB1LaIpWJ35V0c4R151PZmUE7wh/Nip7iSl0YqpOmlVlQ54lNlTqNuS33ke02qqZlUmrg84xbGbZEr9SlqvwkkJc3NEXb; aem-insiemeLBcookie=!xPTSf6O5Ykw2FP2k9RTj68UgdcOFKdi4ssirUqcKwk5c7WyeXU5x5m6yuVNr2J74K/ve6PIgcUiM2agwyGfUOPscNDdqEjzy6ShyV2rLA/eD; accessmode=external; www-insiemeLBcookie=!Phn+hg0zaAjVvHDdB1LaIpWJ35V0c1ia6G3Rss6wFczVc4ae5a3FrD9oO/Qf9NJqhcg1MM2Yo++KVjFnnDxuw172vpuKeAWBWY2W9mexhR1e; TS01d253ce=0188e1aa7f9a4037b87672f01201d630c35dc4f579cf5e452950fa99716fa17f40c68b79668e995a41ea71a6fdbee5fbb2a08c02c642d285b36db5163a462ba54a0d3f453517bca5e8450e2ecfbac3953d27d69f56ab4bd48503bd12783e0158352b6370d748b354459e6542067396bb23f6b7cb59fd5f44eaa7c5b1a9d15dd56ef4600c88bb716559a4893d5bb6dff42da971b94d; _gaexp=GAX1.2.nDLcW6hrSn-39NqV-xC4HA.19347.1; _cs_mk=0.3167821074988282_1663663970300; _gcl_au=1.1.1015222477.1663663970; _gid=GA1.2.909835245.1663663970; _ga=GA1.1.1478474225.1663663970; _ga_FDQTHHLP9T=GS1.1.1663663970.1.1.1663663970.60.0.0; _uetsid=9b51332038c111edb794f5f1d858b3ee; _uetvid=9b514cf038c111edaa55fd39000bdec2; _cs_c=0; _cs_id=cbbe6612-8935-a7ff-f2f8-36067e5f002a.1663663970.1.1663663970.1663663970.1.1697827970419; tws_session=%7B%22pageCount%22%3A1%2C%22calcToggle%22%3Atrue%2C%22cv%22%3A%22%22%2C%22pageHistory%22%3A%5B%7B%22breadcrumb1%22%3A%22lebensmittel%2Fbrot%20%26amp%3B%20backwaren%22%2C%22breadcrumb2%22%3A%22%2Fde%2Flebensmittel%2Fbrot-backwaren%2Fc%2Fm_0115%22%2C%22time%22%3A1663663970%7D%5D%2C%22visitorType%22%3A%22New%22%2C%22productDetailClick%22%3A0%7D; tws_camp=%7B%22medium%22%3A%22(none)%22%2C%22source%22%3A%22(direct)%22%7D; _gat_ga360=1; _fbp=fb.1.1663663970520.1095239851; _cs_s=1.5.0.1663665770613; utag_main=v_id:01835a1997c4000ace60ffc4aeed05075006e06d00c48$_sn:1$_se:3$_ss:0$_st:1663665794229$ses_id:1663663970245%3Bexp-session$_pn:1%3Bexp-session$gaClientId:1478474225.1663663970%3Bexp-session'
}

# Create AWS-Gateway
#key = os.environ['AWS_GATEWAY_KEY']
#secret = os.environ['AWS_GATEWAY_SECRET']

# Create gateway object and initialise in AWS
# gateway = ApiGateway("https://www.coop.ch", access_key_id = key, access_key_secret = secret, regions=["eu-west-3"])
# gateway.start(force=True)

# Assign gateway to session

# Moved Requests Get to a function in case we need to change it again (everywhere)
def get_data(url):
    print('https://journalist.sh/proxy.php?url=%s' % url)
    return requests.get('https://journalist.sh/proxy.php?url=%s' % url)
    session = requests.Session()
    session.mount("https://www.coop.ch", gateway)
    # return session.get(url)
    return session.get(url, headers=headers)

r = requests.get('https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115/facets?q=%3AmostlyBought&sort=mostlyBought&pageSize=60&compiledTemplates%5B%5D=productTile-new&openFilter=worldNameFacet&changedFilter=worldNameFacet&_=1663678558780')
print(r.text)
print(r)
exit()


# Brot
url = 'https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=1'

# page = requests.get(url, headers=headers, proxies=proxies)
page = get_data(url)
print(page.text)
print(page)
# open('facebook.html', 'wb').write(page.content)

# Delete gateways
# gateway.shutdown()

exit()

# print(page.text)
# print(page)
soup = BeautifulSoup(page.content, "html.parser")
soup.find_all('a', class_ = 'pagination__page')

# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/brot-backwaren/c/m_0115?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/milchprodukte-eier/c/m_0055?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fruechte-gemuese/c/m_0001?page=' + str(i+1) + '&pageSize=60&q=%3AmostlyBought&sort=mostlyBought'
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/fleisch-fisch/c/m_0087?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/vorraete/c/m_0140?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/suesses-snacks/c/m_2506?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/lebensmittel/getraenke/c/m_2242?sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/haushalt-kueche/c/m_0298?q=%3AtopRated&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/reinigung-putzen/c/m_0279?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/toiletten-haushaltpapier/c/m_0288?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/buero-papeterie/c/m_0314?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/elektroartikel-batterien/c/m_0324?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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
page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.content, "html.parser")
# get number of last pagination page
number = pd.to_numeric(soup.find_all('a', class_ = 'pagination__page')[-1].text)

prices = []
units = []
products = pd.DataFrame()

for i in range(number):
    url = 'https://www.coop.ch/de/haushalt-tier/bekleidung/c/m_4145?q=%3Arelevance&sort=mostlyBought&pageSize=60&page=' + str(i+1)
    page = requests.get(url, headers=headers)
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


