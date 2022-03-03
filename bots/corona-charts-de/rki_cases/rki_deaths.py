import os
import pandas as pd
import sys
from urllib.request import Request, urlopen

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # download excel file
        url = Request('https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Fallzahlen_Gesamtuebersicht.xlsx?__blob=publicationFile',
                      headers={'User-Agent': 'Mozilla/5.0'})
        xl = urlopen(url, timeout=10).read()

        # read data and convert to csv (requires openpyxl)
        df = pd.read_excel(
            xl, sheet_name=0, index_col=0, skiprows=2, engine='openpyxl').dropna(how='all', axis=1)
        df.to_csv('./fallzahlen.csv', encoding='utf-8')

        # read csv and convert to datetime
        df = pd.read_csv('./fallzahlen.csv', encoding='utf-8', index_col=0)
        df.index = pd.to_datetime(df.index)

        # 7-day moving average of new deaths, drop other columns
        df = df.iloc[:, 3].rolling(
            window=7).mean().round().dropna().astype(int).reset_index()

        # get current date and prepare for Q
        timestamp_str = df.iloc[-1, 0].strftime('%-d. %-m. %Y')
        df = df.set_index(df.columns[0])
        df = df.rename(columns={df.columns[0]: '7-Tage-Schnitt'})
        df.index.rename('', inplace=True)

        notes_chart = 'Stand: ' + timestamp_str

        # run function
        update_chart(id='2a1327d75c83a9c4ea49f935dd597e1a',
                     data=df, notes=notes_chart)

    except:
        raise
