from shapely.ops import unary_union
from shapely.geometry import shape, mapping
import json
from pathlib import Path

def union_geojson(features):
    polygons = list(map(lambda x: shape(x['geometry']), features))
    return unary_union(polygons)

def run(exportpath):

    # Read JSON
    dates = list(Path('./export/areas_history/').glob("*.geojson"))
    dates.sort()

    data_old = json.load(open(dates[-2], 'r'))
    data_new = json.load(open(dates[-1], 'r'))
    print(dates[-2], dates[-1])

    # Union Polygons
    poly_old = union_geojson(data_old['features'])
    poly_new = union_geojson(data_new['features'])

    poly_difference = poly_new.difference(poly_old)

    # Create GeoJSON
    geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "type": "changed",
                },
                "geometry": mapping(poly_difference)
            },
            {
                "type": "Feature",
                "properties": {
                    "type": "old",
                },
                "geometry": mapping(poly_old)
            }]
    }

    json.dump(geojson, open(exportpath, 'w'))    