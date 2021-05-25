import pandas as pd
import webbrowser
from requests import head
from urllib.error import URLError, HTTPError
from datetime import datetime

# read xlsx file (needs openpyxl)
def read_xslx(name):
    df = pd.read_excel(name, sheet_name=0, header=7, index_col=1)

    # remove unnamed columns
    return df.loc[:, ~df.columns.str.contains('^Unnamed')]

if __name__ == '__main__':
    try:
        # check if FG Wahlen renamed the files again
        r = head('https://www.forschungsgruppe.de/Umfragen/Politbarometer/Langzeitentwicklung_-_Themen_im_Ueberblick/Politik_II/9_Probleme_1.xlsx')
        status = r.status_code
        if status == 200:
            url1 = 'https://www.forschungsgruppe.de/Umfragen/Politbarometer/Langzeitentwicklung_-_Themen_im_Ueberblick/Politik_II/9_Probleme_1.xlsx'
            url2 = 'https://www.forschungsgruppe.de/Umfragen/Politbarometer/Langzeitentwicklung_-_Themen_im_Ueberblick/Politik_II/10_Probleme_2.xlsx'
        else:
            url1 = 'https://www.forschungsgruppe.de/Umfragen/Politbarometer/Langzeitentwicklung_-_Themen_im_Ueberblick/Politik_II/9_Probleme_1_1.xlsx'
            url2 = 'https://www.forschungsgruppe.de/Umfragen/Politbarometer/Langzeitentwicklung_-_Themen_im_Ueberblick/Politik_II/10_Probleme_2_2.xlsx'

        # create df for both polls and merge them
        df1 = read_xslx(url1)
        df2 = read_xslx(url2)
        df = pd.merge(df1, df2, left_index=True, right_index=True)

        # rename columns
        df.columns = [
            "Bildung",
            "Rente",
            "Migration",
            "Klima",
            "Soziale Ungleichheit",
            "Corona",
            "Politikverdruss ",
            "Gesundheit",
            "Arbeitslosigkeit",
            "Wirtschaft",
            "Rechte / AfD",
            "Wohnen",
        ]

        # only polls since the last election in 2017
        df = df.loc[datetime(year=2017, month=9, day=15) :]

        # ~6 month moving average (window=10) and max value for each "wichtiges Problem"
        # update only necessary if there's a whole new "wichtiges Problem" (very unlikely)
        max_mov_avg = df.rolling(window=10).mean().max()

        # 6 most relevant "wichtige Probleme" within that period
        cols = max_mov_avg.sort_values(ascending=False).head(6).index.tolist()
        df = df.filter(items=cols)

        # reverse order of columns (=brighter colors in Q for lines closer to the x-axis)
        cols = df.columns.tolist()
        cols = cols[::-1]
        df = df[cols]

        # change date format
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d').strftime('%d.%m.%Y')

        ################################
        # check if update is necessary #
        ################################
        print('Latest poll from: ', df.index[-1])

        # show most important "wichtige Probleme" (sorted in ascending order)
        print(list(df))

        # copy df to clipboard
        df.to_clipboard()
        webbrowser.open(
            'https://q.st.nzz.ch/editor/chart/85d9b6089d1f589138b24ed33008184e',
            new=0,
            autoraise=True,
        )

        # save as excel file if clipboard is not available
        # now = datetime.now().strftime('%Y-%m-%d')
        # df.to_excel(excel_writer= './'   now   '-german-problems.xlsx')

    except HTTPError as e:
        print('HTTP error:', e.reason)
    except URLError as e:
        print('Did the URL change?', e.reason)