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

        #subprocess.call('npm i dataunwrapper', shell=True)
        dataunwrapper = subprocess.Popen('node dataunwrapper.js WHW9o',
                                         shell=True, stdout=subprocess.PIPE)
        output = dataunwrapper.stdout.read()

        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'nodeoutput.csv'), 'wb') as f:
            f.write(output)

        df = pd.read_csv('./data/nodeoutput.csv',
                         encoding='utf-8', index_col=0)
        # run function
        update_chart(id='42c2893ef336754392b6d64297e54d06', data=df)

    except:
        raise
    finally:
        f.close()
