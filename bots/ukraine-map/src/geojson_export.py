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

    df = df[df['_visible'] == 1]

    data = {
        "type": "FeatureCollection",
        "features": []
    }

    df = df.fillna('')
    try:
        df['date_added'] = pd.to_datetime(df['date_added'])
    except:
        print("🤬 Das Feld 'date_added' konnte nicht in ein Datumsfeld konvertiert werden. Bitte prüfen, ob richtiges Datum")
        print("")
        pass

    # Calc State by date
    #hours_added = datetime.timedelta(hours = 24)
    #df['state'] = df['date_added'].apply(lambda x: 3 if datetime.datetime.now() - hours_added >= x  else 1)

    df['today'] = df['today'].fillna(0)
    df['state'] = df['today'].apply(lambda x: 1 if x == 1 else 3)

    df = df.sort_values('state', ascending=False)

    for i, row in df.iterrows():
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
                    "place": row['place'].strip(),
                    "title": row['title'].strip(),
                    "text": row['text'].strip(),
                    "url": row['url'].strip(),
                    "imgurl": row['imgurl'],
                    "imgsource": row['imgsource'],
                    "imgsourceurl": row['imgsourceurl'],
                    "videoid": row['videoid'],
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
