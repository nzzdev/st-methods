# coding=utf-8 
# Dieses File ist Entrypoint für folgende Aktualisierungen:
#   Charts im Artikel
#   Dashboard


import os

import strommarktch
import speicherseen
import bfe
import update_article
import update_dashboard


"""
   Preparation
"""

# Set Working Directory
os.chdir(os.path.dirname(__file__))


""" 
  Get all data. Convert it later for article or dashboard
"""

df_futures = strommarktch.get_futures()
df_spotmarket = strommarktch.get_spotmarket()
df_atomstrom_fr = strommarktch.get_atomstrom_frankreich()
df_speicherseen = speicherseen.get_speicherseen()
df_bfe = bfe.get_bfe()



"""
  Update q.config
"""

update_article.run(df_futures, df_spotmarket, df_atomstrom_fr, df_speicherseen, df_bfe)
update_dashboard.run(df_futures, df_spotmarket, df_speicherseen)
