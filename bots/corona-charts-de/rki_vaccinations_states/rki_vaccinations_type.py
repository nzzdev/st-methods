import os
import pandas as pd
import sys

if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # set source data
        url = 'https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland/master/Aktuell_Deutschland_Bundeslaender_COVID-19-Impfungen.csv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'Aktuell_Deutschland_Bundeslaender_COVID-19-Impfungen.csv'), 'wb') as f:
            f.write(download_data(url).read())

        # read data
        csv = './data/Aktuell_Deutschland_Bundeslaender_COVID-19-Impfungen.csv'
        df = pd.read_csv(csv, encoding='utf-8',
                         usecols=['Impfdatum', 'BundeslandId_Impfort', 'Impfstoff', 'Anzahl'])

        # get date for chart notes
        df['Impfdatum'] = pd.to_datetime(df['Impfdatum'])
        timestamp_str = df['Impfdatum'].tail(1).item() + pd.Timedelta(days=1)
        timestamp_str = timestamp_str.strftime('%-d. %-m. %Y')

        # add empty row with next week number for Q step-after chart
        df = df.append(df.loc[df.index[-1]], ignore_index=True)
        df.loc[df.index[-1], 'Impfdatum'] = df.loc[df.index[-2],
                                                   'Impfdatum'] + pd.Timedelta(days=7)
        df.loc[df.index[-1], 'Anzahl'] = 0

        # calculate sum and convert to week number
        df['Impfdatum'] = df['Impfdatum'].apply(lambda x: str(
            x.isocalendar()[0]) + '-W' + str(x.isocalendar()[1]).zfill(2))
        df = df.groupby(['Impfdatum', 'Impfstoff'])[
            'Anzahl'].sum().reset_index()
        df = df.pivot(index='Impfdatum', columns='Impfstoff',
                      values='Anzahl').fillna(0).astype(int).reset_index()

        # sort and rename columns
        """
        df = df[['Impfdatum', 'Comirnaty', 'AstraZeneca',
                 'Moderna', 'Janssen', 'Novavax']]
        df = df.rename(columns={'Comirnaty': 'Biontech¹', 'AstraZeneca': 'AstraZeneca¹',
                       'Moderna': 'Moderna²', 'Janssen': 'J&J¹'}).set_index('Impfdatum')
        """
        df = df[['Impfdatum', 'Comirnaty', 'Spikevax',
                 'Comirnaty bivalent (Original/Omikron)', 'Spikevax bivalent (Original/Omikron)', 'Nuvaxovid', 'Valneva', 'Vaxzevria', 'Jcovden']]
        df = df.rename(columns={'Vaxzevria': 'AstraZeneca¹', 'Jcovden': 'J&J¹', 'Comirnaty': 'Biontech', 'Spikevax': 'Moderna', 'Nuvaxovid': 'Novavax', 'Valneva': 'Valneva',
                       'Comirnaty bivalent (Original/Omikron)': 'Biontech (Omikron)', 'Spikevax bivalent (Original/Omikron)': 'Moderna (Omikron)'}).set_index('Impfdatum')

        # show date in chart notes
        notes_chart = '¹ Lieferungen von AstraZeneca und J&J werden inzwischen gespendet. Im Sommer 2021 verzichtete Deutschland zugunsten von anderen EU-Staaten zudem auf Lieferungen von Moderna.<br>Stand: ' + timestamp_str

        df.to_clipboard()
        # run function
        update_chart(id='504d12c24392d6de848975cc5bc93b16',
                     data=df, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
