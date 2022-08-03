#!/usr/bin/env python
# coding: utf-8

from helpers import *
import pandas as pd
import requests
import pytz
from datetime import timezone, datetime, timedelta
import os

# Set Working Directory
os.chdir(os.path.dirname(__file__))

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'cache-control': 'no-cache',
    'referer': 'https://www.meteoschweiz.admin.ch/home/messwerte.html?param=messwerte-lufttemperatur-10min&station=SMA&chart=hour'
}

# Daten abfragen
r = requests.get('https://www.meteoschweiz.admin.ch/product/input/measured-values/chartData/temperature_hour/chartData.temperature_hour.SMA.de.json', headers = headers)
data = r.json()

# Resultat in Dataframe umwandeln
def serialize(seriesfilter, name):

    series = list(filter(lambda x: x['id'] == seriesfilter, data['series']))[0]['data']

    df = pd.DataFrame(series)
    df.columns = ['date', 'temp']
    df['date'] = pd.to_datetime(df['date'], utc=True, unit='ms')
    df['date'] = df['date'].dt.tz_convert(pytz.timezone('Europe/Berlin'))
    df['type'] = name

    return df

# Dateframes zusammenfügen
df = pd.concat([
    serialize('temperature_hour.SMA.de.series.2', 'Stundenminimum'),
    # serialize('temperature_hour.SMA.de.series.1', 'Stundenmittel'),
    serialize('temperature_hour.SMA.de.series.3', 'Stundenmaximum'),
])

# Daten pivotieren
df = pd.pivot_table(df, index=['date'], columns='type', values='temp')

# Hitzerekord hinzufügen
df['Hitzerekord von 2003 (36°)'] = 36

# Spalten auswählen
df = df[['Stundenminimum', 'Stundenmaximum', 'Hitzerekord von 2003 (36°)']]

# Annotationen hinzufügen: Höchstwerte der letzten beiden Tagen + aktuell
now = df.reset_index().iloc[-1]['date'].normalize()
events = []
for i in range(0, 3):
    new_date = now - timedelta(days = i)
    df_day = df[df.index.get_level_values('date').normalize() == (now - timedelta(days = i))].sort_values('Stundenmaximum', ascending=False).reset_index()
    n_max = df_day.iloc[0]
    events.append({
        'type': 'point',
        'date': n_max.date.strftime('%Y-%m-%d %H:%M'),
        'label': '%s° Celsius am %s' % (str(n_max.Stundenmaximum).replace('.', ','), n_max.date.strftime("%-d. %B"))
    })

# index in Str umwandeln für Q
df.index = df.index.strftime('%Y-%m-%d %H:%M')

# Update
update_chart(
    id = 'd0be298e35165ab925d72923352cad8b',
    data = df[['Stundenminimum', 'Stundenmaximum', 'Hitzerekord von 2003 (36°)']],
    # title = "Aktuell beträgt die Temperatur in Zürich %s Grad" % current_temp,
    notes="Messstation Zürich Fluntern<br />Zuletzt aktualisiert: %s Uhr" % datetime.strptime(df.reset_index().iloc[-1]['date'], '%Y-%m-%d %H:%M').astimezone(pytz.timezone('Europe/Berlin')).strftime("%-d. %-m. %Y, %H.%M"),
    events = events
)

