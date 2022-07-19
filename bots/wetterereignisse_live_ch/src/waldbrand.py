import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import pyproj
import numbers
from pathlib import Path
from helpers import *
from datetime import datetime
import os

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# 1. Get Website and collect URL
soup = BeautifulSoup(requests.get('https://www.waldbrandgefahr.ch/de/aktuelle-gefahrenlage').text, 'html.parser')


div = soup.select_one('#fire_map_detail')
url = json.loads(div.attrs['data-react-props'])['geojson']
url = 'https://www.waldbrandgefahr.ch' + url

r = requests.get(url)
geojson = r.json()

# Sort (damit Legende richtige Reihenfolge hat)
geojson['features'] = sorted(geojson['features'], key=lambda x: x['properties']['level'])

# Definition von Farben und Labels
colors = {
    1: '#cfdd9d',
    2: '#e0d4b1',
    3: '#d47340',
    4: '#ce4731',
    5: '#93144b'
}

legende = {
    1: 'Keine oder geringe Gefahr',
    2: 'Mässige Gefahr',
    3: 'Erhebliche Gefahr',
    4: 'Grosse Gefahr',
    5: 'Sehr grosse Gefahr'
}

# Städte definieren
labels = [
    {
        "coordinates": [8.540448763866461, 47.377069663836046],
        "type": "point",
        "label": "Zürich",
        "labelPosition": "left"
    },
    {
        "coordinates": [7.448853873224696, 46.95054213418904],
        "type": "point",
        "label": "Bern",
        "labelPosition": "left"
    },
    {
        "coordinates": [6.138221654376033, 46.2064440296011],
        "type": "point",
        "label": "Genf",
        "labelPosition": "right"
    },
    {
        "coordinates": [8.950669089563268, 46.01118348612857],
        "type": "point",
        "label": "Lugano",
        "labelPosition": "left"
    },
    {
        "coordinates": [9.53560206455592, 46.8509515603594],
        "type": "point",
        "label": "Chur",
        "labelPosition": "right"
    },
    {
        "coordinates": [9.375378684759603, 47.42547357986716],
        "type": "point",
        "label": "St. Gallen",
        "labelPosition": "right"
    },
    {
        "coordinates": [7.595953393405145, 47.561448902150964],
        "type": "point",
        "label": "Basel",
        "labelPosition": "left"
    },
    {
        "coordinates": [7.364787560405546, 46.23149747652774],
        "type": "point",
        "label": "Sitten",
        "labelPosition": "right"
    },
    {
        "coordinates": [8.308714014295267, 47.05150580099424],
        "type": "point",
        "label": "Luzern",
        "labelPosition": "bottom"
    },
]

# CRS konvertieren (dauert zu lange, will aber nicht GeoPandas nutzen...)

def project_coords(coords, from_proj, to_proj):
    if len(coords) < 1:
        return []

    if isinstance(coords[0], numbers.Number):
        from_x, from_y = coords
        to_x, to_y = pyproj.transform(from_proj, to_proj, from_x, from_y)
        return [to_x, to_y]

    new_coords = []
    for coord in coords:
        new_coords.append(project_coords(coord, from_proj, to_proj))
    return new_coords


def project_feature(feature, from_proj, to_proj):
    if not 'geometry' in feature or not 'coordinates' in feature['geometry']:
        print('Failed project feature', feature)
        return None

    new_coordinates = project_coords(feature['geometry']['coordinates'], from_proj, to_proj)
    feature['geometry']['coordinates'] = new_coordinates
    return feature

for feature in geojson['features']:
    del feature['bbox']
    del feature['id']
    feature['properties'] = {
        'fill': colors[feature['properties']['level']],
        'label': legende[feature['properties']['level']],
        'fill-opacity': 0.8,
        'stroke-opacity': 0
    }

mercator = pyproj.Proj(init='epsg:4326')
swissgrid = pyproj.Proj(init='epsg:2056')

projected_features = []
for feature in geojson['features']:
    projected_features.append(project_feature(feature, swissgrid, mercator))
geojson['features'] = projected_features

# Städte umwandeln
city_features = list(map(lambda x: {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": x['coordinates']
            },
            "properties": {
                "type": x["type"],
                "label": x["label"],
                "labelPosition": x["labelPosition"],
            }
          }, labels))

# Background laden
background = json.load(open(Path('../data/background_ch.geojson'), 'r'))

# Featureliste erstellen
features = [
    geojson,
    background,
] + city_features

update_chart(
    id = 'd0be298e35165ab925d72923355c5379',
    geojsonList = features,
    notes = "Stand: %s" %  datetime.strptime(geojson['timeStamp'], "%Y-%m-%dT%H:%M:%SZ").strftime('%-d. %-m. %Y, %H.%M Uhr')
)


