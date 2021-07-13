#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
from datetime import timezone, datetime, timedelta

import sys
from io import StringIO
from pathlib import Path

import os
import sys

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



# ## Zürichsee
# https://q.st.nzz.ch/item/6b50824faafb1db49507dbc8cc452e5c


# Get Data
chartid = 'e733bf4b283720fe5a16bd1f91d0804a'
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
df = df.rename(columns = {'BAFU_2209_PegelRadarSchacht': 'Messwert, Gefahrenstufe:'})

df = df.head()

df = df[['Zeitstempel', 'Messwert, Gefahrenstufe:', '2', '3', '4', '5']]

update_chart(
    id = chartid,
    data = df,
    notes = "Done!"
)

print("Done")
quit()

# ## Limmat
# https://q.st.nzz.ch/editor/chart/6b50824faafb1db49507dbc8cc476129

# In[142]:


# Get Data
url = 'https://www.hydrodaten.admin.ch/lhg/az/dwh/csv/BAFU_2099_AbflussRadarSchacht.csv'
df = get_data(url)

# Zeitzone umwandeln
df['Zeitstempel'] = df['Time'].apply(lambda x: x.astimezone('Europe/Berlin').strftime('%Y-%m-%d %H:%M'))

# Gefahrenzone hinzufügen
df['2'] = 350
df['3'] = 450
df['4'] = 530
df['5'] = 600

# Rename
df = df.rename(columns = {'BAFU_2099_AbflussRadarSchacht': 'Messwert, Gefahrenstufe:'})

df[['Zeitstempel', 'Messwert, Gefahrenstufe:', '2', '3', '4', '5']].to_clipboard(index=False)


# ## Sihl
# https://q.st.nzz.ch/item/6b50824faafb1db49507dbc8cc481e93

# In[143]:


# Get Data
url = 'https://www.hydrodaten.admin.ch/lhg/az/dwh/csv/BAFU_2176_AbflussRadarSchacht.csv'
df = get_data(url)

# Zeitzone umwandeln
df['Zeitstempel'] = df['Time'].apply(lambda x: x.astimezone('Europe/Berlin').strftime('%Y-%m-%d %H:%M'))

# Gefahrenzone hinzufügen
df['2'] = 100
df['3'] = 200
df['4'] = 300
df['5'] = 400

# Rename
df = df.rename(columns = {'BAFU_2176_AbflussRadarSchacht': 'Messwert, Gefahrenstufe:'})

df[['Zeitstempel', 'Messwert, Gefahrenstufe:', '2', '3', '4', '5']].to_clipboard(index=False)


# ## Badewannen

# In[114]:


badewanne = 0.18

sihl_m2_gester = 12
sihl_m2_heute = 29

limmat_m2_gestern = 276
limmat_m2_heute = 297


# In[115]:


print("Sihl gestern 12 Uhr: %s Badewannen/s" % round(sihl_m2_gester / badewanne))
print("Sihl heute 12 Uhr: %s Badewannen/s" % round(sihl_m2_heute / badewanne))

print("Limmat gestern 12 Uhr: %s Badewannen/s" % round(limmat_m2_gestern / badewanne))
print("Limmat heute 12 Uhr: %s Badewannen/s" % round(limmat_m2_heute / badewanne))


# In[133]:


# Differenz Gestern 12 Uhr bis heute 12 Uhr
anstieg = round(df.iloc[-1]['Messwert, Gefahrenstufe:'] - df[df.Time >= '2021-07-12 11:00'].iloc[0]['Messwert, Gefahrenstufe:'], 2)


# In[144]:


anstieg = 0.05
lake = 88.66 * 1000 * 1000
kubik = lake * anstieg
badewanne = 0.18

round(kubik / badewanne)


# In[ ]:





# In[125]:


pool = 50 * 25 * 2

(lake * anstieg) / pool


# In[123]:


pool


# In[150]:


katzensee = 0.84 * 1000 * 1000#kubikmeter
katzensee = 840000
kubik / katzensee


# In[ ]:




