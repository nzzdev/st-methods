#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
from io import StringIO
import os

from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))

def get_data(url):
    r = requests.get(url)
    df = pd.read_csv(StringIO(r.text), sep=",")

    # Convert Time
    df['Time'] = pd.to_datetime(df['Time'])

    # From 7.7
    df = df[df.Time >= '2021-07-07 00:00']
    
    return df

def get_last_update(df):
    return df.tail(1).iloc[0]['Time'].astimezone('Europe/Berlin').strftime('%d. %-m., %H.%M Uhr')


#------------------------ Zürichsee
# https://q.st.nzz.ch/item/6b50824faafb1db49507dbc8cc452e5c


# Get Data
chartid = '6b50824faafb1db49507dbc8cc452e5c'
url = 'https://www.hydrodaten.admin.ch/lhg/az/dwh/csv/BAFU_2209_PegelRadarSchacht.csv'
df = get_data(url)

# Zeitzone umwandeln
df['Zeitstempel'] = df['Time'].apply(lambda x: x.astimezone('Europe/Berlin').strftime('%Y-%m-%d %H:%M'))

# Gefahrenzone hinzufügen
df['2'] = 406.25
df['3'] = 406.4
df['4'] = 406.6
df['5'] = 406.85

# Rename
df = df.rename(columns = {'BAFU_2209_PegelRadarSchacht': 'Messwert; Gefahrenstufe:'})

# Resample (1 Entry per hour)
df = df.resample('1H', on='Time').first()

# Set Index
df = df.set_index('Zeitstempel')

update_chart(
    id = chartid,
    data = df[['Messwert; Gefahrenstufe:', '2', '3', '4', '5']],
    notes = "Die Messwerte sind Rohdaten, welche Fehler enthalten können.<br />Letzte Messung: %s" 
      % get_last_update(df)
)

#------------------------ Limmat
# https://q.st.nzz.ch/editor/chart/6b50824faafb1db49507dbc8cc476129

# Get Data
url = 'https://www.hydrodaten.admin.ch/lhg/az/dwh/csv/BAFU_2099_AbflussDrucksondeGewaesser.csv'
chartid = '6b50824faafb1db49507dbc8cc476129'
df = get_data(url)

# Zeitzone umwandeln
df['Zeitstempel'] = df['Time'].apply(lambda x: x.astimezone('Europe/Berlin').strftime('%Y-%m-%d %H:%M'))

# Gefahrenzone hinzufügen
df['2'] = 350
df['3'] = 450
df['4'] = 530
df['5'] = 600

# Rename
df = df.rename(columns = {'BAFU_2099_AbflussDrucksondeGewaesser': 'Messwert; Gefahrenstufe:'})

# Resample (1 Entry per hour)
df = df.resample('1H', on='Time').first()

# Set Index
df = df.set_index('Zeitstempel')

update_chart(
    id = chartid,
    data = df[['Messwert; Gefahrenstufe:', '2', '3', '4', '5']],
    notes = "Die Messwerte sind Rohdaten, welche Fehler enthalten können.<br />Letzte Messung: %s" 
      % get_last_update(df)
)

#------------------------ Sihl
# https://q.st.nzz.ch/item/6b50824faafb1db49507dbc8cc481e93

# Get Data
url = 'https://www.hydrodaten.admin.ch/lhg/az/dwh/csv/BAFU_2176_AbflussRadarSchacht.csv'
chartid = '6b50824faafb1db49507dbc8cc481e93'
df = get_data(url)

# Zeitzone umwandeln
df['Zeitstempel'] = df['Time'].apply(lambda x: x.astimezone('Europe/Berlin').strftime('%Y-%m-%d %H:%M'))

# Gefahrenzone hinzufügen
df['2'] = 100
df['3'] = 200
df['4'] = 300
df['5'] = 400

# Rename
df = df.rename(columns = {'BAFU_2176_AbflussRadarSchacht': 'Messwert; Gefahrenstufe:'})

# Set Index
df = df.set_index('Zeitstempel')

update_chart(
    id = chartid,
    data = df[['Messwert; Gefahrenstufe:', '2', '3', '4', '5']],
    notes = "Die Messwerte sind Rohdaten, welche Fehler enthalten können.<br />Letzte Messung: %s" 
      % get_last_update(df)
)

#------------------------ Vierwaldstättersee
# https://q.st.nzz.ch/editor/chart/34937bf850cf702a02c3648cdf22ffba

# Get Data
url = 'https://www.hydrodaten.admin.ch/lhg/az/dwh/csv/BAFU_2207_PegelDrucksondeSchacht.csv'
       
chartid = '34937bf850cf702a02c3648cdf22ffba'
df = get_data(url)

# Zeitzone umwandeln
df['Zeitstempel'] = df['Time'].apply(lambda x: x.astimezone('Europe/Berlin').strftime('%Y-%m-%d %H:%M'))

# Gefahrenzone hinzufügen
df['2'] = 434
df['3'] = 434.25
df['4'] = 434.45
df['5'] = 434.75

# Rename
df = df.rename(columns = {'BAFU_2207_PegelDrucksondeSchacht': 'Messwert; Gefahrenstufe:'})

# Resample (1 Entry per hour)
df = df.resample('1H', on='Time').first()

# Set Index
df = df.set_index('Zeitstempel')

update_chart(
    id = chartid,
    data = df[['Messwert; Gefahrenstufe:', '2', '3', '4', '5']],
    notes = "Die Messwerte sind Rohdaten, welche Fehler enthalten können.<br />Letzte Messung: %s" 
      % get_last_update(df)
)


#------------------------ Bielersee
# https://q.st.nzz.ch/editor/chart/bc7500f99eb2b7328406d6abbdd24b58

# Get Data
url = 'https://www.hydrodaten.admin.ch/lhg/az/dwh/csv/BAFU_2208_PegelRadar.csv'
       
chartid = 'bc7500f99eb2b7328406d6abbdd24b58'
df = get_data(url)

# Zeitzone umwandeln
df['Zeitstempel'] = df['Time'].apply(lambda x: x.astimezone('Europe/Berlin').strftime('%Y-%m-%d %H:%M'))

# Gefahrenzone hinzufügen
df['2'] = 429.8
df['3'] = 430.05
df['4'] = 430.35
df['5'] = 430.6

# Rename
df = df.rename(columns = {'BAFU_2208_PegelRadar': 'Messwert; Gefahrenstufe:'})

# Resample (1 Entry per hour)
df = df.resample('1H', on='Time').first()

# Set Index
df = df.set_index('Zeitstempel')

update_chart(
    id = chartid,
    data = df[['Messwert; Gefahrenstufe:', '2', '3', '4', '5']],
    notes = "Die Messwerte sind Rohdaten, welche Fehler enthalten können.<br />Letzte Messung: %s" 
      % get_last_update(df)
)