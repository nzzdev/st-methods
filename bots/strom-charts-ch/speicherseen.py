import pandas as pd
import json
from urllib.request import urlopen



from helpers import *
pd.options.mode.chained_assignment = None

def get_speicherseen():
    # read data
    url  = 'https://www.energiedashboard.admin.ch/api/v2/fuellungsgrad-speicherseen'
    
    response = urlopen(url)

    data_json = json.loads(response.read())
    
    totalCH = data_json['totalCH']
    
    df = pd.DataFrame(totalCH['entries'])
    
    df_wf = df[['date', 'fiveYearMin', 'fiveYearMax', 'fiveYearMittelwert', 'speicherstandProzent']]

    df_wf = df_wf.dropna()

    df_wf['date'] = pd.to_datetime(df_wf['date'])

    df_wf.rename(columns = {'fiveYearMin': '', 
                           'fiveYearMax': 'Minimum/Maximum¹',
                           'fiveYearMittelwert': '5-Jahres-Mittelwert',
                           'landesverbrauch': 'Füllstand'
                           }, inplace = True)

    
    #columns = [col[:-19] for col in df.columns.to_list()[1:]]
    #columns.insert(0, 'Datum')
    #df.columns = columns
    #df['Datum'] = pd.to_datetime(df['Datum'])

    # calculate prct
    #df['TotalCH_prct'] = round(df['TotalCH']/df['TotalCH_max']*100, 1)

    # waterfall chart
    #df_wf = df[['Datum', 'TotalCH_prct']]

    #df_wf['Jahr'] =  df_wf['Datum'].dt.year
    #df_wf['Woche'] = pd.to_datetime(df_wf.Datum).dt.strftime('-W%W')
    #df_wf['Jahr_Woche'] = '2000'+df_wf['Woche'].astype(str)

    

    return df_wf

    