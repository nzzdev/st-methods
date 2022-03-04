import os
import pandas as pd
import sys
import subprocess
from datetime import datetime

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # subprocess.call('npm i dataunwrapper', shell=True)
        dataunwrapper = subprocess.Popen('node dataunwrapper.js z9o4e',
                                         shell=True, stdout=subprocess.PIPE)
        output = dataunwrapper.stdout.read()

        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'nodeoutput.csv'), 'wb') as f:
            f.write(output)

        # read csv and convert to datetime, add one day
        df = pd.read_csv('./data/nodeoutput.csv',
                         encoding='utf-8', index_col=0)

        # drop unused columns
        df = df.iloc[:, 2].reset_index()

        # get current date
        timestamp_str = df.iloc[-1, 0]
        timestamp_dt = datetime.strptime(timestamp_str, '%Y-%m-%d')
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')
        notes_chart = 'Stand: ' + timestamp_str

        # prepare dataframe for Q
        df = df.set_index(df.columns[0])
        df = df.rename(
            columns={df.columns[0]: '7-Tage-Schnitt'}).round().astype(int)
        df.index.rename('Datum', inplace=True)

        # run function
        update_chart(id='2a1327d75c83a9c4ea49f935dd687c24',
                     data=df, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
