import pandas as pd
import os
import re
import openpyxl

# set working directory
os.chdir(os.path.dirname(__file__))


# function for reading txt files with election platforms 1949-2021, cleaned with [^a-zA-ZßäÄöÖüÜ^ \r\n]
def getTextOfFile(fileName):
    fileObject = open(fileName, 'r', encoding='utf-8')
    text = fileObject.read()
    getVals = list([val for val in text
                    if val.isalpha() or val == ' '])
    text = ''.join(getVals)
    return text


# years and parties from txt file names (YEAR_PARTY.txt in /data)
fileNames = os.listdir('data')
years = [1949, 1953, 1957, 1961, 1965, 1969, 1972, 1976, 1980, 1983,
         1987, 1990, 1994, 1998, 2002, 2005, 2009, 2013, 2017, 2021]
parties = dict(CDU=0, SPD=0, FDP=0, GRÜNE=0, LINKE=0, AFD=0, FW=0)

# create data frames for each term/topic
character_count = pd.DataFrame(parties, index=years)
freiheit_count = pd.DataFrame(parties, index=years)
buergerrecht_count = pd.DataFrame(parties, index=years)
marktwirtschaft_count = pd.DataFrame(parties, index=years)
volk_count = pd.DataFrame(parties, index=years)
kind_count = pd.DataFrame(parties, index=years)
verantwortung_count = pd.DataFrame(parties, index=years)
klima_count = pd.DataFrame(parties, index=years)
natur_count = pd.DataFrame(parties, index=years)
umwelt_count = pd.DataFrame(parties, index=years)
oekol_count = pd.DataFrame(parties, index=years)
waldsterben_count = pd.DataFrame(parties, index=years)
ozon_count = pd.DataFrame(parties, index=years)
all_climate_count = pd.DataFrame(parties, index=years)

# load txt files into data frames
for file in fileNames:
    text = getTextOfFile('data/'+file)
    year = int(file.split('.')[0].split('_')[0])
    party = file.split('.')[0].split('_')[1].upper().replace('UE', 'Ü')
    character_count.loc[year, party] = len(text)
    freiheit_count.loc[year, party] = len(re.findall(
        r"\b[Ff]reiheit\b", text, flags=re.M))
    buergerrecht_count.loc[year, party] = len(
        re.findall(r"\b[Bb]ürger(?:[iI]nnen)?recht[a-z]{0,2}\b", text, flags=re.M))  # gender stars have already been removed in txt source
    marktwirtschaft_count.loc[year, party] = len(
        re.findall(r"\b[Mm]arktwirtschaft\b", text, flags=re.M))
    volk_count.loc[year, party] = len(
        re.findall(r"\b[Vv]olk[a-z]{0,2}\b", text, flags=re.M))
    kind_count.loc[year, party] = len(
        re.findall(r"\b[Kk]ind[a-z]{0,2}\b", text, flags=re.M))
    verantwortung_count.loc[year, party] = len(
        re.findall(r"\b[Ee]igenverantwortung\b", text, flags=re.M))
    klima_count.loc[year, party] = len(re.findall("[Kk]lima\w*", text))
    natur_count.loc[year, party] = len(re.findall("[Nn]atur\w*", text))
    umwelt_count.loc[year, party] = len(re.findall("[Uu]mwelt\w*", text))
    oekol_count.loc[year, party] = len(re.findall("[Öö]kol\w+", text))
    waldsterben_count.loc[year, party] = len(
        re.findall("[Ww]aldsterben\w*", text))
    ozon_count.loc[year, party] = len(re.findall("[Oo]zon\w*", text))

# calculate relative values (per 10.000 characters)
base = 10000
freiheit_relative = pd.DataFrame(parties, index=years)
buergerrecht_relative = pd.DataFrame(parties, index=years)
marktwirtschaft_relative = pd.DataFrame(parties, index=years)
volk_relative = pd.DataFrame(parties, index=years)
kind_relative = pd.DataFrame(parties, index=years)
verantwortung_relative = pd.DataFrame(parties, index=years)
klima_relative = pd.DataFrame(parties, index=years)
natur_relative = pd.DataFrame(parties, index=years)
umwelt_relative = pd.DataFrame(parties, index=years)
oekol_relative = pd.DataFrame(parties, index=years)
waldsterben_relative = pd.DataFrame(parties, index=years)
ozon_relative = pd.DataFrame(parties, index=years)
all_climate_relative = pd.DataFrame(parties, index=years)

for year in years:
    for party in parties:
        # aggregate climate terms
        all_climate_count.loc[year, party] = klima_count.loc[year, party] + \
            umwelt_count.loc[year, party] + natur_count.loc[year,
                                                            party] + oekol_count.loc[year, party]
        # other relative values
        freiheit_relative.loc[year, party] = freiheit_count.loc[year,
                                                                party]*base/character_count.loc[year, party]
        buergerrecht_relative.loc[year, party] = buergerrecht_count.loc[year,
                                                                        party]*base/character_count.loc[year, party]
        marktwirtschaft_relative.loc[year, party] = marktwirtschaft_count.loc[year,
                                                                              party]*base/character_count.loc[year, party]
        buergerrecht_relative.loc[year, party] = buergerrecht_count.loc[year,
                                                                        party]*base/character_count.loc[year, party]
        volk_relative.loc[year, party] = volk_count.loc[year,
                                                        party]*base/character_count.loc[year, party]
        kind_relative.loc[year, party] = kind_count.loc[year,
                                                        party]*base/character_count.loc[year, party]
        verantwortung_relative.loc[year, party] = verantwortung_count.loc[year,
                                                                          party]*base/character_count.loc[year, party]
        klima_relative.loc[year, party] = klima_count.loc[year,
                                                          party]*base/character_count.loc[year, party]
        umwelt_relative.loc[year, party] = umwelt_count.loc[year,
                                                            party]*base/character_count.loc[year, party]
        natur_relative.loc[year, party] = natur_count.loc[year,
                                                          party]*base/character_count.loc[year, party]
        oekol_relative.loc[year, party] = oekol_count.loc[year,
                                                          party]*base/character_count.loc[year, party]
        waldsterben_relative.loc[year, party] = waldsterben_count.loc[year,
                                                                      party]*base/character_count.loc[year, party]
        ozon_relative.loc[year, party] = ozon_count.loc[year,
                                                        party]*base/character_count.loc[year, party]
        all_climate_relative.loc[year, party] = all_climate_count.loc[year,
                                                                      party]*base/character_count.loc[year, party]

# save results to excel file
writer = pd.ExcelWriter('result.xlsx', engine='openpyxl')
freiheit_count.to_excel(writer, sheet_name='freiheit')
freiheit_relative.to_excel(writer, sheet_name='freiheit_rel')
buergerrecht_count.to_excel(writer, sheet_name='bürgerrecht')
buergerrecht_relative.to_excel(writer, sheet_name='bürgerrecht_rel')
marktwirtschaft_count.to_excel(writer, sheet_name='marktw')
marktwirtschaft_relative.to_excel(writer, sheet_name='marktw_rel')
volk_count.to_excel(writer, sheet_name='volk')
volk_relative.to_excel(writer, sheet_name='volk_rel')
kind_count.to_excel(writer, sheet_name='kind')
kind_relative.to_excel(writer, sheet_name='kind_rel')
verantwortung_count.to_excel(writer, sheet_name='eigenvw')
verantwortung_relative.to_excel(writer, sheet_name='eigenvw_rel')
buergerrecht_count.to_excel(writer, sheet_name='bürgerrecht')
buergerrecht_relative.to_excel(writer, sheet_name='bürgerrecht_rel')
klima_count.to_excel(writer, sheet_name='bürgerrecht')
klima_relative.to_excel(writer, sheet_name='bürgerrecht_rel')
natur_count.to_excel(writer, sheet_name='natur')
natur_relative.to_excel(writer, sheet_name='natur_rel')
umwelt_count.to_excel(writer, sheet_name='umwelt')
umwelt_relative.to_excel(writer, sheet_name='umwelt_rel')
oekol_count.to_excel(writer, sheet_name='ökol')
oekol_relative.to_excel(writer, sheet_name='ökol_rel')
all_climate_count.to_excel(writer, sheet_name='klima_alles')
all_climate_relative.to_excel(writer, sheet_name='klima_alles_rel')
waldsterben_count.to_excel(writer, sheet_name='waldsterben')
waldsterben_relative.to_excel(writer, sheet_name='waldsterben_rel')
ozon_count.to_excel(writer, sheet_name='ozon')
ozon_relative.to_excel(writer, sheet_name='ozon_rel')
writer.save()
