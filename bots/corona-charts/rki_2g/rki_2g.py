import os
import pandas as pd
import gc
from datetime import datetime
import sys


# calculate corona rules according to RKI value
def corona_rule_given_rki(value: float) -> str:
    if value < 0:
        return("")
    elif value < 3:
        return "Teilw. 2G"
    elif value < 6:
        return "2G"
    elif value < 9:
        return "2G+"
    else:
        return "Teil-Lockdown"


# add corona rule to every RKI value
def transform_2G_data(data: pd.DataFrame, estimates: pd.Series) -> pd.DataFrame:
    corona_rules = []
    corona_rules_set = set()
    for rki_value in data['RKI-Wert']:
        rule = corona_rule_given_rki(value=rki_value)
        corona_rules.append(rule)
        corona_rules_set.add(rule)
    data['Regel¹'] = corona_rules

    country_codes = {
        'Baden-Württemberg': 'DE-BW',
        'Bayern': 'DE-BY',
        'Berlin': 'DE-BE',
        'Brandenburg': 'DE-BB',
        'Bremen': 'DE-HB',
        'Hamburg': 'DE-HH',
        'Hessen': 'DE-HE',
        'Mecklenburg-Vorpommern': 'DE-MV',
        'Niedersachsen': 'DE-NI',
        'Nordrhein-Westfalen': 'DE-NW',
        'Rheinland-Pfalz': 'DE-RP',
        'Saarland': 'DE-SL',
        'Sachsen': 'DE-SN',
        'Sachsen-Anhalt': 'DE-ST',
        'Schleswig-Holstein': 'DE-SH',
        'Thüringen': 'DE-TH'
    }

    # add Nowcast estimate to dataframe
    for index, row in data.iterrows():
        data.loc[index, 'Real²'] = estimates.loc[country_codes[index]]

    return corona_rules_set


# create options dictionary
def get_options(rules: set) -> dict:
    colors = {
        'Teilw. 2G': '#EDECE1',
        '2G': '#C6D7B8',
        '2G+': '#8BC5A0',
        'Teil-Lockdown': '#24B39C'
    }

    colorOverwrites = list()
    customCategoriesOrder = list()

    position = 1
    for rule in ['Teilw. 2G', '2G', '2G+', 'Teil-Lockdown']:
        if rule in rules:
            colorOverwrites.append({
                'textColor': 'dark',
                'color': colors[rule],
                'position': position
            })
            position += 1
            customCategoriesOrder.append({
                'category': rule
            })

    options = {
        'colorColumn': {
            'categoricalOptions': {
                'colorOverwrites': colorOverwrites,
                'customCategoriesOrder': customCategoriesOrder
            },
            'selectedColumn': 1
        }
    }
    return options


if __name__ == '__main__':
    try:
        # add parent directory to path so helpers file can be referenced
        sys.path.append(os.path.dirname((os.path.dirname(__file__))))
        from helpers import *

        # set working directory, change if necessary
        os.chdir(os.path.dirname(__file__))

        # set RKI source
        url = 'https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Hospitalisierungen_in_Deutschland/master/Aktuell_Deutschland_COVID-19-Hospitalisierungen.csv'

        # read columns needed for the chart
        dfall = pd.read_csv(url,
                            encoding='utf-8',
                            usecols=['Datum', 'Bundesland', 'Altersgruppe', '7T_Hospitalisierung_Inzidenz'])

        # RKI: select rows with states and relevant age group
        df = dfall.loc[dfall['Bundesland'] != 'Bundesgebiet']
        df = df.loc[df['Altersgruppe'].isin(['00+'])]

        # RKI: select rows with Germany and relevant age group
        dfde = dfall.loc[dfall['Bundesland'] == 'Bundesgebiet']
        dfde = dfde.loc[dfde['Altersgruppe'].isin(['00+'])]

        # delete old dataframe
        del [[dfall]]
        gc.collect()

        # drop unused columns
        df = df.drop(columns='Altersgruppe')
        dfde = dfde.drop(columns='Altersgruppe')

        # create a spreadsheet-style pivot table for rules table and line chart
        df = df.pivot_table(index=['Datum'], columns=[
                            'Bundesland'], values='7T_Hospitalisierung_Inzidenz')
        dfde = dfde.pivot_table(index=['Datum'], columns=[
                                'Bundesland'], values='7T_Hospitalisierung_Inzidenz')

        # get date for chart notes and add one day
        today = df.iloc[-1].name
        timestamp_dt = datetime.strptime(today, '%Y-%m-%d')
        timestamp_str = timestamp_dt.strftime('%-d. %-m. %Y')

        # set Nowcast source (current day)
        for i in range(1, 4):
            day = df.iloc[-i].name
            urlcast = 'https://raw.githubusercontent.com/KITmetricslab/hospitalization-nowcast-hub/main/data-processed/LMU_StaBLab-GAM_nowcast/{}-LMU_StaBLab-GAM_nowcast.csv'.format(
                day)
            try:
                # read columns needed for the chart
                dfcastall = pd.read_csv(urlcast,
                                        encoding='utf-8',
                                        usecols=['location', 'age_group', 'target_end_date', 'type', 'value'])
            except Exception:
                continue
            break

        # Nowcast: select rows with states and relevant age group
        dfcast = dfcastall.loc[dfcastall['location'] != 'DE']
        dfcast = dfcast.loc[dfcast['age_group'].isin(['00+'])]
        dfcast = dfcast.loc[dfcast['type'].isin(['mean'])]

        # Nowcast: select rows with Germany and relevant age group
        dfcastde = dfcastall.loc[dfcastall['location'] == 'DE']
        dfcastde = dfcastde.loc[dfcastde['age_group'].isin(['00+'])]
        dfcastde = dfcastde.loc[dfcastde['type'].isin(['mean'])]

        dfcast = dfcast.drop(columns=['age_group', 'type'])
        dfcastde = dfcastde.drop(columns=['location', 'age_group', 'type'])

        # create a spreadsheet-style pivot table for Nowcast table and line chart
        dfcast = dfcast.pivot_table(index=['target_end_date'], columns=[
                                    'location'], values='value')
        dfcastde = dfcastde.pivot_table(
            index=['target_end_date'], values='value')

        # Nowcast values per state from two days ago
        dfcast = dfcast.iloc[-3]

        # population data
        urlpop = 'https://raw.githubusercontent.com/KITmetricslab/hospitalization-nowcast-hub/main/nowcast_viz_de/plot_data/population_sizes.csv'
        dfpop = pd.read_csv(urlpop, encoding='utf-8',
                            usecols=['location', 'age_group', 'population'])
        dfpop = dfpop.pivot_table(index=['location'], columns=[
                                  'age_group'], values='population').iloc[:, 0]

        # calculate relative values for table and line chart
        estimates = round(dfcast/dfpop*100000, 1).iloc[1:]
        dfcastde['NZZ-Schätzung'] = round(dfcastde['value']/83138368*100000, 1)

        # create new dataframe for line chart
        datachart = dfcastde.join(dfde)
        datachart = datachart.drop(columns='value')
        datachart = datachart.rename(columns={'Bundesgebiet': 'RKI-Wert'})
        datachart.index = datachart.index.rename('')

        # remove last two from Nowcast estimate
        datachart.loc[datachart.index[-2:], 'NZZ-Schätzung'] = ''

        # use only current day
        data = pd.DataFrame({'RKI-Wert': df.iloc[-1]})

        # add corona rules to each state and extract existing corona rules as set
        corona_rules_set = transform_2G_data(data=data, estimates=estimates)

        # sort RKI values
        # data['RKI-Wert'] = round(data['RKI-Wert'], 1)
        data = data.sort_values(by=['RKI-Wert'], ascending=False)
        data = data[['Regel¹', 'RKI-Wert', 'Real²']]

        # run function
        update_chart(id='9dd87b7667e84ce621ab705db264e761', notes='¹ Bis 19. 3. sind strengere Regeln erlaubt.<br>² Schätzung der LMU München inklusive Nachmeldungen.<br><br>Stand: ' +
                     timestamp_str, data=data, options=get_options(corona_rules_set))
        update_chart(id='590776db9b66058b024b8dff27bfb8f6',
                     data=datachart, notes='Stand: ' + timestamp_str)

    except:
        raise
