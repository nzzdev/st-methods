import pandas as pd
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
import helpers
import datetime, pytz

# Consts
url = 'https://www.bundeswahlleiter.de/bundestagswahlen/2021/ergebnisse/opendata/daten/gewaehlte_01.xml'
wahlkreise = Path('data/wahlkreise.csv')

# Load data
d = requests.get(url)
root = ET.fromstring(d.content)

# Load Wahlkreise
df_wahlkreise = pd.read_csv(wahlkreise, sep=';')

def translate_party(name):
    if name.lower() == 'Christlich Demokratische Union Deutschlands'.lower():
        return 'CDU'
    elif name.lower() == 'Sozialdemokratische Partei Deutschlands'.lower():
        return 'SPD'
    elif name.lower() == 'DIE LINKE'.lower():
        return 'Linke'
    elif name.lower() == 'BÜNDNIS 90/DIE GRÜNEN'.lower():
        return 'Grüne'
    elif name.lower() == 'Alternative für Deutschland'.lower():
        return 'AfD'
    elif name.lower() == 'Christlich-Soziale Union in Bayern e.V.'.lower():
        return 'CSU'
    else:
        print("Partei nicht erkannt: %s" % name)
        return name

for k in root.findall('Kandidat'):
    direkt = k.find('Wahldaten/Direkt')
    if direkt != None:
        # Wurde gewählt

        #prozent = round(float(k.find('Wahldaten').attrib.get('Prozent')), 2)
        gebiet = direkt.attrib.get('Gebietsnummer')
        gruppe = direkt.attrib.get('Gruppenname')
        person = k.find('Personendaten')

        # Concat Name because NameTitelVorname1 and NameTitelVorname2 are not congruent
        name = (
            person.attrib.get('Vorname') +
            (' ' + person.attrib.get('Namensbestandteile') if 'Namensbestandteile' in person.attrib else '') +
            ' ' + person.attrib.get('Name')
        )

        # Update dataframe
        df_wahlkreise.loc[df_wahlkreise['#'] == int(gebiet), 'Gewählt'] = name
        df_wahlkreise.loc[df_wahlkreise['#'] == int(gebiet), 'Partei'] = translate_party(gruppe)

    df_wahlkreise.set_index(df_wahlkreise['#'], inplace=True)

df_wahlkreise.head()

# Update chart
berlin = pytz.timezone('Europe/Berlin')
now = datetime.datetime.now().astimezone(berlin).strftime('%d. %-m., %H.%M Uhr')
helpers.update_chart('7e4ecfe5b05ba3a28acf390677a5e57f',
    data = df_wahlkreise,
    notes = "Stand: vorläufiges Endergebnis. Zuletzt aktualisiert: %s" % now)