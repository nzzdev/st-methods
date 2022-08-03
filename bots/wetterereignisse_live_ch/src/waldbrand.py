import json
from pathlib import Path
from helpers import *
from datetime import datetime
import os
import pytz
import gefahrenkarteutils

# Set Working Directory
os.chdir(os.path.dirname(__file__))

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

# Get Gefahrenkarte
geojson = gefahrenkarteutils.run('https://www.waldbrandgefahr.ch/de/aktuelle-gefahrenlage', colors, legende)

# Background laden
background = json.load(open(Path('../data/background_ch.geojson'), 'r'))

# Standard-Städtelabels laden
city_features = gefahrenkarteutils.get_citylabels()

# Featureliste erstellen
features = [
    geojson,
    background,
] + city_features

update_chart(
    id = 'd0be298e35165ab925d72923355c5379',
    geojsonList = features,
    # notes = "Stand: %s" %  datetime.strptime(geojson['timeStamp'], "%Y-%m-%dT%H:%M:%SZ").strftime('%-d. %-m. %Y, %H.%M Uhr')
    notes = "Stand: %s" %  datetime.now(pytz.timezone('Europe/Berlin')).strftime('%-d. %-m., %H.%M Uhr')
)