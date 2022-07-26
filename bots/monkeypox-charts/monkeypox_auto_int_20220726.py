import pandas as pd
import webbrowser
import pycountry
import gettext
from datetime import datetime
import os
import country_converter as coco
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
df = df.rename(columns={'confirmed': 'Bestätigt'})
df.drop('discarded', inplace=True, axis=True)
df.drop('suspected', inplace=True, axis=True)


# add totals column
df['Total'] = df.iloc[:, 1:].sum(axis=True)
df = df[df['Total']!=0].reset_index(drop = True)

# format integers
df = df.fillna(0)
df.iloc[:, 1:] = df.iloc[:, 1:].astype(int)
df['Country'] = df['Country'].str.strip()
df['Country_sum'] = df['Country']
df.loc[df['Country'].isin(['England', 'Scotland', 'Wales', 'Northern Ireland',
'United Kingdom']), 'Country_sum'] = 'United Kingdom'

df = df.groupby('Country_sum')['Total'].sum().reset_index()

df = df.sort_values('Total', ascending=False)
df.rename(columns = {'Country_sum': 'Country'}, inplace = True)

# replace Country names with our worldmap ids
df['Country'] = df['Country'].str.replace('Iran', 'Iran, Islamic Republic of')
df['Country'] = df['Country'].str.replace('Czech Republic', 'Czechia')

# remove unofficial countries
#df = df[df['Country']!='Kosovo']


df['Land'] = df['Country'].apply(lambda x: _(x))

df['Land'] = df['Land'].str.replace('Iran, Islamische Republik', 'Iran')
df['Land'] = df['Land'].str.replace('Russia', 'Russland')
df['Land'] = df['Land'].str.replace('Bosnia And Herzegovina', 'Bosnien-H.')
df['Land'] = df['Land'].str.replace('South Korea', 'Südkorea')


df = df[['Country', 'Land', 'Total']]
df['ID'] = df['Country'].apply(lambda x: coco.convert(names=x, to='ISO3', not_found=None))



# set date for charts
date_notes = 'Stand: '+ datetime.now().strftime("%-d. %-m. %Y")

ids = pd.read_csv('q_countries.csv')

# merge df with ids
df = ids.merge(df, on = 'ID', how = 'left')
df['Wert'] = df['Total'].fillna("")

pop = pd.read_csv('https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2022_TotalPopulationBySex.zip')
pop = pop[pop['Time'].isin([2021])]
pop = pop[['ISO3_code', 'PopTotal']]


df = df.merge(pop, left_on = 'ID', right_on = 'ISO3_code', how = 'left' )
df['Fälle pro 1 Mio. Einwohner'] = round(df['Total']*1000/df['PopTotal'], 1)
df.rename(columns = {'Total': 'Fälle gesamt'}, inplace = True)





id_worldmap = '4acf1a0fd4dd89aef4abaeefd0b6f4dc'  # linked in article
update_chart(id=id_worldmap, 
            data=df[['ID', 'Wert']],
            notes = date_notes)

# export for q table
df_q_table = df[['Land', 'Fälle gesamt', 'Fälle pro 1 Mio. Einwohner']].rename(
    columns={'Land': ''})

id_q_table = '4acf1a0fd4dd89aef4abaeefd0da5ac6'  # linked in article
update_chart(id=id_q_table, 
            data=df_q_table,
            notes = date_notes)
