import os
import pandas
import yfinance as yf
from datetime import date

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *

        # download stock market data
        tickers = ["EURCHF=X", "KE=F", "TTF=F",
                   "^GDAXI", "EURUSD=X", "BTC-USD", "BZ=F"]
        df = yf.download(tickers,  start="2019-01-01", end=date.today())

        df_gas = df['Close']['TTF=F'][df.index >=
                                      '2021-03-01'].to_frame().dropna()
        df_gas.rename(columns={'TTF=F': 'Kosten'}, inplace=True)
        df_gas = df_gas[['Kosten']]

        # create date for chart notes
        timecode = df_gas.index[-1]
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = 'Stand: ' + timecode_str

        # convert DatetimeIndex
        df_gas.index = df_gas.index.strftime('%Y-%m-%d')

        update_chart(id='4decc4d9f742ceb683fd78fa5937acfd',
                     notes=notes_chart, data=df_gas[['Kosten']])

    except:
        raise
