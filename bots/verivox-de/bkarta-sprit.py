import os
import pandas as pd
import subprocess

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

        # read csv and convert to datetime, add one day
        df_diesel = pd.read_csv('./data/node_diesel.csv',
                                encoding='utf-8', usecols=['day', 'tages_mittel_min_10', 'tages_mittel_max_10', 'tages_mittel'], index_col=0)
        df_super = pd.read_csv('./data/node_super.csv',
                               encoding='utf-8', usecols=['day', 'tages_mittel_min_10', 'tages_mittel_max_10', 'tages_mittel'], index_col=0)

        # get date for chart notes
        df_diesel.index = pd.to_datetime(df_diesel.index)
        timestamp_str = df_diesel.tail(1).index.item().strftime('%-d. %-m. %Y')
        df_diesel.index = df_diesel.index.strftime('%Y-%m-%d')
        notes_chart = '¹ Durchschnitt oberstes und unterstes Dezentil von rund 15 000 Tankstellen.<br>Stand: ' + timestamp_str

        # rename column headers
        df_diesel = df_diesel.rename(
            {'tages_mittel_min_10': '', 'tages_mittel_max_10': 'Höchster/niedrigster Preis¹', 'tages_mittel': 'Bundesschnitt'}, axis=1)
        df_super = df_super.rename(
            {'tages_mittel_min_10': '', 'tages_mittel_max_10': 'Höchster/niedrigster Preis¹', 'tages_mittel': 'Bundesschnitt'}, axis=1)

        # get current price for chart title
        price_d = df_diesel['Bundesschnitt'].iloc[-1].round(
            2).astype(str).replace('.', ',')
        price_s = df_super['Bundesschnitt'].iloc[-1].round(
            2).astype(str).replace('.', ',')
        title_chart_d = f'Diesel kostet derzeit im Schnitt {price_d} Euro je Liter'
        title_chart_s = f'Benzin kostet derzeit im Schnitt {price_s} Euro je Liter'

        print(title_chart_s)

        # run Q function
        update_chart(id='458d885de84d6eb558874e221f294a93',
                     data=df_diesel, title=title_chart_d, notes=notes_chart)
        update_chart(id='458d885de84d6eb558874e221f2c09c0',
                     data=df_super, title=title_chart_s, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
