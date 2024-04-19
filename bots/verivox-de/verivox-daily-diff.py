import os
from datetime import timedelta, date
import pandas as pd
from datawrapper import Datawrapper

if __name__ == '__main__':
    try:

        # set working directory, change if necessary; get dates
        os.chdir(os.path.dirname(__file__))
        today = date.today()
        lasty = today - timedelta(days=365)

        # Datawrapper API key
        dw_key = os.environ['DATAWRAPPER_API']
        dw = Datawrapper(access_token=dw_key)
        dw_id = 'sgFfi'

        # pre-crisis average 2018-2020
        gasavg = 874.7527372
        acavg = 956.5565693

        # create indexed time series
        df = pd.read_csv(
            './data/gas-strom-bundesschnitt.tsv', sep='\t', index_col='date')
        df.index = pd.to_datetime(df.index)
        df = df.rolling(window=7).mean().dropna()
        df = df[~(df.index < f'{lasty}')]
        df['Gas'] = (df['Gas'] / gasavg) * 100
        df['Strom'] = (df['Strom'] / acavg) * 100
        # calculate percentage change
        df['Gas'] = abs(df['Gas']) - 100
        df['Strom'] = abs(df['Strom']) - 100

        # create dynamic chart title
        gas_new = df['Gas'].iloc[-1].round(0).astype(int)
        ac_new = df['Strom'].iloc[-1].round(0).astype(int)
        if gas_new > 0 and ac_new > 0:
            title_chart = f'Gas ist {abs(gas_new)} Prozent, Strom {abs(ac_new)} Prozent teurer als vor der Krise'
        elif gas_new < 0 and ac_new < 0:
            title_chart = f'Gas ist {abs(gas_new)} Prozent, Strom {abs(ac_new)} Prozent billiger als vor der Krise'
        elif gas_new == 0 and ac_new == 0:
            title_chart = f'Gas und Strom kosten so viel wie vor der Krise'
        elif gas_new == 0 and ac_new > 0:
            title_chart = f'Nur Strom ist noch {abs(ac_new)} Prozent teurer als vor der Krise'
        elif ac_new == 0 and gas_new > 0:
            title_chart = f'Nur Gas ist noch {abs(gas_new)} Prozent teurer als vor der Krise'
        elif gas_new == 0 and ac_new < 0:
            title_chart = f'Gas kostet so viel wie vor der Krise, Strom ist {abs(ac_new)} Prozent billiger'
        elif ac_new == 0 and gas_new < 0:
            title_chart = f'Strom kostet so viel wie vor der Krise, Gas ist {abs(gas_new)} Prozent billiger'
        elif gas_new > 0 and ac_new < 0:
            title_chart = f'Gas ist {abs(gas_new)} Prozent teurer als vor der Krise, Strom {abs(ac_new)} Prozent billiger'
        elif ac_new > 0 and gas_new < 0:
            title_chart = f'Strom ist {abs(ac_new)} Prozent teurer als vor der Krise, Gas {abs(gas_new)} Prozent billiger'

        # create notes
        timecode = df.index[-1]
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Bei einem Jahresverbrauch von 20 MWh Gas bzw. 4 MWh Strom. Gewichteter Bundesdurchschnitt der jeweils günstigsten Tarife (Preisgarantie mindestens 12 Monate, ohne Grundversorgung).<br>Stand: ' + timecode_str

        # update Datawrapper chart
        df.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id, data=df)
        dw.update_chart(chart_id=dw_id, title=title_chart)
        date = {'annotate': {'notes': f'{notes_chart}'}}
        dw.update_metadata(chart_id=dw_id, metadata=date)
        dw.publish_chart(chart_id=dw_id, display=False)

    except:
        raise
