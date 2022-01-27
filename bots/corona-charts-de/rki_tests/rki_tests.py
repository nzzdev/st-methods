import os
import requests
import pandas as pd
import sys
from datetime import datetime, timedelta
import tempfile


def read_xlsx_from_url(url, **kwargs):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686)'}
    response = requests.get(url, headers=headers)
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        with open(tmp.name, 'wb') as f:
            f.write(response.content)
        df = pd.read_excel(tmp.name, **kwargs)
    df = df.dropna(how='all')
    return df


class Germany:
    def __init__(self):
        self.location = 'Germany'
        self.source_url = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Testzahlen-gesamt.xlsx?__blob=publicationFile'

    def read(self):
        df = read_xlsx_from_url(
            self.source_url, sheet_name='1_Testzahlerfassung')
        mask = df.Kalenderwoche.str.match(r'\d{1,2}/\d{4}')
        df = df[mask]
        return df

    def pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            **{
                'Datum': df.Kalenderwoche.apply(
                    lambda x: datetime.strptime(
                        x + ' +0', '%V/%G +%w').strftime('%Y-%m-%d')
                ),
                'Negative Tests': df['Anzahl Testungen'] - df['Positiv getestet'],
                'Positive Tests': df['Positiv getestet']
            }
        ).sort_values('Datum')

        df = df[
            [
                'Datum',
                'Negative Tests',
                'Positive Tests',
            ]
        ]
        return df

    def to_df(self):
        df = self.read().pipe(self.pipeline)
        # add row with current date for step-after chart
        timestamp_df = df['Datum'].iloc[-1]
        timestamp = datetime.strptime(
            timestamp_df, '%Y-%m-%d') + timedelta(weeks=1)
        df.loc[-1] = [str(timestamp).split(" ")[0], '', '']
        df = df.set_index('Datum')
        timestamp_str = datetime.strptime(
            timestamp_df, '%Y-%m-%d').strftime('%-d. %-m. %Y')
        notes_chart = 'Je höher der Anteil der positiven Tests im Verhältnis zum Anteil der negativen Tests, desto höher die Positivrate.<br>Stand: ' + timestamp_str
        update_chart(id='fcd18326e9d6d215efe2e522678af018',
                     data=df, notes=notes_chart)


def main():
    Germany().to_df()


if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        main()

    except:
        raise
