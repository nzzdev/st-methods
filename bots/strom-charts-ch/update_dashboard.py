from pathlib import Path
from helpers import *
from datetime import date

def trend2str(df):
    if df.iloc[-1]['value'] > df.iloc[-2]['value']:
        return 'steigend'
    elif df.iloc[-1]['value'] < df.iloc[-2]['value']:
        return 'fallend'
    else:
        return 'gleichbleibend'

#def run(futures, spotmarket, speicherseen):
def run(landesverbrauch, spotmarket, speicherseen):

    # ---------- Spotmarket
    # Trend: rollender 7-Tage-Schnitt

    spotmarket.rename(columns={'preisEUR': 'value'}, inplace=True)

    df_trend = spotmarket.copy()
    df_trend['roll'] = df_trend['value'].rolling(window=7).mean()

    json_spotmarket = {
            "indicatorTitle": "Spotmarkt",
            "date": spotmarket.iloc[-1]['date'],
            "indicatorSubtitle": "kurzfristige Lieferung pro MWh",
            "value": spotmarket.iloc[-1]['value'],
            "valueLabel": "%s Euro" % str(spotmarket.iloc[-1]['value']).replace('.', ','),
            "yAxisStart": 0,
            "yAxisLabels": [0, 200, 400, 600, 800 ],
            "yAxisLabelDecimals": 0,
            "color": "#374e8e",
            "trend": trend2str(df_trend),
            "chartType": "area",
            "chartData": spotmarket.to_dict('records')
    }


    # ---------- Futures
    #df_futures = futures[['Datum', 'Preis']]
    #df_futures.rename(columns={
     #   'Preis': 'value',
      #  'Datum': 'date'
       # }, inplace=True)
    #df_futures = df_futures.dropna(subset=['value'])
    #df_futures['date'] = df_futures['date'].dt.date

    #df_trend = df_futures.copy()
    #df_trend['roll'] = df_trend['value'].rolling(window=7).mean()

    #json_futures = {
     #       "indicatorTitle": "Terminmarkt",
      #      "date": df_futures.iloc[-1]['date'],
       #     "indicatorSubtitle": "Lieferung in 2024 pro MWh",
        #    "value": df_futures.iloc[-1]['value'],
         #   "valueLabel": "%s Euro" % str(df_futures.iloc[-1]['value']).replace('.', ','),
          #  "yAxisStart": 0,
           # "yAxisLabels": [0, 250, 500, 750, 1000, 1250 ],
            #"yAxisLabelDecimals": 0,
            #"color": "#374e8e",
            #"trend": trend2str(df_trend),
            #"chartType": "area",
            #"chartData": df_futures.to_dict('records')
    #}
    
    
    
    
    #----------- Landesverbrauch
    df = landesverbrauch[['date', 'Landesverbrauch', 'Geschätzter Verbrauch']]

    df.loc[df['Landesverbrauch'].isna(), 'Landesverbrauch'] = df['Geschätzter Verbrauch']

    df = df.dropna(subset = ['Landesverbrauch']).copy()
    df = df[['date', 'Landesverbrauch']]
    df.rename(columns={
        'Landesverbrauch': 'value'
        }, inplace=True)
    df = df.dropna(subset=['value'])
    df['date'] = df['date'].dt.date

    df_trend = df.copy()
    df_trend['roll'] = df_trend['value'].rolling(window=10).mean()

    json_futures = {
            "indicatorTitle": "Stromverbrauch",
            "date": df.iloc[-1]['date'],
            "indicatorSubtitle": "Geschätzter Landesverbrauch",
            "value": df.iloc[-1]['value'],
            "valueLabel": "%s Euro" % str(df.iloc[-1]['value']).replace('.', ','),
            "yAxisStart": 0,
            "yAxisLabels": [0, 100, 200, 300 ],
            "yAxisLabelDecimals": 0,
            "color": "#374e8e",
            "trend": trend2str(df),
            "chartType": "area",
            "chartData": df.to_dict('records')
    }
    

    # ---------- Speicherseen
    df_speicherseen = speicherseen[speicherseen.Datum >= '2022-01-01']
    df_speicherseen.rename(columns={'Datum': 'date', 'TotalCH_prct': 'value'}, inplace=True)
    df_speicherseen = df_speicherseen[['date', 'value']]
    df_speicherseen['date'] = df_speicherseen['date'].dt.date

    df_trend = df_speicherseen.copy()
    df_trend['roll'] = df_trend['value'].rolling(window=7).mean()

    json_speicherseen = {
            "indicatorTitle": "Stauseen",
            "date": df_speicherseen.iloc[-1]['date'],
            "indicatorSubtitle": "Füllgrad in Prozent",
            "value": df_speicherseen.iloc[-1]['value'],
            "valueLabel": "%s Prozent" % str(df_speicherseen.iloc[-1]['value']).replace('.', ','),
            "yAxisStart": 0,
            "yAxisLabels": [0, 25, 50, 75, 100],
            "yAxisLabelDecimals": 0,
            "color": "#374e8e",
            "trend": trend2str(df_trend),
            "chartType": "area",
            "chartData": df_speicherseen.to_dict('records')
    }

    # ---------- Create Q
    fn =  Path('./dashboard_ch.json')
    json.dump([json_spotmarket, json_futures, json_speicherseen], open(fn, 'w'), default=str)

    file = [{
        "loadSyncBeforeInit": True,
        "file": {
            "path": str(fn)
        }
    }]
    update_chart(id='6d24b255087653cf9743f6fd8308474b', files=file)    