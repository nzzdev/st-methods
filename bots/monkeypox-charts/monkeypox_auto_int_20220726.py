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

# read data from Github
latest = pd.read_csv('https://raw.githubusercontent.com/globaldothealth/monkeypox/main/latest.csv')
latest['Endemic'] = latest['ID'].str[0]
latest = latest[(latest['Endemic'] == 'N') & (latest['Status'] == 'confirmed')]
latest['date'] = pd.to_datetime(latest['Date_entry'])
latest = latest.set_index('date')

# by countries
df = latest.groupby('Country_ISO3')[
    'ID'].count().reset_index(name = 'Wert')

df = df.sort_values('Wert', ascending=False)

# assign names to country codes and translate them
df['Country'] = df['Country_ISO3'].apply(lambda x: coco.convert(names=x, to='name_short', not_found=None))
df['Land'] = df['Country'].apply(lambda x: _(x))
# manual adjustments of country names
df['Land'] = df['Land'].str.replace('Iran, Islamische Republik', 'Iran')
df['Land'] = df['Land'].str.replace('Russia', 'Russland')
df['Land'] = df['Land'].str.replace('South Korea', 'Südkorea')

# Country codes from Q Choropleth
ids = pd.read_csv('q_countries.csv')
# merge df with Q codes
df = ids.merge(df, left_on = 'ID', right_on = 'Country_ISO3', how = 'left')

# set date for charts
date_notes = 'Stand: '+ datetime.now().strftime("%-d. %-m. %Y") +'<br> ¹ohne Fälle aus endemischen Ländern'


# get 2021 population data
pop = pd.read_csv('https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2022_TotalPopulationBySex.zip')
pop = pop[pop['Time'].isin([2021])]
pop = pop[['ISO3_code', 'PopTotal']].dropna()
# merge with df and calculate cases per 1 Mio. pop.
df = df.merge(pop, left_on = 'Country_ISO3', right_on = 'ISO3_code', how = 'left' )
df['Fälle pro 1 Mio. Einwohner'] = round(df['Wert']*1000/df['PopTotal'], 1)
df['Wert'] = round(df['Wert'], 0).fillna(0).astype(int).replace(0, '')


id_worldmap = 'd0be298e35165ab925d7292335e77bb7'  # linked in article
update_chart(id=id_worldmap, 
            data=df[['ID', 'Wert']],
            notes = date_notes)

# export for q table
df_q_table = df[['Land', 'Wert', 'Fälle pro 1 Mio. Einwohner']].rename(
    columns={'Land': ''}).dropna(subset = ['Wert']).sort_values(by = ['Fälle pro 1 Mio. Einwohner'], ascending = False).dropna(subset = ['Fälle pro 1 Mio. Einwohner'])
df_q_table.rename(columns = {'Wert': 'Fälle gesamt'}, inplace = True)


date_notes = 'Stand: '+ datetime.now().strftime("%-d. %-m. %Y")

id_q_table = 'd0be298e35165ab925d7292335e97175'  # linked in article
update_chart(id=id_q_table, 
            data=df_q_table,
            notes = date_notes)


# 7-day-average
df = latest.groupby(latest.index)['Status'].count()
df = df.rolling(7).mean().reset_index()

date_notes = 'Stand: '+ datetime.now().strftime("%-d. %-m. %Y") +'<br> ¹ohne Fälle aus endemischen Ländern'

update_chart(id='d0be298e35165ab925d7292335eb1ba0', 
            data=df,
            notes = date_notes)

