import json
import pandas as pd
import os
from user_agent import generate_user_agent
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from datawrapper import Datawrapper

if __name__ == '__main__':
    try:

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))
        from helpers import *
        from market_ids import *

        # Datawrapper API key
        dw_key = os.environ['DATAWRAPPER_API']
        dw = Datawrapper(access_token=dw_key)
        dw_id = 'C3pJx'

        """
        # SpaceX stock chart in Q
        spacex_ticker = 'SPCX'
        spacex_chart_id = 'cd90678a1369ca3d8a0e9f5c2febd9f1'
        """

        # headers for ICE data
        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }

        # download historical data from Yahoo
        df = yf.download('TTF=F', period='5y', auto_adjust=False)

        # extract the 'Close' column and convert to DataFrame
        df = df[('Close', 'TTF=F')]
        df = df[df.index >= '2020-12-31'].dropna()
        df = df.to_frame(name='Kosten')
        df.index.rename('Datum', inplace=True)
        df['Kosten'] = df['Kosten'].round(2).astype(float)

        print("Yahoo Finance download successful")
        print(f"Yahoo rows: {len(df)}")

        if not df.empty:
            print(
                f"Yahoo date range: "
                f"{df.index[0].strftime('%Y-%m-%d')} -> "
                f"{df.index[-1].strftime('%Y-%m-%d')}"
            )
            print(f"Yahoo latest value: {df['Kosten'].iloc[-1]}")
        else:
            raise RuntimeError("Yahoo Finance returned no TTF data")

        """
        # as Dataframe instead of Series
        # extract the Series and convert to DataFrame
        df = df[('Close', 'TTF=F')]
        df = df[df.index >= '2020-12-31'].dropna()
        df = df.to_frame(name='Kosten')

        # rename the index and adjust values
        df.index.rename('Datum', inplace=True)
        df['Kosten'] = df['Kosten'].round(2).astype(float)
        """

        # drop last buggy value from Yahoo if current day
        today = datetime.today().strftime('%Y-%m-%d')

        if today == df.index[-1].strftime('%Y-%m-%d'):
            print(
                "Yahoo latest value is from current day; "
                "dropping it before ICE update"
            )
            df.drop(df.tail(1).index, inplace=True)

        # ------------------------------------------------------------------
        # Get latest data from ICE.
        #
        # ICE occasionally returns an empty response, HTML, a block page,
        # or otherwise invalid JSON. In that case we keep the Yahoo data
        # and allow the rest of the script to continue.
        # ------------------------------------------------------------------

        url = (
            'https://www.ice.com/marketdata/api/productguide/charting/'
            'data/historical?marketId='
            + market_id
            + '&historicalSpan=2'
        )

        print("")
        print("========== ICE DEBUG ==========")
        print(f"ICE market ID: {market_id}")
        print(f"ICE URL: {url}")

        bars = None
        full_data = None

        try:
            resp = download_data(url, headers=fheaders)

            status_code = getattr(resp, 'status_code', 'unknown')

            if hasattr(resp, 'headers'):
                content_type = resp.headers.get('content-type', 'unknown')
            else:
                content_type = 'unknown'

            response_text = getattr(resp, 'text', '')

            if response_text is None:
                response_text = ''

            print(f"ICE HTTP status: {status_code}")
            print(f"ICE content-type: {content_type}")
            print(f"ICE response length: {len(response_text)} characters")
            print(f"ICE response start: {response_text[:500]!r}")

            # Raise an exception for HTTP errors such as 403, 429, 500 etc.
            if hasattr(resp, 'raise_for_status'):
                resp.raise_for_status()

            # Explicit check because json.loads('') produces an
            # unhelpful JSONDecodeError.
            if not response_text.strip():
                raise ValueError("ICE returned an empty response")

            # Parse response as JSON
            try:
                full_data = resp.json()
            except (AttributeError, ValueError):
                full_data = json.loads(response_text)

            print(f"ICE JSON type: {type(full_data).__name__}")

            if isinstance(full_data, dict):
                print(f"ICE top-level keys: {list(full_data.keys())}")

                # Determine bars data in ICE response.
                # The key used by ICE may vary.
                for key in ['bars', 'data']:
                    if key in full_data and full_data[key]:
                        bars = full_data[key]
                        print(f"ICE bars found under key: {key}")
                        break

                # Some ICE responses can contain bars inside a series list.
                if not bars and isinstance(full_data.get('series'), list):
                    for series_entry in full_data['series']:
                        if (
                            isinstance(series_entry, dict)
                            and series_entry.get('bars')
                        ):
                            bars = series_entry['bars']
                            print("ICE bars found under series -> bars")
                            break

            elif isinstance(full_data, list):
                # Debug information in case ICE changes to a list response.
                print(
                    f"ICE returned a top-level list "
                    f"with {len(full_data)} entries"
                )

                # If it already looks like bar data, use it.
                if full_data:
                    bars = full_data

            else:
                print(
                    "Warning: ICE returned an unexpected JSON structure: "
                    f"{type(full_data).__name__}"
                )

            if bars:
                print(f"ICE bars count: {len(bars)}")
                print(f"ICE latest bar raw: {bars[-1]}")
            else:
                print("ICE response contains no usable bars")

        except Exception as e:
            print(f"Warning: ICE request/parsing failed: {type(e).__name__}: {e}")
            print("Skipping ICE update and using Yahoo Finance data only")
            bars = None

        print("======== END ICE DEBUG ========")
        print("")

        # If no ICE data found, skip merging ICE price
        if not bars:
            print("Warning: No ICE data found; skipping ICE update")

        else:
            try:
                df_ice = pd.DataFrame(
                    bars,
                    columns=['Datum', 'Kosten']
                )

                df_ice = df_ice.tail(1)

                print("ICE latest row after DataFrame conversion:")
                print(df_ice.to_string(index=False))

                df_ice['Datum'] = pd.to_datetime(
                    df_ice['Datum']
                ).dt.strftime('%Y-%m-%d')

                df_ice['Datum'] = pd.to_datetime(df_ice['Datum'])
                df_ice.set_index('Datum', inplace=True)

                df_ice['Kosten'] = (
                    df_ice['Kosten']
                    .round(2)
                    .astype(float)
                )

                print(
                    f"ICE latest parsed date: "
                    f"{df_ice.index[-1].strftime('%Y-%m-%d')}"
                )
                print(
                    f"ICE latest parsed value: "
                    f"{df_ice['Kosten'].iloc[-1]}"
                )

                # merge with main DataFrame, avoiding duplicates
                df = pd.concat([df, df_ice], axis=0)
                df = df[~df.index.duplicated(keep='last')]
                df = df.sort_index()

                print("ICE latest value successfully merged with Yahoo data")

            except Exception as e:
                print(
                    f"Warning: ICE bars could not be processed: "
                    f"{type(e).__name__}: {e}"
                )
                print("Continuing with Yahoo Finance data only")

        print(
            f"Final latest TTF date before chart processing: "
            f"{df.index[-1].strftime('%Y-%m-%d')}"
        )
        print(
            f"Final latest TTF value before chart processing: "
            f"{df['Kosten'].iloc[-1]}"
        )

        # create chart with comparison
        dfold = pd.read_csv(
            './data/ttf-gas-stock-historical.tsv',
            sep='\t',
            index_col=None
        )

        yesterday_year = datetime.now() - timedelta(days=1)
        year = yesterday_year.year

        dfold['Datum'] = pd.to_datetime(dfold['Datum'])

        dfnew = dfold.merge(
            df,
            on='Datum',
            how='left'
        )

        dfnew = dfnew[
            [
                'Datum',
                'Kosten',
                '2024',
                '2023',
                '2022',
                'Vorkrisenniveau²'
            ]
        ]

        dfnew = dfnew.rename(
            columns={'Kosten': f'{year}'}
        )

        dfnew.set_index('Datum', inplace=True)

        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$',
            np.nan,
            regex=True
        )

        # for wrong dates
        dfnew[f'{year}'] = dfnew[f'{year}'].interpolate(
            method='linear',
            limit_direction='backward'
        )

        dfnew = dfnew.drop('2023', axis=1)
        dfnew = dfnew.drop('2024', axis=1)

        df['Kosten'] = df['Kosten'].round(0).astype(int)

        """
        # get weekdays for current year from Dutch stock market
        # import pandas_market_calendars as mcal
        xams = mcal.get_calendar('LSE')  # ICE US
        early = xams.schedule(
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        df_tradingdays = pd.DataFrame(
            pd.DatetimeIndex(
                mcal.date_range(
                    early,
                    frequency='1D'
                )
            )
        )
        """

        """
        # START historical ICE data from
        # theice.com/products/27996665/Dutch-TTF-Gas-Futures/
        # data?marketId=5396828

        url = (
            'https://www.theice.com/marketdata/'
            'DelayedMarkets.shtml?getHistoricalChartDataAsJson=&marketId='
            + market_id
            + '&historicalSpan=3'
        )

        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)

        # create dataframe and format date column
        df = pd.DataFrame(
            full_data['bars'],
            columns=['Datum', 'Kosten']
        )

        df['Datum'] = pd.to_datetime(df['Datum'])
        df.set_index('Datum', inplace=True)

        df = (
            df['Kosten'][df.index >= '2020-12-31']
            .to_frame()
            .dropna()
        )

        # round numbers
        df['Kosten'] = df['Kosten'].round(0).astype(int)
        # END old historical ICE data
        """

        # save current price as csv for dashboard
        df_intra_today = df.copy()

        # df_intra_today.index = pd.to_datetime(
        #     df_intra_today.index
        # ).strftime('%Y-%m-%d')

        df_intra_today = df_intra_today.rename(
            columns={
                df_intra_today.columns[0]: 'Gas-Börsenpreis'
            }
        )

        df_intra_today = pd.concat(
            [df_intra_today.tail(2)]
        )

        df_intra_today.to_csv(
            './data/ttf-gas-stock-dash.csv'
        )

        # generate additional dashboard time series starting 2025-01-01
        # (2025 + 2026)
        # Use df (Yahoo + last ICE point). This already contains
        # 2025/2026 trading days.
        df_dash_full = df.copy()

        # ensure clean index and column name for dashboard
        df_dash_full = (
            df_dash_full[
                ~df_dash_full.index.duplicated(keep='last')
            ]
            .sort_index()
        )

        # keep from 2025-01-01 onward
        df_dash_full = df_dash_full[
            df_dash_full.index >= pd.Timestamp('2025-01-01')
        ]

        # rename to dashboard column name
        df_dash_full = df_dash_full.rename(
            columns={
                'Kosten': 'Gas-Börsenpreis'
            }
        )

        # drop non-trading days / holidays (rows without data)
        df_dash_full = df_dash_full[
            df_dash_full['Gas-Börsenpreis'].notna()
        ]

        df_dash_full.to_csv(
            './data/ttf-gas-stock-dash_full.csv'
        )

        """
        # START hourly prices (not reliable)

        # save current price as csv for dashboard

        # get latest intraday data from ICE
        # (avoid errors with Yahoo Finance)
        url = (
            'https://www.theice.com/marketdata/'
            'DelayedMarkets.shtml?getIntradayChartDataAsJson=&marketId='
            + market_id
        )

        resp = download_data(url, headers=fheaders)
        json_file = resp.text
        full_data = json.loads(json_file)

        df_intra = pd.DataFrame(
            full_data['bars'],
            columns=['Datum', 'Intraday']
        )

        df_intra = df_intra.tail(1)
        df_intra['Datum'] = pd.to_datetime(df_intra['Datum'])
        df_intra.set_index('Datum', inplace=True)

        df_intra_today = df_intra.copy()
        df_intra_today = df.copy()

        # df_intra_today.index = pd.to_datetime(
        #     df_intra_today.index
        # ).strftime('%Y-%m-%d')

        df_intra_today = df_intra_today.rename(
            columns={
                df_intra_today.columns[0]:
                'Gas-Börsenpreis'
            }
        )

        df_intra_today = pd.concat(
            [df_intra_today.head(1), df_intra_today.tail(1)]
        )

        df_intra_today.to_csv(
            './data/ttf-gas-stock-dash.csv'
        )

        # END hourly prices (not reliable)

        # calculate intraday mean and drop everything except last row
        df_intra['Kosten'] = df_intra['Intraday'].mean()

        df_intra = df_intra.drop(
            df_intra.index.to_list()[0:-1],
            axis=0
        )

        df_intra = df_intra.drop(
            'Intraday',
            axis=1
        )

        df_intra['Kosten'] = (
            df_intra['Kosten']
            .round(0)
            .astype(int)
        )

        # create final dataframe with historical and intraday data
        # drop last pseudo historical value from Yahoo
        # and replace with intraday data
        df.drop(df.tail(1).index, inplace=True)

        df_full = pd.concat(
            [df, df_intra]
        )
        """

        # convert Euro / MWh to Cent / kWh
        dfnew[f'{year}'] = dfnew[f'{year}'].replace(
            r'^\s*$',
            np.nan,
            regex=True
        )

        dfnew = dfnew.divide(10).round(3)
        df = df.divide(10)

        # get pre-crisis value
        kwh_new = dfnew[f'{year}'].loc[
            dfnew[f'{year}'].last_valid_index()
        ]

        kwh_new_pos = dfnew[f'{year}'].index.get_loc(
            dfnew[f'{year}'].last_valid_index()
        )

        kwh_old = dfnew.iloc[
            kwh_new_pos
        ]['Vorkrisenniveau²']

        title_kwh_diff = round(
            (kwh_new - kwh_old),
            1
        )

        title_kwh_diff_perc = round(
            100 * (kwh_new - kwh_old) / kwh_old,
            0
        ).astype(int)

        title_kwh = round(kwh_new, 1)

        dfnew[f'{year}'] = dfnew[f'{year}'].fillna('')

        print("")
        print("========== CHART DEBUG ==========")
        print(f"Current chart year: {year}")
        print(f"Latest current-year value: {kwh_new}")
        print(f"Vorkrisenniveau: {kwh_old}")
        print(f"Difference: {title_kwh_diff}")
        print(f"Difference percent: {title_kwh_diff_perc}")
        print("======== END CHART DEBUG ========")
        print("")

        # dynamic chart title
        title_old = (
            f'Gas kostet im Grosshandel '
            f'{title_kwh.astype(str).replace(".", ",")} Cent'
        )

        if title_kwh_diff > 0:
            title = (
                f'Gas kostet im Grosshandel '
                f'{title_kwh.astype(str).replace(".", ",")} Cent – '
                f'{title_kwh_diff_perc} Prozent mehr als vor der Krise'
            )

        elif title_kwh_diff == 0:
            title = (
                f'Gas kostet im Grosshandel '
                f'{title_kwh.astype(str).replace(".", ",")} Cent – '
                f'so viel wie vor der Krise'
            )

        else:
            title = (
                f'Gas kostet im Grosshandel '
                f'{title_kwh.astype(str).replace(".", ",")} Cent – '
                f'{abs(title_kwh_diff_perc)} Prozent weniger als '
                f'vor der Krise'
            )

        """
        title_old = (
            f'Gas kostet im Grosshandel '
            f'{title_kwh.astype(str).replace(".", ",")} Cent'
        )

        if title_kwh_diff > 0:
            title = (
                f'Gas kostet im Grosshandel '
                f'{title_kwh.astype(str).replace(".", ",")} Cent – '
                f'{title_kwh_diff.astype(str).replace(".", ",")} '
                f'Cent mehr als vor der Krise'
            )

        elif title_kwh_diff == 0:
            title = (
                f'Gas kostet im Grosshandel '
                f'{title_kwh.astype(str).replace(".", ",")} Cent – '
                f'so viel wie vor der Krise'
            )

        else:
            title = (
                f'Gas kostet im Grosshandel '
                f'{title_kwh.astype(str).replace(".", ",")} Cent – '
                f'{abs(title_kwh_diff).astype(str).replace(".", ",")} '
                f'Cent weniger als vor der Krise'
            )
        """

        # create date for chart notes
        timecode = df.index[-1]  # old: df_full
        timecode_str = timecode.strftime('%-d. %-m. %Y')

        notes_chart = (
            '¹ Preise für Terminkontrakte mit Lieferung '
            'im jeweils nächsten Monat.<br>Stand: '
            + timecode_str
        )

        notes_chart_new = (
            '¹ Preise für Terminkontrakte mit Lieferung '
            'im jeweils nächsten Monat.<br>'
            '² Durchschnitt 2018-2020.<br>Stand: '
            + timecode_str
        )

        """
        # SpaceX stock chart:
        # historical daily close values from Yahoo Finance.

        # Do not force an intraday/overnight point:
        # for SPCX, Yahoo's quote and chart endpoints
        # currently expose inconsistent values or block requests.

        df_spacex = yf.download(
            spacex_ticker,
            period='1y',
            interval='1d',
            auto_adjust=False
        )

        df_spacex = df_spacex['Close'].dropna()

        if isinstance(df_spacex, pd.Series):
            df_spacex = df_spacex.to_frame(
                name=spacex_ticker
            )
        else:
            df_spacex = df_spacex.rename(
                columns={
                    df_spacex.columns[0]:
                    spacex_ticker
                }
            )

        df_spacex.index.rename(
            'Date',
            inplace=True
        )

        df_spacex = df_spacex.sort_index()

        df_spacex[spacex_ticker] = (
            df_spacex[spacex_ticker]
            .round(2)
            .astype(float)
        )

        title_spacex = (
            'So hat sich die SpaceX-Aktie '
            'seit Handelsstart entwickelt'
        )

        spacex_timecode = df_spacex.index[-1]

        spacex_timecode_str = spacex_timecode.strftime(
            '%-d. %-m. %Y'
        )

        notes_spacex = (
            'Schlusskurse.<br>Stand: '
            + spacex_timecode_str
        )

        # Q option: minimal value Y-axis.
        # Keep it below the lowest value in the data.
        spacex_min_y = int(
            np.floor(
                df_spacex[spacex_ticker].min() / 10
            ) * 10
        )
        """

        # convert DatetimeIndex
        # df_full.index = df_full.index.strftime('%Y-%m-%d')

        # run Q function
        update_chart(
            id='4decc4d9f742ceb683fd78fa5937acfd',
            title=title_old,
            notes=notes_chart,
            data=df
        )

        update_chart(
            id='74063b3ff77f45a56472a5cc70bb2a93',
            title=title,
            notes=notes_chart_new,
            data=dfnew
        )

        """
        update_chart(
            id=spacex_chart_id,
            title=title_spacex,
            data=df_spacex,
            notes=notes_spacex,
            options={
                'lineChartOptions': {
                    'minValue': spacex_min_y
                }
            }
        )
        """

        # Rename column for Datawrapper
        dfnew = dfnew.rename(
            columns={
                'Vorkrisenniveau²':
                'Vorkrisen-Niveau²'
            }
        )

        # update Datawrapper chart
        dfnew.reset_index(inplace=True)

        dw_chart = dw.add_data(
            chart_id=dw_id,
            data=dfnew
        )

        dw.update_chart(
            chart_id=dw_id,
            title=title
        )

        date = {
            'annotate': {
                'notes': f' {notes_chart_new}'
            }
        }

        dw.update_metadata(
            chart_id=dw_id,
            metadata=date
        )

        dw.publish_chart(
            chart_id=dw_id,
            display=False
        )

    except:
        raise