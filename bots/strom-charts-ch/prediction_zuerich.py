
#  Achtung: Dieses Script nicht in der gleichen Action wie die anderen Stromcharts laufen lassen. Zwei Gründe:
#   * Braucht zwingend Python 3.8
#   * Überschreibt q.config.json
#
#  Q-Charts:
#   * Alle: https://q.st.nzz.ch/editor/chart/85c9e635bfeae3a127d9c9db9059cc83
#   * Privathaushalte: https://q.st.nzz.ch/editor/chart/85c9e635bfeae3a127d9c9db90640964
#   * Unternehmen: https://q.st.nzz.ch/editor/chart/8a89ec29d240ad709dc0c77b7f75e967
#
#  Um die Modelle zu trainieren: https://github.com/nzzdev/energyconsumption-zurich-model

import math
import pandas as pd
from pathlib import Path
from prophet.serialize import model_from_json
import requests
import datetime
import json
import os
import pytz

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# -------------- DAILY WEATHER
# Get Daily weather data
headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'sec-fetch-site': 'same-origin',
    'referer': 'https://www.meteoschweiz.admin.ch/home/messwerte.html?param=messwerte-lufttemperatur-10min&station=REH&chart=day'
}
data = requests.get('https://www.meteoschweiz.admin.ch/product/output/measured-values/chartData/temperature_day/chartData.temperature_day.REH.de.json', headers=headers)
data = data.json()

# Filter by Serie
data = list(filter(lambda x: x['id'] == 'temperature_day.REH.de.series.1', data['series']))

# Throw error, if data id changes
if len(data) != 1:
    raise Exception("Nach 'temperature_day.REH.de.series.1' (Tagesmittel) gesucht. Nichts (oder zu viel) gefunden :(")

df_temperature = pd.DataFrame(data[0]['data'], columns=['date', 'temperature'])

# Typecast
df_temperature['date'] = pd.to_datetime(df_temperature['date'], unit='ms')#.dt.date

# Set Index
df_temperature = df_temperature.set_index('date')

# For 2023: Add 2022 data
if df_temperature.index.min() > datetime.datetime(2022, 1, 1):
    df_old = pd.read_csv(Path('./data/REH.csv'))
    df_old['date'] = pd.to_datetime(df_old['date'])#.dt.date
    df_old = df_old[df_old.date < df_temperature.index.min()]
    df_old.set_index('date', inplace=True)
    df_temperature = pd.concat([df_old, df_temperature])
    df_temperature = df_temperature.sort_values('date')



# -------------- DAILY ENERGY
# Load Consumption
df_consumption = pd.read_csv('https://data.stadt-zuerich.ch/dataset/ewz_stromabgabe_netzebenen_stadt_zuerich/download/ewz_stromabgabe_netzebenen_stadt_zuerich.csv')

# Typecast
df_consumption['date'] = pd.to_datetime(df_consumption['Timestamp'], errors='raise', utc=True)
df_consumption['date'] = df_consumption['date'].dt.tz_convert('Europe/Berlin')

# Cleanup
df_consumption.rename(columns={'Value_NE5': 'consumption_ne5', 'Value_NE7': 'consumption_ne7'}, inplace=True)

# Group
df_consumption = df_consumption.groupby(df_consumption.date.dt.date).sum(numeric_only=True)

df_consumption.index = pd.to_datetime(df_consumption.index)

# Sum
df_consumption['consumption_total'] = df_consumption['consumption_ne5'] + df_consumption['consumption_ne7']


# -------------- COMBINE DATASETS AND ROLL
# Join
df_data = df_consumption.join(df_temperature, "date").reset_index(drop=False)

# Drop Na
df_data = df_data.dropna(subset=['consumption_total', 'temperature'], how='any')

# Calc Cos Sin
df_data['CosYearTemp'] = df_data.apply(lambda row: row['temperature'] * math.cos(row['date'].dayofyear * 2 * math.pi / 365), axis=1)
df_data['SinYearTemp'] = df_data.apply(lambda row: row['temperature'] * math.sin(row['date'].dayofyear * 2 * math.pi / 365), axis=1)

# Rolling
df_data = df_data.rolling(window=7, on='date').mean().dropna()#[:-7]

# Only 2022
df_data = df_data[df_data.date >= datetime.datetime(2022, 1, 1)]


# -------------- HELPERS
# Build nice Dataframe
def build_result_df(df, forecastTrain):
  df = pd.DataFrame(
    {
      "": forecastTrain["yhat_upper"].array,
      "Erwarteter Stromverbrauch": forecastTrain["yhat_lower"].array,
      "Effektiver Stromverbrauch": df["y"].array,
    },
    index=df["ds"]
  )

  # Round to GWh
  df = df.div(1000000).round(2)

  return df

def predict(modelpath, df_data, column):
    print("🔮 Predict %s, use model %s" % (column, modelpath.name))

    # Load model
    with open(modelpath, 'r') as fin:
        m = model_from_json(fin.read())

    df = df_data.copy()
    df.rename(columns={'date': 'ds', column: 'y'}, inplace=True)
    df['ds'] = df['ds'].dt.date

    # Predict
    forecastTrain = m.predict(df)     

    return build_result_df(df, forecastTrain)     

# -------------- PREDICT
# Für alle berechnen
df_predict_all = predict(Path('./zh-models/totalconsumption_rolling7day.json'), df_data, 'consumption_total')
df_predict_ne7 = predict(Path('./zh-models/ne7consumption_rolling7day.json'), df_data, 'consumption_ne7')
df_predict_ne5 = predict(Path('./zh-models/ne5consumption_rolling7day.json'), df_data, 'consumption_ne5')

# -------------- CREATE q.config.json

transform_df = lambda df: df.applymap(str).reset_index(drop=False).T.reset_index(drop=False).T.apply(list, axis=1).to_list()
notes = "Methode: Dieses Modell berechnet den zu erwartenden Stromverbrauch anhand des Wetters. Dazu wurde ein Algorithmus mit Stromdaten aus den Vorjahren (ab 2010) und den entsprechenden Tagestemperaturen trainiert. Die Berechnung erfolgte mit der Programmbibliothek «Prophet» von Facebook. Entwickelt wurde das Modell von EWZ.<br />Zuletzt aktualisiert: %s Uhr" % datetime.datetime.now().astimezone(pytz.timezone('Europe/Berlin')).strftime("%-d. %-m. %Y, %H.%M")

config = {
    "items": [
        {
            "environments": [
                {
                    "name": "production",
                    "id": "85c9e635bfeae3a127d9c9db9059cc83"
                }
            ],
            "item": {
                "notes": notes,
                "data": transform_df(df_predict_all)
            }
        },
        {
            "environments": [
                {
                    "name": "production",
                    "id": "85c9e635bfeae3a127d9c9db90640964"
                }
            ],
            "item": {
                "notes": notes,
                "data": transform_df(df_predict_ne7)
            }
        },
        {
            "environments": [
                {
                    "name": "production",
                    "id": "8a89ec29d240ad709dc0c77b7f75e967"
                }
            ],
            "item": {
                "notes": notes,
                "data": transform_df(df_predict_ne5)
            }
        },
    ]
}

# Store
json.dump(config, open(Path('./q.config.json'), 'w'), ensure_ascii=False, indent=1, default=str)