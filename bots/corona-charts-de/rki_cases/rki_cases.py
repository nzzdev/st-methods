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

        # subprocess.call('npm i dataunwrapper', shell=True)
        dataunwrapper = subprocess.Popen('node dataunwrapper.js WHW9o',
                                         shell=True, stdout=subprocess.PIPE)
        output = dataunwrapper.stdout.read()

        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'nodeoutput.csv'), 'wb') as f:
            f.write(output)

        # read csv and convert to datetime, add one day
        df = pd.read_csv('./data/nodeoutput.csv',
                         encoding='utf-8', index_col=0)
        df.index = pd.to_datetime(df.index)
        df.index = df.index.date + pd.Timedelta(days=1)

        # drop unused columns
        df = df.iloc[:, 2].reset_index()

        # get current date and prepare for Q
        timestamp_str = df.iloc[-1, 0].strftime('%-d. %-m. %Y')
        df = df.set_index(df.columns[0])
        df = df.rename(columns={df.columns[0]: '7-Tage-Schnitt'})
        df.index.rename('', inplace=True)

        notes_chart = '<br>Stand: ' + timestamp_str

        # run function
        update_chart(id='42c2893ef336754392b6d64297e54d06',
                     data=df, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
