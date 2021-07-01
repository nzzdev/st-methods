import os
import pandas as pd
import gc
from datetime import datetime, timedelta
import sys


if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # set source data
        url = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv'

        # save data
        if not os.path.exists('data'):
            os.makedirs('data')
        with open(os.path.join('data', 'germany_vaccinations_timeseries_v2.tsv'), 'wb') as f:
            f.write(download_data(url).read())

        # read columns need for the chart
        df = pd.read_csv('./data/germany_vaccinations_timeseries_v2.tsv', delimiter='\t',
                         encoding='utf-8', usecols=['date', 'impf_quote_erst', 'impf_quote_voll'])

        # extract last row (=today), reset index and delete old df
        df2 = df.iloc[[-1]].reset_index(drop=True)
        del [[df]]
        gc.collect()

        # get date for chart notes and add one day
        timestamp_str = df2.loc[0, 'date']
        timestamp_dt = datetime.strptime(
            timestamp_str, '%Y-%m-%d') + timedelta(days=1)
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # delete date value in df
        df2.loc[0, 'date'] = ''

        # convert row values to percentage and do calculations for stacked bar chart
        df2['impf_quote_erst'] = (
            (df2['impf_quote_erst'] - df2['impf_quote_voll']) * 100).round(1)
        df2['impf_quote_voll'] = (df2['impf_quote_voll'] * 100).round(1)

        # create new column "Ziel" and calculate gap between status quo and herd immunity
        df2['Ziel'] = (80 - (df2['impf_quote_voll'] +
                             df2['impf_quote_erst'])).round(1)

        # rearrange columns
        df2 = df2[['date', 'impf_quote_voll', 'impf_quote_erst', 'Ziel']]

        # rename first column and set as index
        df2 = df2.rename(columns={
            'date': '', 'impf_quote_voll': 'vollständig geimpft', 'impf_quote_erst': 'erste Dose'}).set_index('')

        # show percentage total (copy to chart title later)
        title_percent = df2.iat[0, 0]+df2.iat[0, 1]
        title_percent_full = df2.iat[0, 0]
        title_chart = str(title_percent.round(1)).replace('.', ',') + \
            ' Prozent sind geimpft, ' + \
            str(title_percent_full.round(1)).replace('.', ',') + \
            ' Prozent vollständig'

        # show date in chart notes
        notes_chart = 'Impfquote von 80 Prozent in Grau. Der Impfstoff von J&J, von dem nur eine Dose nötig ist, ist sowohl in den Erst- als auch in den Zweitimpfungen enthalten. <br>Stand: ' + \
            timestamp_str

        # run function
        update_chart(id='dd4b1de66b3907bb65164669b0cca8dd',
                     data=df2, title=title_chart, notes=notes_chart)

    except:
        raise
    finally:
        f.close()
