import json
import pandas as pd
import os
from user_agent import generate_user_agent

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *
        from market_ids import *

        """
        # download stock market data
        tickers = ["TTF=F"]
        df = yf.download(tickers,  start="2019-01-01", end=date.today())

        df = df['Close']['TTF=F'][df.index >=
                                      '2021-03-01'].to_frame().dropna()
        df.rename(columns={'TTF=F': 'Kosten'}, inplace=True)
        df = df[['Kosten']]
        """

        # get data from theice.com/products/27996665/Dutch-TTF-Gas-Futures/data?marketId=5396828
        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getHistoricalChartDataAsJson=&marketId=' + \
            market_id + '&historicalSpan=3'
        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)

        # create dataframe and format date column
        df = pd.DataFrame(full_data['bars'], columns=['Datum', 'Kosten'])
        df['Datum'] = pd.to_datetime(df['Datum'])
        df.set_index('Datum', inplace=True)
        df = df['Kosten'][df.index >= '2020-12-31'].to_frame().dropna()

        # round numbers
        df['Kosten'] = df['Kosten'].round(0).astype(int)

        # get latest intraday data
        url = 'https://www.theice.com/marketdata/DelayedMarkets.shtml?getIntradayChartDataAsJson=&marketId=' + market_id
        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)

        # create dataframe and format date column
        df_intra = pd.DataFrame(full_data['bars'], columns=[
                                'Datum', 'Intraday'])
        df_intra['Datum'] = pd.to_datetime(df_intra['Datum'])
        df_intra.set_index('Datum', inplace=True)

        # save current price as csv for dashboard
        df_intra_today = df_intra.copy()
        #df_intra_today.index = pd.to_datetime(df_intra_today.index).strftime('%Y-%m-%d')
        df_intra_today = df_intra_today.rename(
            columns={df_intra_today.columns[0]: 'Gas-Börsenpreis'})
        df_intra_today = pd.concat(
            [df_intra_today.head(1), df_intra_today.tail(1)])
        df_intra_today.to_csv('./data/ttf-gas-stock-dash.csv')

        # calculate intraday mean and drop everything except last row
        df_intra['Kosten'] = df_intra['Intraday'].mean()
        df_intra = df_intra.drop(df_intra.index.to_list()[0:-1], axis=0)
        df_intra = df_intra.drop('Intraday', axis=1)
        df_intra['Kosten'] = df_intra['Kosten'].round(0).astype(int)

        # create final dataframe with historical and intraday data
        df_full = pd.concat([df, df_intra])

        # dynamic chart title
        title_mwh = df_full[df_full.columns[0]].iloc[-1].round(0).astype(int)
        title = f'Gas kostet an der Börse im Schnitt {title_mwh} Euro je MWh'

        # create date for chart notes
        timecode = df_full.index[-1]
        timecode_str = timecode.strftime('%-d. %-m. %Y')
        notes_chart = '¹ Preise für Terminkontrakte mit Lieferung im nächsten Monat; aktueller Tag: Tagesdurchschnitt.<br>Stand: ' + timecode_str

        # convert DatetimeIndex
        #df_full.index = df_full.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(id='4decc4d9f742ceb683fd78fa5937acfd',
                     title=title, notes=notes_chart, data=df_full)

    except:
        raise
