#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 21 10:12:12 2022

@author: florianseliger, matthias benz
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import requests
import os
import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))


## Swissgrid data

path = "https://www.swissgrid.ch/dam/dataimport/energy-statistic/EnergieUebersichtCH-2021.xlsx"
ch_2021 = pd.read_excel(path, sheet_name="Zeitreihen0h15")
ch_2021.drop([0], inplace=True)

path = "https://www.swissgrid.ch/dam/dataimport/energy-statistic/EnergieUebersichtCH-2022.xlsx"
ch_2022 = pd.read_excel(path, sheet_name="Zeitreihen0h15")
ch_2022.drop([0], inplace=True)

swissgrid = pd.concat([ch_2021, ch_2022])

swissgrid.rename(columns={"Unnamed: 0" : "Tag", "Summe endverbrauchte Energie Regelblock Schweiz\nTotal energy consumed by end users in the Swiss controlblock" : "Endverbrauch", "Summe produzierte Energie Regelblock Schweiz\nTotal energy production Swiss controlblock" : "ProduktionSchweiz" , "Summe verbrauchte Energie Regelblock Schweiz\nTotal energy consumption Swiss controlblock" : "Gesamtlast"}, inplace=True)
swissgrid.Endverbrauch = swissgrid.Endverbrauch.astype(float)
swissgrid.ProduktionSchweiz = swissgrid.ProduktionSchweiz.astype(float)
swissgrid.Gesamtlast = swissgrid.Gesamtlast.astype(float)
swissgrid['Tag'] = pd.to_datetime(swissgrid['Tag'],  format = '%d.%m.%Y %H:%M')
#restliche Spalten rauswerfen
swissgrid = swissgrid[["Tag", "Endverbrauch", "ProduktionSchweiz", "Gesamtlast"]]

#Tages-Summen für die Gesamtlast (und den Endverbrauch etc.) bilden
swissgrid = swissgrid.resample('D', on='Tag').sum()

swissgrid.reset_index(inplace=True)

#jetzt transformieren wir noch die Werte von kWh in GWh
swissgrid["Endverbrauch"] = swissgrid["Endverbrauch"].div(1000000)
swissgrid["ProduktionSchweiz"] = swissgrid["ProduktionSchweiz"].div(1000000)
swissgrid["Gesamtlast"] = swissgrid["Gesamtlast"].div(1000000)

#jetzt berechnen wir den rollierenden 7-Tages-Durchschnitt bei der Gesamtlast
swissgrid["7-Roll-Avg-Gesamtlast"] = swissgrid["Gesamtlast"].rolling(7, min_periods=7).mean()

#wir schmeissen noch die letzte Zeile (den letzten Tag) raus, da die Daten dort nicht vollständig sind
swissgrid.drop(swissgrid.tail(1).index,inplace=True)


## Swiss energy data

swiss_energy = pd.read_csv('./swiss_energy.csv')
swiss_energy['Tag'] = pd.to_datetime(swiss_energy['Tag'])
swiss_energy['Tag'] = swiss_energy['Tag'].dt.date

## Entsoe data

last_date_swiss_energy = swiss_energy['Tag'].max()
first_date_entsoe = last_date_swiss_energy + timedelta(days = 1)

date_today = datetime.today().date()


data = {}
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

for single_date in daterange(first_date_entsoe, date_today):
    url = 'https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=' + single_date.strftime('%d.%m.%Y') + '+00:00|CET|DAY&biddingZone.values=CTY|10YCH-SWISSGRIDZ!CTY|10YCH-SWISSGRIDZ&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2)'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find('tbody')

    load = []
    load_est = []
    for i in range(1, 49, 2):
        load.append(results.find_all('span')[i].text.strip())
    for i in range(0, 48, 2):
        load_est.append(results.find_all('span')[i].text.strip())
    # wir müssen mit 'N/A'-Werten in der 3. Tabellenspalte von den Entsoe-Tabellen umgehen und diese mit den Schätzwerten (2. Tabellenspalte) ersetzen
    df_load = pd.DataFrame(list(zip(load, load_est)),
               columns = ['load', 'load_est'])
    df_load.loc[df_load['load'] == 'N/A', 'load'] = df_load['load_est']
    df_load['load_est'] = pd.to_numeric(df_load['load_est'])
    # wir speichern die Tagessummen zusammen mit dem Datum in einem dictionary, das wir dann in ein pd.DataFrame umwandeln können.
    data[single_date.strftime('%Y-%m-%d')] = df_load['load_est'].sum()


entsoe = pd.DataFrame(data.items(), columns = ['Tag', 'Last'])

swiss_energy = pd.concat([swiss_energy[['Tag', 'Last']], entsoe], ignore_index = True)

swiss_energy.to_csv(f'./swiss_energy.csv', index = False)

#MWh -> GWh
swiss_energy.iloc[:, 1:] = swiss_energy.iloc[:, 1:].div(1000)

#Wir benennen noch die Spalte "Last" um, neuer Name ist GesamtlastSEC (für Gesamtlast Swiss Energy Charts)
swiss_energy.rename(columns={"Last" : "GesamtlastSEC"}, inplace=True)

#jetzt berechnen wir den rollierenden 7-Tages-Durchschnitt bei der Gesamtlast
swiss_energy["7-Roll-Avg-GesamtlastSEC"] = swiss_energy["GesamtlastSEC"].rolling(7, min_periods=7).mean()
swiss_energy['Tag'] = pd.to_datetime(swiss_energy['Tag'])

#jetzt fügen wir die beiden zusammen - the magic happens!
df = swiss_energy.merge(swissgrid, how='outer', left_on='Tag', right_on='Tag')

df.sort_values("Tag", inplace=True)

df.set_index("Tag", inplace=True)

#jetzt kreieren wir die geschätzten Daten für den aktuellen Zeitraum. 
#Das heisst: 7-Roll-Avg-Gesamtlast plus Mittelwert des Schätzfehlers (2,5), darum herum das 95%-Konfidenzintervall
#also plus/minus 2 mal Standardfehler (das ist die Näherung, korrekt wäre 1,96 mal Standardfehler)

#wir kreieren diese daten nur dort, wo die Gesamtlast in den Swissgrid-Daten "missing, NaN" ist

#Wir kreieren eine Hilfsvariable X, die dort 1 ist, wo Gesamtlast = NaN 
df["Hilfsvariable"] = df["Gesamtlast"].isna()

#jetzt können wir die geschätzte tagesaktuelle Last und den Unsicherheitsbereich kreieren
df.loc[df["Hilfsvariable"] == True, ["Aktuelle_Last_geschätzt"]] = df["7-Roll-Avg-GesamtlastSEC"] * 1.025
df.loc[df["Hilfsvariable"] == True, ["Unsicherheitsbereich_oben"]] = df["7-Roll-Avg-GesamtlastSEC"] * 1.115
df.loc[df["Hilfsvariable"] == True, ["Unsicherheitsbereich_unten"]] = df["7-Roll-Avg-GesamtlastSEC"] * 0.935

df.reset_index(inplace=True)

first_date = datetime.today().replace(day=1) - relativedelta(months=1)
second_date = datetime.today().replace(day=1) - relativedelta(months=1) + timedelta(days=1)

first_date = first_date.strftime('%Y-%m-%d')
second_date = second_date.strftime('%Y-%m-%d')

#Wir schmeissen noch die ersten zwei Tage bei den Schätzungen raus (optisches Problem...)

df.loc[df['Tag'] == first_date, 'Aktuelle_Last_geschätzt'] = np.nan
df.loc[df['Tag'] == first_date, 'Unsicherheitsbereich_oben'] = np.nan
df.loc[df['Tag'] == first_date, 'Unsicherheitsbereich_unten'] = np.nan
df.loc[df['Tag'] == second_date, 'Aktuelle_Last_geschätzt'] = np.nan
df.loc[df['Tag'] == second_date, 'Unsicherheitsbereich_oben'] = np.nan
df.loc[df['Tag'] == second_date, 'Unsicherheitsbereich_unten'] = np.nan

#Jetzt müssen wir das file noch so ummodeln, dass es eins zu eins in Q übernommen werden kann.
#Dazu müssen wir vor allem die Datumsstruktur ändern

df_2021 = df.loc[df["Tag"] < "2022-01-01"].copy()
df_2021['Datum'] = pd.to_datetime(df_2021['Tag']).dt.strftime('%m-%d')
df_2022 = df.loc[df["Tag"] > "2021-12-31"].copy()
df_2022['Datum'] = pd.to_datetime(df_2022['Tag']).dt.strftime('%m-%d')

df_2022 = df_2022[['Datum', "7-Roll-Avg-Gesamtlast", 'Aktuelle_Last_geschätzt',	'Unsicherheitsbereich_oben',	'Unsicherheitsbereich_unten']]
df_2022.rename(columns={"7-Roll-Avg-Gesamtlast" : "2022"}, inplace = True)
df_2021 = df_2021[['Datum', 'Tag', '7-Roll-Avg-Gesamtlast']].rename(columns={"7-Roll-Avg-Gesamtlast" : "2021"})

df_final = df_2021.merge(df_2022, how="left", left_on="Datum", right_on="Datum")

df_final.drop('Datum', axis = 1, inplace = True)

#df_final.set_index("Tag", inplace=True)

#Wir benennen die Spalten noch um
df_final.rename(columns={"Aktuelle_Last_geschätzt" : "Aktuelle Daten","Unsicherheitsbereich_oben" : " ", "Unsicherheitsbereich_unten" : "Unsicherheitsbereich"}, inplace=True)

this_month = df_final.loc[df_final['Aktuelle Daten'].notna(), 'Tag'].min().month_name(locale = 'de_DE.UTF-8')
this_year = df_final.loc[df_final['Aktuelle Daten'].notna(), 'Tag'].min().year + 1


notes = 'Die Daten ab ' + str(this_month) + ' ' + str(this_year) + ' beruhen auf tagesaktuellen Lastdaten, die um einen Korrekturfaktor bereinigt wurden. Diese Angaben sind mit einer Unsicherheit behaftet. Der Unsicherheitsbereich (95-Prozent-Konfidenzintervall) ist grafisch dargestellt. Lesebeispiel: Dass sicher Strom gespart wird, lässt sich erst sagen, wenn der Unsicherheitsbereich unterhalb der Vorjahreslinie liegt.'
update_chart(id='187d672099ad87048552f370cc5a0def', data=df_final, notes = notes)



