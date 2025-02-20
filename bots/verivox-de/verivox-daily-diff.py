import os
from datetime import timedelta, date
import pandas as pd
from datawrapper import Datawrapper

if __name__ == '__main__':
    try:
        print("debug verivox daily")
        # set working directory, change if necessary; get dates
        os.chdir(os.path.dirname(__file__))
        today = date.today()
        lasty = today - timedelta(days=731)

        # Datawrapper API key
        dw_key = os.environ['DATAWRAPPER_API']
        dw = Datawrapper(access_token=dw_key)
        dw_id = 'sgFfi'

        # pre-crisis average 2018-2020
        gasavg = 969.58 # with bonus: 874.75
        acavg = 1090.16 # with bonus: 956.56

        # create indexed time series
        df = pd.read_csv(
            './data/gas-strom-bundesschnitt.tsv', sep='\t', index_col='date')
        df.index = pd.to_datetime(df.index)

        # Remove spikes due to missing suppliers in the Verivox database, see also gas-dashboard.py
        # Make sure data is sorted by date (if not already)
        df.sort_index(inplace=True)
        # Define threshold percentages
        increase_threshold = 1.1  # 10% increase
        decrease_threshold = 0.9  # 10% decrease
        def clean_outliers(df, column, inc_thresh=1.1, dec_thresh=0.9):
            """
            Detects and replaces both upward and downward isolated outliers in the specified column.
            """
            # Convert column to float for accurate calculations
            df[column] = df[column].astype(float)
            # Create shifted series for previous and next values
            prev = df[column].shift(1)
            next_ = df[column].shift(-1)
            prev_prev = df[column].shift(2)
            next_next = df[column].shift(-2)
            # Detect upward outliers
            upward_outliers = (df[column] > inc_thresh * prev) & (df[column] > inc_thresh * next_)
            # Ensure isolation: neither previous nor next day is also an upward outlier
            upward_isolated = upward_outliers & ~((prev > inc_thresh * prev_prev) | (next_ > inc_thresh * next_next))
            # Detect downward outliers
            downward_outliers = (df[column] < dec_thresh * prev) & (df[column] < dec_thresh * next_)
            # Ensure isolation: neither previous nor next day is also a downward outlier
            downward_isolated = downward_outliers & ~((prev < dec_thresh * prev_prev) | (next_ < dec_thresh * next_next))
            # Combine isolated outliers
            isolated_outliers = upward_isolated | downward_isolated
            # Replace outliers with the average of previous and next day's values
            df.loc[isolated_outliers, column] = (prev + next_) / 2
            # Round the values and convert back to integer
            df[column] = df[column].round().astype(int)
        # Apply the cleaning function to both 'Strom' and 'Gas' columns
        clean_outliers(df, 'Strom', inc_thresh=increase_threshold, dec_thresh=decrease_threshold)
        clean_outliers(df, 'Gas', inc_thresh=increase_threshold, dec_thresh=decrease_threshold)
        # Round the final values and convert to integer
        #df['Strom'] = df['Strom'].round().astype(int)
        #df['Gas'] = df['Gas'].round().astype(int)

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
        notes_chart = '¹ Bei einem Jahresverbrauch von 20 MWh Gas bzw. 4 MWh Strom. Gewichteter Bundesdurchschnitt der jeweils günstigsten Tarife (Preisgarantie mindestens 12 Monate, ohne Boni).<br>Stand: ' + timecode_str
        
        # update Datawrapper chart
        df.reset_index(inplace=True)
        dw_chart = dw.add_data(chart_id=dw_id, data=df)
        dw.update_chart(chart_id=dw_id, title=title_chart)
        date = {'annotate': {'notes': f'{notes_chart}'}}
        dw.update_metadata(chart_id=dw_id, metadata=date)
        dw.publish_chart(chart_id=dw_id, display=False)

    except:
        raise
