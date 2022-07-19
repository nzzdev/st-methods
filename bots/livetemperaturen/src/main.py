#!/usr/bin/env python
# coding: utf-8

from helpers import *
import pandas as pd
import requests
from datetime import timezone, datetime, timedelta
from fake_useragent import UserAgent
from datetime import datetime
import sys
import os

# Set Working Directory
os.chdir(os.path.dirname(__file__))

ua = UserAgent()

headers = {
    'user-agent': ua['google chrome'],
    'cache-control': 'no-cache',
    'referer': 'https://www.meteoschweiz.admin.ch/home/messwerte.html?param=messwerte-lufttemperatur-10min&station=SMA&chart=hour'
}

r = requests.get('https://www.meteoschweiz.admin.ch/product/input/measured-values/chartData/temperature_hour/chartData.temperature_hour.SMA.de.json', headers = headers)

data = r.json()

def serialize(seriesfilter, name):

    series = list(filter(lambda x: x['id'] == seriesfilter, data['series']))[0]['data']

    df = pd.DataFrame(series)
    df.columns = ['date', 'temp']
    df['date'] = df['date'].apply(lambda x: datetime.fromtimestamp(x / 1000))
    df['type'] = name

    return df

df = pd.concat([
    serialize('temperature_hour.SMA.de.series.2', 'Stundenminimum'),
    # serialize('temperature_hour.SMA.de.series.1', 'Stundenmittel'),
    serialize('temperature_hour.SMA.de.series.3', 'Stundenmaximum'),
])

df = pd.pivot_table(df, index='date', columns='type', values='temp')

df = df[['Stundenminimum', 'Stundenmaximum']]

update_chart(
    id = 'd0be298e35165ab925d72923352cad8b',
    data = df,
    subtitle="Stündlich aktualisierte Daten",
    notes="zuletzt aktualisiert: %s Uhr" % df.reset_index().iloc[-1]['date'].strftime("%-d. %-m. %Y, %H.%M")
)