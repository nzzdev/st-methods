import pandas as pd
import webbrowser
import pycountry
import gettext
from datetime import datetime
import os
german = gettext.translation(
    'iso3166', pycountry.LOCALES_DIR, languages=['de'])
german.install()

from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# read data from google sheet
sheet_id = '1CEBhao3rMe-qtCbAgJTn5ZKQMRFWeAeaiXFpBY3gbHE'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
df_roh = pd.read_csv(url)

# Pivot wider
df = df_roh.groupby(['Country', 'Status'])[
    'ID'].count().unstack().reset_index()
df = df.rename(columns={'confirmed': 'Bestätigt', 'suspected': 'Verdacht'})
df.drop('discarded', inplace=True, axis=True)

# add totals column
df['Total'] = df.iloc[:, 1:].sum(axis=True)
df = df[df['Total']!=0].reset_index(drop = True)

# format integers
df = df.fillna(0)
df.iloc[:, 1:] = df.iloc[:, 1:].astype(int)

# sum up UK and France
def sum_up_countries(df, subcountries, new_name):
    country_idx = df[df['Country'].isin(subcountries)].index
    country_row = df.iloc[country_idx].sum()
    country_row.loc['Country'] = new_name
    df =df.append(country_row, ignore_index=True)
    df.drop(country_idx, inplace=True)
    return df.reset_index(drop=True)
    
df = sum_up_countries(df, ['England', 'Scotland', 'Wales', 'Northern Ireland'], 'United Kingdom' )
df = sum_up_countries(df, ['France', 'French Guiana'], 'France' )

df = df.sort_values('Total', ascending=False)

# replace Country names with our worldmap ids
df['Country'] = df['Country'].str.replace('Iran', 'Iran, Islamic Republic of')
df['Country'] = df['Country'].str.replace('Czech Republic', 'Czechia')

# Catch country name if not in pycountry
for name in df['Country'].to_list():
    if pycountry.countries.get(name=name)== None and pycountry.countries.get(common_name =name) == None:
        raise ValueError('Country name is not recognised by pycountry:', name)

# get country object, using common name if there is one
def get_common_name(name):
    if pycountry.countries.get(common_name=name) == None:
        country = pycountry.countries.get(name=name)
    else:
        country = pycountry.countries.get(common_name=name)
    return country

# return german name
def get_german_name(name):
    country = get_common_name(name)
    if pycountry.countries.get(common_name=name) == None:
        country = country.name
    else:
        country = country.common_name
    return (country)

# return flag
def get_flag(name):
    country = get_common_name(name)
    return country.flag

df['Land'] = df['Country'].apply(get_german_name)
df['Flagge'] = df['Country'].apply(get_flag)
df['Land'] = df['Land'].str.replace('Iran, Islamische Republik', 'Iran')

df = df[['Country', 'Land', 'Flagge', 'Bestätigt', 'Verdacht', 'Total']]

# save csv
#now = datetime.now()
#time_now = now.strftime("%Y%m%d-%Hh%M")
#df.to_csv('data/'+ time_now+'.csv', index=False)

# set date for charts
date_notes = 'Stand: '+ datetime.now().strftime("%-d. %-m. %Y")

# export for q world map
ids = pd.read_csv('country_ids.csv')
df_worldmap = df.copy()

# Rename countries to match world map ids
df_worldmap['Country'] = df_worldmap['Country'].str.replace(
    'United States', 'United States of America')
df_worldmap['Country'] = df_worldmap['Country'].str.replace(
    'Iran, Islamic Republic of', 'Iran')

# merge df with ids
df_worldmap = df_worldmap.rename(columns={'Country': 'ID', 'Total': 'Wert'})
df_worldmap = ids.merge(df_worldmap[['ID', 'Wert']], how='left').sort_values(
    'Wert', ascending=False)

# to check locally if all countries were recognised by q_worldmap
#print('Total Worldmap:', str(df_worldmap['Wert'].sum()))
#print('Total DF:', str(df['Total'].sum()))
#df_worldmap.to_csv('test_worldmap.csv', index=False)

# check if all countries were merged
if df_worldmap['Wert'].sum() != df['Total'].sum():
    raise ValueError(
        'Some country names do not correspond with our world map ids. Please rename manually.')

df_worldmap = df_worldmap.sort_values('ID', key=lambda col: col.str.lower())
df_worldmap['Wert'] = df_worldmap['Wert'].fillna("")

id_worldmap = '4acf1a0fd4dd89aef4abaeefd0b6f4dc'  # linked in article
update_chart(id=id_worldmap, 
            data=df_worldmap,
            notes = date_notes)

# export for q table
df_q_table = df[['Land', 'Flagge', 'Bestätigt', 'Verdacht', 'Total']].rename(
    columns={'Land': '', 'Flagge': ''})

id_q_table = '4acf1a0fd4dd89aef4abaeefd0da5ac6'  # linked in article
update_chart(id=id_q_table, 
            data=df_q_table,
            notes = date_notes)
