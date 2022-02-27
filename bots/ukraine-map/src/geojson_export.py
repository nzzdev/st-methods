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

    df['grey'] = df['grey'].str.replace(' ', '0')
    df['grey'] = df['grey'].fillna(0)
    df = df.fillna('')

    for i, row in df[df['_visible'] == 1].iterrows():
        coords = row['latlon'].replace(' ', '').split(',')

        if len(coords) < 2:
            raise ValueError('Koordinaten falsch: %s' % list(row))

        data['features'].append({
            "type": "Feature",
            "properties": {
                "date": row['date'],
                "place": row['place'],
                "title": row['title'],
                "text": row['text'],
                "url": row['url'],
                "imgurl": row['imgurl'],
                "type": row['type'],
                "source": row['source'],
                "sourceurl": row['sourceurl'],
                "grey": int(row['grey']),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(coords[1]), float(coords[0])]
            }
        })

    with open(export_path, 'w', encoding='UTF-8') as f:
        json.dump(data, f, ensure_ascii=False)
