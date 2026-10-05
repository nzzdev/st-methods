import json
import os
import io
from time import sleep
from datetime import datetime, date, timedelta

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from user_agent import generate_user_agent


if __name__ == '__main__':
    try:

        # ---------------------------------------------------------------------
        # Arbeitsverzeichnis
        # ---------------------------------------------------------------------

        os.chdir(os.path.dirname(__file__))

        from helpers import *


        # =====================================================================
        # LNG-Importe EU / Bruegel via Infogram
        # =====================================================================

        fheaders = {
            'user-agent': generate_user_agent(),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }


        # ---------------------------------------------------------------------
        # Infogram-Daten
        # ---------------------------------------------------------------------

        urlnew = (
            'https://infogram.com/'
            '83b2e7a1-a4b0-47eb-acff-5530f94e6247'
        )

        urllng = (
            'https://infogram.com/'
            'fb29e40e-29d2-4d11-a87c-41f497270031'
        )


        respnew = download_data(
            urlnew,
            headers=fheaders
        )

        resplng = download_data(
            urllng,
            headers=fheaders
        )


        htmlnew = respnew.text
        htmllng = resplng.text


        soupnew = BeautifulSoup(
            htmlnew,
            features='html.parser'
        )

        souplng = BeautifulSoup(
            htmllng,
            features='html.parser'
        )


        snew = soupnew.findAll('script')
        slng = souplng.findAll('script')


        full_script_new = None
        full_script_lng = None


        # ---------------------------------------------------------------------
        # Infogram-JSON extrahieren
        # ---------------------------------------------------------------------

        for script in snew:

            if not script.contents:
                continue

            script_text = str(
                script.contents[0]
            )

            if 'window.infographicData' in script_text:

                full_script_new = (
                    script_text
                    .split(
                        'window.infographicData=',
                        1
                    )[1]
                    .strip()
                    .rstrip(';')
                )

                break


        if full_script_new is None:

            raise RuntimeError(
                'Infogram-Daten für urlnew '
                'konnten nicht gefunden werden.'
            )


        full_data_new = json.loads(
            full_script_new
        )


        # ---------------------------------------------------------------------
        # LNG-Infogram
        # ---------------------------------------------------------------------

        for script in slng:

            if not script.contents:
                continue

            script_text = str(
                script.contents[0]
            )

            if 'window.infographicData' in script_text:

                full_script_lng = (
                    script_text
                    .split(
                        'window.infographicData=',
                        1
                    )[1]
                    .strip()
                    .rstrip(';')
                )

                break


        if full_script_lng is None:

            raise RuntimeError(
                'Infogram-Daten für LNG '
                'konnten nicht gefunden werden.'
            )


        full_data_lng = json.loads(
            full_script_lng
        )


        # ---------------------------------------------------------------------
        # LNG-Daten aus dem Infogram
        # ---------------------------------------------------------------------

        df_list_lng = []


        for data in (
            full_data_lng[
                'elements'
            ][
                'content'
            ][
                'content'
            ][
                'entities'
            ][
                '3a41ab1a-9ccc-40b3-a1d3-225d07a8eeb8bac6ef8b-2f7e-487e-ae9f-69e8a6bd2593'
            ][
                'props'
            ][
                'chartData'
            ][
                'data'
            ]
        ):

            headers = [
                'KW',
                'America',
                'Africa',
                'Middle East',
                'Russia',
                'Other'
            ]

            # Headerzeilen entfernen
            del data[0]
            del data[0]

            df_lng_new = pd.DataFrame(
                data,
                columns=headers
            )

            df_list_lng.append(
                df_lng_new
            )


        # =====================================================================
        # LNG-Daten bereinigen
        # =====================================================================

        lng_columns = [
            'America',
            'Africa',
            'Middle East',
            'Russia',
            'Other'
        ]


        for column in lng_columns:

            df_lng_new[column] = (
                df_lng_new[column]
                .astype(str)
                .str.replace(
                    r'{.*?xa0 ',
                    '',
                    regex=True
                )
                .str.replace(
                    '}',
                    '',
                    regex=False
                )
                .str.replace(
                    "{'value': '",
                    '',
                    regex=False
                )
                .str.replace(
                    ',',
                    '',
                    regex=False
                )
            )

            df_lng_new[column] = pd.to_numeric(
                df_lng_new[column],
                errors='coerce'
            ).astype(float)


        # ---------------------------------------------------------------------
        # Datum bereinigen
        # ---------------------------------------------------------------------

        df_lng_new['KW'] = (
            df_lng_new['KW']
            .astype(str)
            .str.extract(
                r'(\d{2}/\d{4})',
                expand=False
            )
        )


        df_lng_new.rename(
            columns={
                'KW': 'Datum',
                'America': 'USA',
                'Africa': 'Afrika',
                'Middle East': 'Mittlerer Osten',
                'Russia': 'Russland',
                'Other': 'Sonstige'
            },
            inplace=True
        )


        df_lng_new = df_lng_new[
            [
                'Datum',
                'Russland',
                'USA',
                'Afrika',
                'Mittlerer Osten',
                'Sonstige'
            ]
        ]


        # ---------------------------------------------------------------------
        # Datum auf Monatsbasis
        # ---------------------------------------------------------------------

        df_lng_new['Datum'] = pd.to_datetime(
            df_lng_new['Datum'],
            format='%m/%Y',
            errors='coerce'
        )


        lngdate = (
            df_lng_new['Datum'].max()
            + pd.DateOffset(months=1)
        )


        df_lng_new['Datum'] = (
            df_lng_new['Datum']
            .fillna(lngdate)
        )


        df_lng_new.set_index(
            'Datum',
            inplace=True
        )


        month_str = lngdate.strftime(
            '%-d. %-m. %Y'
        )


        notes_chart_lng = (
            '¹ USA mit Trinidad und Tobago. '
            'Der grösste Exporteur im Mittleren Osten '
            'ist Katar; in Afrika exportieren Nigeria '
            'und Algerien am meisten.'
            '<br>Stand: '
            + month_str
        )


        df_lng_new = (
            df_lng_new
            .fillna('')
        )


        # ---------------------------------------------------------------------
        # LNG-Grafik aktualisieren
        # ---------------------------------------------------------------------

        update_chart(
            id='6c02e1d1daabb23cfaaae686241d6e4e',
            data=df_lng_new,
            notes=notes_chart_lng
        )


        # =====================================================================
        # GASIMPORTE DEUTSCHLAND – BUNDESNETZAGENTUR
        # =====================================================================

        BNETZA_URL = (
            'https://www.bundesnetzagentur.de/'
            'SiteGlobals/Functions/SVG/_functions/'
            'csv_export.html'
            '?view=renderCSV&id=870296'
        )

        LNG_IMPORTS_CACHE = (
            './data/lng_imports.tsv'
        )


        # ---------------------------------------------------------------------
        # Aktuelle BNetzA-Daten laden
        # ---------------------------------------------------------------------

        try:

            print(
                'Lade Gasimporte von der '
                'Bundesnetzagentur ...'
            )


            resp = download_data(
                BNETZA_URL,
                headers=fheaders
            )


            # Falls download_data ein requests.Response liefert
            if hasattr(
                resp,
                'raise_for_status'
            ):
                resp.raise_for_status()


            csv_file = resp.text


            if not csv_file.strip():

                raise ValueError(
                    'BNetzA lieferte eine leere Antwort.'
                )


            # -------------------------------------------------------------
            # CSV lesen
            # -------------------------------------------------------------

            df_ns_new = pd.read_csv(
                io.StringIO(csv_file),
                encoding='utf-8',
                sep=';',
                decimal=',',
                index_col=None
            )


            # -------------------------------------------------------------
            # Erste Spalte hat derzeit nur "." als Überschrift.
            # Unabhängig davon immer als "Datum" benennen.
            # -------------------------------------------------------------

            df_ns_new.rename(
                columns={
                    df_ns_new.columns[0]:
                    'Datum'
                },
                inplace=True
            )


            # -------------------------------------------------------------
            # Erwartete Spalten prüfen
            # -------------------------------------------------------------

            required_columns = {
                'Datum',
                'Tschechien',
                'Niederlande',
                'Belgien',
                'Polen',
                'Norwegen',
                'Dänemark',
                'Frankreich',
                'Österreich',
                'Schweiz',
                'Russland',
                'LNG',
                'Deutschland Import'
            }


            missing_columns = (
                required_columns
                - set(df_ns_new.columns)
            )


            if missing_columns:

                raise ValueError(
                    'BNetzA-CSV: '
                    'Folgende Spalten fehlen: '
                    f'{sorted(missing_columns)}. '
                    'Vorhandene Spalten: '
                    f'{df_ns_new.columns.tolist()}'
                )


            # -------------------------------------------------------------
            # Datum und zentrale Werte konvertieren
            # -------------------------------------------------------------

            df_ns_new['Datum'] = pd.to_datetime(
                df_ns_new['Datum']
                .astype(str)
                .str.strip(),
                format='%d.%m.%Y',
                errors='coerce'
            )


            numeric_columns = [
                'Tschechien',
                'Niederlande',
                'Belgien',
                'Polen',
                'Norwegen',
                'Dänemark',
                'Frankreich',
                'Österreich',
                'Schweiz',
                'Russland',
                'LNG',
                'Deutschland Import'
            ]


            for column in numeric_columns:

                df_ns_new[column] = pd.to_numeric(
                    df_ns_new[column],
                    errors='coerce'
                )


            # -------------------------------------------------------------
            # Ungültige Datumszeilen entfernen
            # -------------------------------------------------------------

            df_ns_new = (
                df_ns_new
                .dropna(
                    subset=[
                        'Datum',
                        'Deutschland Import'
                    ]
                )
                .sort_values('Datum')
                .reset_index(drop=True)
            )


            if df_ns_new.empty:

                raise ValueError(
                    'BNetzA-CSV enthält '
                    'keine verwertbaren Daten.'
                )


            # -------------------------------------------------------------
            # Die BNetzA liefert gelegentlich am Ende eine noch
            # unvollständige Tageszeile.
            #
            # Wir entfernen NICHT pauschal die letzte Zeile.
            # Stattdessen verwenden wir die letzte Zeile, bei der
            # Gesamtimport UND LNG vorhanden sind.
            #
            # Frühere LNG-NaN-Werte vor Inbetriebnahme der deutschen
            # Terminals bleiben dadurch erhalten.
            # -------------------------------------------------------------

            complete_rows = (
                df_ns_new[
                    'Deutschland Import'
                ].notna()
                & df_ns_new[
                    'LNG'
                ].notna()
            )


            complete_positions = np.flatnonzero(
                complete_rows.to_numpy()
            )


            if len(
                complete_positions
            ) == 0:

                raise ValueError(
                    'BNetzA-CSV enthält '
                    'keine vollständige Zeile '
                    'mit Gesamtimport und LNG.'
                )


            last_complete_position = (
                complete_positions[-1]
            )


            df_ns_new = (
                df_ns_new
                .iloc[
                    :last_complete_position + 1
                ]
                .copy()
            )


            latest_new_date = (
                df_ns_new[
                    'Datum'
                ].max()
            )


            # -------------------------------------------------------------
            # Prüfen, wie aktuell die Daten sind.
            #
            # Nicht abbrechen, falls die BNetzA einmal einige Tage
            # hinterherhinkt – aber deutlich warnen.
            # -------------------------------------------------------------

            age_days = (
                pd.Timestamp.today()
                .normalize()
                - latest_new_date.normalize()
            ).days


            if age_days > 7:

                print(
                    'WARNUNG: '
                    'Die heruntergeladenen '
                    'BNetzA-Gasimportdaten '
                    f'enden bereits am '
                    f'{latest_new_date:%d.%m.%Y} '
                    f'({age_days} Tage alt).'
                )


            # -------------------------------------------------------------
            # Bestehenden Cache prüfen.
            #
            # Niemals eine neuere lokale Datei mit älteren Daten
            # überschreiben.
            # -------------------------------------------------------------

            existing_latest_date = None


            if os.path.exists(
                LNG_IMPORTS_CACHE
            ):

                try:

                    df_existing = pd.read_csv(
                        LNG_IMPORTS_CACHE,
                        sep='\t',
                        index_col=None
                    )


                    if not df_existing.empty:

                        existing_dates = pd.to_datetime(
                            df_existing.iloc[:, 0]
                            .astype(str)
                            .str.strip(),
                            format='%d.%m.%Y',
                            errors='coerce'
                        )


                        existing_latest_date = (
                            existing_dates.max()
                        )

                except Exception as cache_error:

                    print(
                        'WARNUNG: '
                        'Vorhandener BNetzA-Cache '
                        'konnte nicht geprüft werden:',
                        cache_error
                    )


            # -------------------------------------------------------------
            # Nur speichern, wenn Download mindestens so aktuell ist
            # wie die vorhandene Datei.
            # -------------------------------------------------------------

            should_save = (
                existing_latest_date is None
                or pd.isna(
                    existing_latest_date
                )
                or latest_new_date
                >= existing_latest_date
            )


            if should_save:

                # Datum wieder so formatieren,
                # wie es der restliche Code erwartet.
                df_ns_new[
                    'Datum'
                ] = (
                    df_ns_new[
                        'Datum'
                    ]
                    .dt.strftime(
                        '%d.%m.%Y'
                    )
                )


                df_ns_new.to_csv(
                    LNG_IMPORTS_CACHE,
                    sep='\t',
                    encoding='utf-8',
                    index=False
                )


                print(
                    'BNetzA-Gasimporte '
                    'aktualisiert bis:',
                    latest_new_date.strftime(
                        '%d.%m.%Y'
                    )
                )


            else:

                print(
                    'WARNUNG: '
                    'Der BNetzA-Download '
                    f'endet am '
                    f'{latest_new_date:%d.%m.%Y}, '
                    'die lokale Datei ist aber '
                    f'neuer '
                    f'({existing_latest_date:%d.%m.%Y}). '
                    'Lokale Datei bleibt erhalten.'
                )


        except Exception as bnetza_error:

            # -------------------------------------------------------------
            # Fehler NICHT mehr verschlucken.
            # -------------------------------------------------------------

            print()
            print(
                'WARNUNG: '
                'BNetzA-Gasimporte konnten '
                'nicht aktualisiert werden.'
            )

            print(
                'Fehler:',
                repr(
                    bnetza_error
                )
            )


            if not os.path.exists(
                LNG_IMPORTS_CACHE
            ):

                raise RuntimeError(
                    'BNetzA-Download fehlgeschlagen '
                    'und es existiert keine lokale '
                    'Fallback-Datei.'
                ) from bnetza_error


            print(
                'Verwende stattdessen '
                'die zuletzt gespeicherte Datei:',
                LNG_IMPORTS_CACHE
            )


        # ---------------------------------------------------------------------
        # Aktuelle bzw. letzte funktionierende lokale Datei laden
        # ---------------------------------------------------------------------

        df_ns = pd.read_csv(
            LNG_IMPORTS_CACHE,
            sep='\t',
            index_col=None
        )


        # =====================================================================
        # Gesamtimporte und Russland-Daten
        # =====================================================================

        df_total = df_ns.copy()


        # ---------------------------------------------------------------------
        # Nur Datum, LNG und Deutschland Import behalten
        # ---------------------------------------------------------------------

        df_total = df_total[
            [
                df_total.columns[0],
                'LNG',
                'Deutschland Import'
            ]
        ].copy()


        # ---------------------------------------------------------------------
        # Für Russland nur Datum + Russland behalten
        # ---------------------------------------------------------------------

        df_ns = df_ns[
            [
                df_ns.columns[0],
                'Russland'
            ]
        ].copy()


        # ---------------------------------------------------------------------
        # Datum konvertieren
        # ---------------------------------------------------------------------

        df_total[
            df_total.columns[0]
        ] = pd.to_datetime(
            df_total[
                df_total.columns[0]
            ]
            .astype(str)
            .str.strip(),
            format='%d.%m.%Y',
            errors='raise'
        )


        df_ns[
            df_ns.columns[0]
        ] = pd.to_datetime(
            df_ns[
                df_ns.columns[0]
            ]
            .astype(str)
            .str.strip(),
            format='%d.%m.%Y',
            errors='raise'
        )


        # ---------------------------------------------------------------------
        # Datum als Index
        # ---------------------------------------------------------------------

        df_total = df_total.set_index(
            df_total.columns[0]
        )

        df_ns = df_ns.set_index(
            df_ns.columns[0]
        )


        # ---------------------------------------------------------------------
        # GWh -> TWh
        # ---------------------------------------------------------------------

        df_total[
            [
                'LNG',
                'Deutschland Import'
            ]
        ] = (
            df_total[
                [
                    'LNG',
                    'Deutschland Import'
                ]
            ]
            .div(1000)
        )


        # ---------------------------------------------------------------------
        # Reihenfolge und Bezeichnungen für Grafik
        # ---------------------------------------------------------------------

        df_total = df_total[
            [
                'Deutschland Import',
                'LNG'
            ]
        ]


        df_total = df_total.rename(
            columns={
                'Deutschland Import':
                'Gesamt-Importe',

                'LNG':
                'Direkt-Importe LNG'
            }
        )


        # ---------------------------------------------------------------------
        # Russland:
        # GWh -> Mio. m³ bei Heizwert 10,3 kWh/m³
        # ---------------------------------------------------------------------

        df_ns = (
            df_ns
            / 10.3
        ).round(1)


        # =====================================================================
        # Dynamischer Nord-Stream-/Russland-Titel
        # =====================================================================

        if (
            df_ns[
                'Russland'
            ]
            .iloc[-1]
            > 0
        ):

            chart_title = (
                'Über Nord Stream 1 fliesst '
                'kaum noch russisches Gas'
            )

        else:

            chart_title = (
                'Über Nord Stream 1 fliesst '
                'kein russisches Gas mehr'
            )


        # =====================================================================
        # Anteil direkt importiertes LNG
        # =====================================================================

        latest_total_import = (
            df_total[
                'Gesamt-Importe'
            ]
            .iloc[-1]
        )


        latest_direct_lng = (
            df_total[
                'Direkt-Importe LNG'
            ]
            .iloc[-1]
        )


        if (
            pd.isna(
                latest_total_import
            )
            or latest_total_import == 0
            or pd.isna(
                latest_direct_lng
            )
        ):

            raise ValueError(
                'Letzter BNetzA-Wert '
                'kann nicht für den '
                'LNG-Anteil verwendet werden.'
            )


        title_twh = (
            latest_direct_lng
            / latest_total_import
            * 100
        )


        title_twh = int(
            round(
                title_twh,
                0
            )
        )


        chart_title_total = (
            'Anteil des direkt importierten '
            f'LNG liegt derzeit bei '
            f'{title_twh} Prozent'
        )


        # =====================================================================
        # Stand
        # =====================================================================

        timecode = (
            df_total.index[-1]
        )


        timecodestr = (
            timecode.strftime(
                '%-d. %-m. %Y'
            )
        )


        notes_chart_ns = (
            'Stand: '
            + timecodestr
        )


        notes_chart_total = (
            '¹ inklusive möglicher Ringflüsse '
            'und Bestellungen aus anderen Staaten.'
            '<br>Stand: '
            + timecodestr
        )


        # =====================================================================
        # Russland-Daten für Dashboard speichern
        # =====================================================================

        df_ns = df_ns.rename(
            columns={
                'nordstream1':
                'Nord Stream 1'
            }
        )


        df_ns.index = (
            df_ns.index.rename(
                'periodFrom'
            )
        )


        df_ns.to_csv(
            './data/pipelines_ns.tsv',
            sep='\t'
        )


        # =====================================================================
        # LNG-Anteil für Dashboard
        # =====================================================================

        df_dash = (
            df_total.copy()
        )


        df_dash['LNG'] = (
            df_dash[
                'Direkt-Importe LNG'
            ]
            / df_dash[
                'Gesamt-Importe'
            ]
            * 100
        )


        df_dash = df_dash[
            ['LNG']
        ]


        df_dash.index.names = [
            'Datum'
        ]


        df_dash.to_csv(
            './data/german-imports.tsv',
            sep='\t',
            encoding='utf-8'
        )


        # =====================================================================
        # Charts aktualisieren
        # =====================================================================

        update_chart(
            id='78215f05ea0a73af28c0bb1c2c89f896',
            data=df_ns,
            notes=notes_chart_ns,
            title=chart_title
        )


        update_chart(
            id='85c9e635bfeae3a127d9c9db90dfb2c5',
            data=df_total,
            notes=notes_chart_total,
            title=chart_title_total
        )


    except Exception:
        raise