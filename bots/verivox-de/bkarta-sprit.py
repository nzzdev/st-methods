import os
import pandas as pd
import subprocess
from datetime import datetime
from dateutil import tz

if __name__ == '__main__':
    try:
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # call Node.js script and save output as csv
        # Diesel
        dataunwrapper = subprocess.Popen(
            ['node', 'dataunwrapper.js', 'k0KSK'], stdout=subprocess.PIPE)
        output = dataunwrapper.stdout.read()
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'node_diesel.csv'), 'wb') as f:
            f.write(output)

        # Super E5
        dataunwrapper = subprocess.Popen(
            ['node', 'dataunwrapper.js', 'c5jql'], stdout=subprocess.PIPE)
        output = dataunwrapper.stdout.read()
        with open(os.path.join('data', 'node_super.csv'), 'wb') as f:
            f.write(output)

        # read csv
        df_diesel = pd.read_csv('./data/node_diesel.csv', index_col=1)
        df_super = pd.read_csv('./data/node_super.csv', index_col=1)

        # drop unused columns and duplicate entries for current day
        df_diesel = df_diesel.drop(
            df_diesel.columns[[0, 1, 2, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19]], axis=1)
        df_diesel = df_diesel[~df_diesel.index.duplicated(keep='last')]
        df_super = df_super.drop(
            df_super.columns[[0, 1, 2, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19]], axis=1)
        df_super = df_super[~df_super.index.duplicated(keep='last')]

        # get date for chart notes
        df_diesel.index = pd.to_datetime(df_diesel.index)
        timestamp_str = df_diesel.tail(1).index.item().strftime('%-d. %-m. %Y')

        # get current hour
        """
        df_diesel.index = pd.to_datetime(df_diesel.index)
        timestamp_str = df_diesel.tail(1).index.item().strftime('%-d. %-m. %Y')
        tcode = tz.gettz('Europe/Berlin')
        tcode_h = datetime.now(tcode)
        tcode_h = tcode_h.strftime("%H. %M")
        """

        notes_chart = f'¹ Durchschnitt oberstes und unterstes Dezil von rund 15 000 Tankstellen.<br>Stand: {timestamp_str}'

        # rename column headers
        mapping = {df_diesel.columns[0]: '', df_diesel.columns[1]: 'Höchster/niedrigster Preis¹', df_diesel.columns[2]: 'Bundesschnitt'}
        df_diesel = df_diesel.rename(columns=mapping)
        mapping = {df_super.columns[0]: '', df_super.columns[1]: 'Höchster/niedrigster Preis¹', df_super.columns[2]: 'Bundesschnitt'}
        df_super = df_super.rename(columns=mapping)

        # get current price for chart title
        price_d = df_diesel['Bundesschnitt'].iloc[-1].round(
            2).astype(str).replace('.', ',')
        price_s = df_super['Bundesschnitt'].iloc[-1].round(
            2).astype(str).replace('.', ',')
        title_chart_d = f'Diesel kostet im Schnitt {price_d} Euro je Liter'
        title_chart_s = f'Benzin kostet im Schnitt {price_s} Euro je Liter'

        # run Q function
        update_chart(id='458d885de84d6eb558874e221f294a93',
                     data=df_diesel, title=title_chart_d, notes=notes_chart)
        update_chart(id='458d885de84d6eb558874e221f2c09c0',
                     data=df_super, title=title_chart_s, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
