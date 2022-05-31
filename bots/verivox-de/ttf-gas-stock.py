import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
import pandas as pd
import os
from datetime import date
from user_agent import generate_user_agent

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *

        """
        # download stock market data
        tickers = ["TTF=F"]
        df = yf.download(tickers,  start="2019-01-01", end=date.today())

        df = df['Close']['TTF=F'][df.index >=
                                      '2021-03-01'].to_frame().dropna()
        df.rename(columns={'TTF=F': 'Kosten'}, inplace=True)
        df = df[['Kosten']]
        """

        # retry if error
        logging.basicConfig(level=logging.INFO)
        s = requests.Session()
        retries = Retry(total=10, backoff_factor=1,
                        status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        # get data from theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5396828
        headers = generate_user_agent()
        url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getHistoricalChartDataAsJson=&marketId=5396828&historicalSpan=3'
        resp = s.get(url, headers=headers)
        json_file = resp.text
        full_data = json.loads(json_file)

        # create dataframe and format date column
        df = pd.DataFrame(full_data['bars'], columns=['Datum', 'Kosten'])
        df['Datum'] = pd.to_datetime(df['Datum'])
        df.set_index('Datum', inplace=True)
        df = df['Kosten'][df.index >= '2021-03-01'].to_frame().dropna()

        # create date for chart notes
        timecode = df.index[-1]
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = 'Stand: ' + timecode_str

        # convert DatetimeIndex
        df.index = df.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(id='4decc4d9f742ceb683fd78fa5937acfd',
                     notes=notes_chart, data=df)

    except:
        raise
