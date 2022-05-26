import pandas as pd
import webbrowser
import pycountry
import gettext
from datetime import datetime
import os
german = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['de'])
german.install()

from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# read data from google sheet
sheet_id = '1CEBhao3rMe-qtCbAgJTn5ZKQMRFWeAeaiXFpBY3gbHE'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
df_roh = pd.read_csv(url)

# Pivot wider
df = df_roh.groupby(['Country','Status'])['ID'].count().unstack().reset_index()
df= df.rename(columns={'confirmed':'Bestätigt', 'suspected':'Verdacht'})

# add totals column
df['Total']=df.iloc[:,1:].sum(axis=True)


# format integers
df = df.fillna(0)
df.iloc[:,1:] = df.iloc[:,1:].astype(int)

# sum up country-parts of united kingdom
uk_idx = df[df['Country'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland'])].index
uk_row = df.iloc[uk_idx].sum()
uk_row.loc['Country'] = 'United Kingdom'
df =df.append(uk_row, ignore_index=True)
df.drop(uk_idx, inplace=True)

# replace Country names with our worldmap ids
df['Country'] = df['Country'].str.replace('Czech Republic', 'Czechia')

df=df.sort_values('Total', ascending=False)

# Catch country name if not in pycountry
for name in df['Country'].to_list():
    if pycountry.countries.get(name=name)== None:
        raise ValueError('Country name is not recognised by pycountry:', name)

# Add German country names and flags
def get_german_name(name):
    country = pycountry.countries.get(name=name)
    return _(country.name)

def get_flag(name):
    country = pycountry.countries.get(name=name)
    return country.flag

df['Land'] = df['Country'].apply(get_german_name)
df['Flagge'] =  df['Country'].apply(get_flag)

df = df[['Country', 'Land', 'Flagge','Bestätigt', 'Verdacht', 'Total']]

# save csv
now = datetime.now()
time_now = now.strftime("%Y%m%d-%Hh%M")

df.to_csv('data/'+ time_now+'.csv', index=False)

# export for q world map
ids = pd.read_csv('country_ids.csv')
df_worldmap =df.copy()

# Rename countries to match world map ids
df_worldmap['Country'] = df_worldmap['Country'].str.replace('United States','United States of America')

# merge df with ids
df_worldmap = df_worldmap.rename(columns ={'Country':'ID', 'Total':'Wert'})
df_worldmap = ids.merge(df_worldmap[['ID', 'Wert']], how='left').sort_values('Wert', ascending=False)

# check if all countries were merged
if df_worldmap['Wert'].sum() != df['Total'].sum():
    raise ValueError('Some country names do not correspond with our world map ids. Please rename manually.')

df_worldmap=df_worldmap.sort_values('ID', key=lambda col: col.str.lower())
df_worldmap['Wert'] = df_worldmap['Wert'].fillna("")

id_worldmap_test = '043bfe3491dac666e4bb4fe97a4101bf' # for testing
id_worldmap = '4acf1a0fd4dd89aef4abaeefd0b6f4dc' # linked in article

update_chart(id=id_worldmap, data=df_worldmap)

# export for q table
df_q_table = df[['Land', 'Flagge', 'Bestätigt', 'Verdacht','Total']].rename(columns = {'Land':'', 'Flagge':''})

id_q_table_test = '4913f749b598fb2ecc9721cb17187e05' # for testing
id_q_table = '4acf1a0fd4dd89aef4abaeefd0da5ac6' # linked in article

update_chart(id=id_q_table, data=df_q_table)
