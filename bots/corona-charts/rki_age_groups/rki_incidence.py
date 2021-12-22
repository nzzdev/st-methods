import os
import pandas as pd
import sys
from datetime import datetime
from urllib.request import Request, urlopen

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # check weekday
        d = datetime.today()
        dcheck = d.isoweekday() == 5

        # only download data on Fridays
        if dcheck == 'True':
            url = Request('https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Altersverteilung.xlsx?__blob=publicationFile',
                          headers={'User-Agent': 'Mozilla/5.0'})
            xl = urlopen(url, timeout=10).read()

            # read data and convert to csv (requires openpyxl)
            df = pd.read_excel(
                xl, sheet_name=0, index_col=0, engine='openpyxl')
            df.to_csv('./Altersverteilung.csv', encoding='utf-8')

            # get current week number for chart notes
            timestamp = (d.isocalendar().week) - 1

        # read csv and transpose data
        df = pd.read_csv('./Altersverteilung.csv', encoding='utf-8')
        df = df.set_index('Altersgruppe').T

        # calculate correct sum of cases with known age groups in "Gesamt"
        df['Gesamt'].values[:] = 0
        sum = df.columns[: df.shape[0]-1]
        df['Gesamt'] = df[sum].sum(axis=1)

        # calculate percentages by column index, starting from "0-4"
        df.iloc[:, -1] = (df.iloc[:, -1] / df.iloc[:, 0]) * 100
        df = df.rename(columns={df.columns[-1]: '0-4'})
        df['5-14'] = df.iloc[:, -2] + df.iloc[:, -3]
        df.iloc[:, -1] = (df.iloc[:, -1] / df.iloc[:, 0]) * 100
        df['15-34'] = df.iloc[:, -5] + df.iloc[:, -6] + \
            df.iloc[:, -7] + df.iloc[:, -8]
        df.iloc[:, -1] = (df.iloc[:, -1] / df.iloc[:, 0]) * 100
        df['35-59'] = df.iloc[:, -10] + df.iloc[:, -11] + \
            df.iloc[:, -12] + df.iloc[:, -13] + df.iloc[:, -14]
        df.iloc[:, -1] = (df.iloc[:, -1] / df.iloc[:, 0]) * 100
        df['60-79'] = df.iloc[:, -16] + df.iloc[:, -17] + \
            df.iloc[:, -18] + df.iloc[:, -19]
        df.iloc[:, -1] = (df.iloc[:, -1] / df.iloc[:, 0]) * 100
        df['80+'] = df.iloc[:, -21] + df.iloc[:, -22] + df.iloc[:, -23]
        df.iloc[:, -1] = (df.iloc[:, -1] / df.iloc[:, 0]) * 100
        df = df.drop(columns=df.columns[:19], axis=1)

        # convert weeknumbers to Q date format
        df.index = df.index.str.replace('_', '-W')

        # show date in chart notes
        notes_chart = 'Stand: Kalenderwoche ' + str(timestamp)

        # run function
        update_chart(id='34937bf850cf702a02c3648cdf8c02b9',
                     data=df, notes=notes_chart)

    except:
        raise
