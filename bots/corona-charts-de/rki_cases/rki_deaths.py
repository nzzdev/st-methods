import os
import pandas as pd
import sys
import subprocess

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # call Node.js script and save output as csv
        # subprocess.call(['npm' 'i' 'dataunwrapper'])
        dataunwrapper = subprocess.Popen(
            ['node', 'dataunwrapper.js', 'V721h'], stdout=subprocess.PIPE)
        output = dataunwrapper.stdout.read()

        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'node_tote.csv'), 'wb') as f:
            f.write(output)

        # read csv and convert to datetime, add one day
        df = pd.read_csv('./data/node_tote.csv',
                         encoding='utf-8', index_col=0)
        df.index = pd.to_datetime(df.index)
        df.index = df.index.date + pd.Timedelta(days=1)
        df.index = pd.to_datetime(df.index)
        timestamp_str = df.tail(1).index.item().strftime('%-d. %-m. %Y')
        df.index = df.index.strftime('%Y-%m-%d')

        # drop unused columns
        df = df.iloc[:, 1].reset_index()

        # prepare for Q
        df = df.set_index(df.columns[0])
        df = df.rename(
            columns={df.columns[0]: 'Tote'}).astype(int)
        df.index.rename('Datum', inplace=True)
        notes_chart = 'Stand: ' + timestamp_str
        df.to_csv('./data/tote7d.csv', encoding='utf-8', index=True)

        # run function
        update_chart(id='2a1327d75c83a9c4ea49f935dd597e1a',
                     data=df, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
