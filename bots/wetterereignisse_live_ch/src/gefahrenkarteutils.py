from bs4 import BeautifulSoup
import pyproj
import json
import requests
from shapely.geometry import shape
from shapely.ops import transform

def run(url, colors, legende):

    # 1. Get Website and collect URL
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')


    div = soup.select_one('#fire_map_detail')
    url = json.loads(div.attrs['data-react-props'])['geojson']
    url = 'https://www.waldbrandgefahr.ch' + url

    r = requests.get(url)
    geojson = r.json()

    # Sort (damit Legende richtige Reihenfolge hat)
    geojson['features'] = sorted(geojson['features'], key=lambda x: x['properties']['level'])


    # CRS konvertieren (dauert zu lange, will aber nicht GeoPandas nutzen...)
    for feature in geojson['features']:
        del feature['bbox']
        del feature['id']
        feature['properties'] = {
            'fill': colors[feature['properties']['level']],
            'label': legende[feature['properties']['level']],
            'fill-opacity': 0.8,
            'stroke-opacity': 0
        }

    mercator = pyproj.CRS('EPSG:4326')
    swissgrid = pyproj.CRS('EPSG:2056')
    project = pyproj.Transformer.from_crs(swissgrid, mercator, always_xy=True).transform

    for feature in geojson['features']:
        shp = shape(feature['geometry'])
        feature['geometry'] = transform(project, shp).__geo_interface__

    return geojson

def get_citylabels():

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

    return city_features