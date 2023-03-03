#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 15 10:28:51 2022

Updates:
 - Neue API: Die alte liefert nur Werte bis 2022, aber mit falschen Datum. Wird vielleicht geflickt... @simonhuwiler

@author: florianseliger


"""

import pandas as pd
import json
from urllib.request import urlopen
from datetime import timedelta, date

from helpers import *

def get_bfe():
    url = 'https://www.energiedashboard.admin.ch/api/v2/strom-verbrauch/landesverbrauch-mit-prognose'

    response = urlopen(url)

    data_json = json.loads(response.read())

    landesverbrauch = pd.DataFrame(data_json['entries'])

    landesverbrauch = landesverbrauch[['date', 'fiveYearMin', 'fiveYearMax', 'fiveYearMittelwert', 'landesverbrauch', 'landesverbrauchGeschaetzt', 'landesverbrauchPrognose']]

    landesverbrauch['date'] = pd.to_datetime(landesverbrauch['date'])

    landesverbrauch = landesverbrauch.loc[landesverbrauch['date'] >= pd.to_datetime(date.today() - timedelta(days=125))]

    landesverbrauch.rename(columns = {'fiveYearMin': '', 
                                  'fiveYearMax': 'Minimum/Maximum¹',
                                  'fiveYearMittelwert': '5-Jahres-Mittelwert',
                                  'landesverbrauch': 'Landesverbrauch',
                                  'landesverbrauchGeschaetzt': 'Geschätzter Verbrauch',
                                  'landesverbrauchPrognose': 'Prognose'
                                  }, inplace = True)

    return landesverbrauch

    einsparung = pd.read_json('https://energiedashboard.admin.ch/api/v2/strom-sparziel/aktuelle-einsparung')
    einsparung = einsparung.dropna()
    einsparung = einsparung.rename(columns = {'differenzMittelwertProzent': 'Mehr-/Minderverbrauch'})
    einsparung['Sparziel'] = -10
    einsparung = einsparung[['date', 'Mehr-/Minderverbrauch', 'Sparziel']]
    
    return einsparung