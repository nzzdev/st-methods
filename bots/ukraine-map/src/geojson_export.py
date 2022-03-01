# %% [markdown]
# # Geojson export

# %%
import pandas as pd
import json
import datetime

# %%
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vR28WE_2xWMoUvFIItA_rQDu0-nBnmIByy3T3H1bcZCeni1FWAxVLUFxml6sBhYCTWxsVoLNSaOTrY8/pub?gid=0&single=true&output=csv&cache=%s' % datetime.datetime.now().timestamp()

def create_geojson(export_path):

    df = pd.read_csv(url)

    data = {
        "type": "FeatureCollection",
        "features": []
    }

    df = df.fillna('')
    try:
        df['date_added'] = pd.to_datetime(df['date_added'], format='%d.%m.%Y %H:%M:00')
    except:
        print("🤬 Das Feld 'date_added' konnte nicht in ein Datumsfeld konvertiert werden. Bitte prüfen, ob richtiges Datum")
        print("")
        pass

    # Calc State
    hours_added = datetime.timedelta(hours = 24)
    df['state'] = df['date_added'].apply(lambda x: 3 if datetime.datetime.now() - hours_added >= x  else 1)

    df = df.sort_values('state', ascending=False)

    for i, row in df[df['_visible'] == 1].iterrows():
        try:
            coords = row['latlon'].replace(' ', '').split(',')

            if len(coords) < 2:
                raise ValueError('Koordinaten falsch: %s' % list(row))

            data['features'].append({
                "type": "Feature",
                "properties": {
                    "type": row['type'],
                    "state": int(row['state']),
                    "date": row['date_text'],
                    "place": row['place'],
                    "title": row['title'],
                    "text": row['text'],
                    "url": row['url'],
                    "imgurl": row['imgurl'],
                    "imgsource": row['imgsource'],
                    "imgsourceurl": row['imgsourceurl'],
                    "source": row['source'],
                    "sourceurl": row['sourceurl'],
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(coords[1]), float(coords[0])]
                }
            })
        except Exception as e:
            print("🥵 Ups, da ging was schief. In Zeile %s im Sheet:" % (i + 1))
            print(list(row))
            print("ℹ️ Fehlermeldung: %s" % e)
            pass
            break


    with open(export_path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False)
