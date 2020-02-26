#!/usr/bin/env python
# coding: utf-8

# In[88]:


import pandas as pd
import pycountry_convert as pc
import datetime


# In[89]:


#Pulling Data in
df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv')


# In[90]:


#Classifying countries
def continents(elem):
    if elem == 'Mainland China':
        return 'China'
    if elem == 'US':
        return 'Nordamerika'
    if elem == 'UK':
        return 'Europa'
    if elem == 'Others':
        return 'Andere'
    try:
        country_code = pc.country_name_to_country_alpha2(elem, cn_name_format="default")
        continent_name = pc.country_alpha2_to_continent_code(country_code)
        if continent_name == "NA":
            return 'Nordamerika'
        if continent_name == 'EU':
            return "Europa"
        if continent_name == 'AS':
            return "Asien"
        if continent_name == 'AF':
            return "Afrika"
        if continent_name == 'OC':
            return "Ozeanien"
        return continent_name
    except:
        return elem
df["Continent"] = df["Country/Region"].apply(continents)
del df['Lat']
del df['Long']
con_df = df.groupby("Continent")[list(df)[3:]].sum().transpose()
con_df = con_df[["Europa", "Nordamerika", "Ozeanien", "Asien", "Andere"]].copy()


# In[91]:


con_df.to_csv(str(datetime.date.today())+"_coronainfektionen_nachland.csv")

