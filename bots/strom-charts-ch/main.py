# Dieses File ist Entrypoint für folgende Aktualisierungen:
#   Charts im Artikel
#   Dashboard
#

import pandas as pd
import os
from datetime import datetime as dt

from helpers import *
import strommarktch
import speicherseen

"""
   Preparation
"""

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# set date
q_date = 'Stand: '+ dt.now().strftime("%-d. %-m. %Y")

""" 
  Get all data. Convert it later for article or dashboard
"""

df_futures = strommarktch.get_futures()
df_spotmarket = strommarktch.get_spotmarket()
df_atomstrom_fr = strommarktch.get_atomstrom_frankreich()
df_speicherseen = speicherseen.get_speicherseen()



"""
  Update q.config for ARTICLE
"""
# Futures
update_chart(id="de091de1c8d4f5042323dbd9e08c9548", 
            data=df_futures,
            notes = q_date)

# Spotmarket
update_chart(id="046c2f2cc67578f60cc5c36ce55d27ae", 
            data=df_spotmarket,
            notes = q_date)

# Atomkraft Fr
update_chart(id="4d6b0595264016839099c06df6bdd6af", 
            data=df_atomstrom_fr,
            notes = q_date)

# Speicherseen
update_chart(id='69bd37806691fc0c2e6786eb38efea63', 
            data=df_speicherseen,
            notes = q_date)



"""
  Update q.config for DASHBOARD
"""