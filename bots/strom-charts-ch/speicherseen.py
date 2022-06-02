
import requests
from datetime import datetime
import os
import pandas as pd
pd.options.mode.chained_assignment = None

from helpers import *

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# set date
q_date = 'Stand: '+ datetime.now().strftime("%-d. %-m. %Y")

# read data
url  = 'https://www.uvek-gis.admin.ch/BFE/ogd/17/ogd17_fuellungsgrad_speicherseen.csv'
r = requests.get(url)
open('temp.csv', 'wb').write(r.content)
df = pd.read_csv('temp.csv')

columns = [col[:-19] for col in df.columns.to_list()[1:]]
columns.insert(0, 'Datum')
df.columns = columns
df['Datum'] = pd.to_datetime(df['Datum'])

# calculate prct
df['TotalCH_prct']     = round(df['TotalCH']/df['TotalCH_max']*100, 1)

# waterfall chart
df_wf = df[['Datum', 'TotalCH_prct']]

df_wf['Jahr'] =  df_wf['Datum'].dt.year
df_wf['Woche'] = pd.to_datetime(df_wf.Datum).dt.strftime('-W%W')
df_wf['Jahr_Woche'] = '2000'+df_wf['Woche'].astype(str) 

df_wf_wide = df_wf.pivot(index=['Jahr_Woche'], columns='Jahr', values='TotalCH_prct')

waterfall_q_data = df_wf_wide.iloc[:,-3:]
waterfall_q_id = '69bd37806691fc0c2e6786eb38efea63'

#update_chart(id=waterfall_q_id, 
#            data=df_wf_wide.iloc[:,-3:],
#            notes = q_date)

waterfall_q_data.to_csv('test_data.csv')