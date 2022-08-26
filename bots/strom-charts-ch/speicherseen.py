import pandas as pd
from datetime import datetime
import os

from helpers import *
pd.options.mode.chained_assignment = None

def get_speicherseen():
    # read data
    url  = 'https://www.uvek-gis.admin.ch/BFE/ogd/17/ogd17_fuellungsgrad_speicherseen.csv'
    df = pd.read_csv(url)

    columns = [col[:-19] for col in df.columns.to_list()[1:]]
    columns.insert(0, 'Datum')
    df.columns = columns
    df['Datum'] = pd.to_datetime(df['Datum'])

    # calculate prct
    df['TotalCH_prct'] = round(df['TotalCH']/df['TotalCH_max']*100, 1)

    # waterfall chart
    df_wf = df[['Datum', 'TotalCH_prct']]

    df_wf['Jahr'] =  df_wf['Datum'].dt.year
    df_wf['Woche'] = pd.to_datetime(df_wf.Datum).dt.strftime('-W%W')
    df_wf['Jahr_Woche'] = '2000'+df_wf['Woche'].astype(str)

    return df_wf

    #waterfall_q_data.to_csv('test_data.csv')