import pandas as pd
import numpy as np
import os
import csv
from io import StringIO
import json
import re
from scipy.ndimage import uniform_filter1d
import requests
from datawrapper import Datawrapper
import time

# === Helper Functions ===

def convert_percentage_to_float(value):
    if pd.isna(value):
        return np.nan
    value_str = str(value)  # Ensure the input is a string
    p_strings = re.findall(r"\d+,\d", value_str)
    if len(p_strings) == 0:
        p_strings = re.findall(r"\d+", value_str)
    p_floats = [float(s.replace(",", ".")) for s in p_strings]
    return sum(p_floats) if "-" not in value_str else sum(p_floats) / 2

def convert_befragte(str):
    if str == "Bundestagswahl" or "?" in str:
        return np.NaN
    s = str
    to_replace = ".~≈>"
    for r in to_replace:
        s = s.replace(r, "")
    s = re.findall(r"\d+", s)[0]
    return int(s)

months = {
    "Jan": 1,
    "Feb": 2,
    "Mrz": 3,
    "Apr": 4,
    "Mai": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Okt": 10,
    "Nov": 11,
    "Dez": 12
}

def convert_weird_date_to_date(str):
    if bool(re.match(r"\w{3}.? \d{4}", str)):
        return f"15.{months[str[:3]]}.{str[-4:]}"
    else:
        return str
    
def update_chart(id, title="", subtitle="", notes="", data="", parties="", possibleCoalitions="", assetGroups="", options=""):  # Q helper function
    # read qConfig file
    json_file = open("./q.config.json")
    qConfig = json.load(json_file)
    # update chart properties
    for item in qConfig.get("items"):
        for environment in item.get("environments"):
            if environment.get("id") == id:
                if title != "":
                    item.get("item").update({"title": title})
                if subtitle != "":
                    item.get("item").update({"subtitle": subtitle})
                if notes != "":
                    item.get("item").update({"notes": notes})
                if len(data) > 0:
                    # reset_index() and T (for transpose) are used to bring column names into the first row
                    transformed_data = data.applymap(str).reset_index(
                        drop=False).T.reset_index().T.apply(list, axis=1).to_list()
                    if 'table' in item.get('item').get('data'):
                        item.get('item').get('data').update(
                            {'table': transformed_data})
                    else:
                        item.get('item').update({'data': transformed_data})
                if len(parties) > 0:
                    item["item"]["parties"] = parties
                if len(possibleCoalitions) > 0:
                    item["item"]["possibleCoalitions"] = possibleCoalitions
                if len(assetGroups) > 0:
                    item["item"]["assetGroups"] = assetGroups
                print("Successfully updated item with id", id,
                      "on", environment.get("name"), "environment")
                if options != "":
                    item.get("item").update({"options": options})

    # write qConfig file
    with open("./q.config.json", "w", encoding="utf-8") as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False,
                  indent=1, default=str)
    json_file.close()

def fetch_html_table(url, max_retries=5, pause=1):
    for attempt in range(max_retries):
        try:
            # Attempt to read the HTML table
            table = pd.read_html(url)
            # If successful, return the table
            return table
        except Exception as e:
            print(f"Attempt {attempt + 1} of {max_retries} failed for URL {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(pause)  # Pause before retrying
            else:
                print(f"Failed to fetch HTML table from {url} after {max_retries} attempts. Aborting script.")
                exit(1)  # Exit the script with error status

# Datawrapper API key
dw_key = os.environ["DATAWRAPPER_API"]
dw = Datawrapper(access_token=dw_key)
dw_id = "IWzhE"
dw_id_weidel = "hDqW6"
dw_id_table = "G0FzZ"

# Set the working directory
os.chdir(os.path.dirname(__file__))

with open("urls.csv") as f:
    reader = csv.DictReader(f)
    urls = [d for d in reader]

all_data = []

for row in urls:
    institut = row["Institut"]
    region = row["Region"]
    url = row["url"]
    table = fetch_html_table(url)
    data = table[1]

    # Find the index where the table ends
    m = data[data["Sonstige"] == "Sonstige"].index.to_numpy()[0]
    l = len(data) - m

    # Remove the last l rows
    data.drop(
        index=data.tail(l).index,
        axis=0,
        inplace=True
    )

    # Drop empty columns
    data.dropna(
        how="all",
        axis=1,
        inplace=True
    )

    # Rename the first column
    data.rename(
        columns={
            "Unnamed: 0": "Datum"
        },
        inplace=True
    )

    # Extract "BSW" percentage from "Sonstige" for "GMS" polls
    if institut == "GMS" and "Sonstige" in data.columns:
        def extract_bsw(sonstige):
            match = re.search(r"BSW (\d+)(,(\d+))?", str(sonstige))
            if match:
                return float(match.group(1) + "." + (match.group(3) if match.group(3) else "0"))
            return np.nan

        data["BSW"] = data["Sonstige"].apply(extract_bsw)
        data["Sonstige"] = data["Sonstige"].apply(lambda x: re.sub(r"BSW \d+(,\d+)? %?", "", str(x)).strip())

    # Extract party names and variable columns
    parteinamen = [x for x in data.columns if x not in ["Datum", "Befragte", "Zeitraum"]]
    variablen = [x for x in data.columns if x not in parteinamen]

    # Fill empty results with "-"
    for partei in parteinamen:
        data[partei] = data[partei].fillna("-")

    # Melt the table
    data = pd.melt(
        data,
        id_vars=variablen,
        value_vars=parteinamen,
        var_name="Partei",
        value_name="Ergebnis"
    )

    # Remove entries without a clear date
    data["Datum"] = data["Datum"].fillna("..")
    data.Datum = data.Datum.apply(
        lambda x: ".." if "?" in x else x.strip("*")
    )

    # Hardcoded special cases
    data.Datum = data.Datum.apply(
        lambda x: "27.09.1998" if x == "Wahl 1998" else x
    )
    if institut == "INSA / YouGov":
        data.drop(data[data["Datum"] == "02.02.2017"].index, inplace=True)

    # Convert weird date formats
    data.Datum = data.Datum.apply(convert_weird_date_to_date)

    # Create Day, Month, Year columns
    datum_split = data.Datum.str.split(".", expand=True)
    data["Tag"] = pd.to_numeric(datum_split[0])
    data["Monat"] = pd.to_numeric(datum_split[1])
    data["Jahr"] = pd.to_numeric(datum_split[2])
    data.drop(
        columns=["Datum"],
        axis=1,
        inplace=True
    )

    # Convert percentage strings to floats
    data.Ergebnis = data.Ergebnis.apply(convert_percentage_to_float)

    # Add Befragte column if it doesn't exist
    if "Befragte" not in data:
        data["Befragte"] = np.NaN

    # Distinguish between surveys and elections
    data["Art"] = data.Befragte.apply(
        lambda x: "Wahl" if x == "Bundestagswahl" else "Umfrage"
    )
    # Convert Befragte numbers to ints
    data.Befragte = data.Befragte.astype("string")
    data["Befragte"] = data["Befragte"].fillna("?")
    data.Befragte = data.Befragte.apply(convert_befragte)

    # Add Zeitraum column if it doesn't exist
    if "Zeitraum" not in data:
        data["Zeitraum"] = np.NaN

    # Remove "Bundestagswahl" from Zeitraum
    data.Zeitraum = data.Zeitraum.apply(
        lambda x: np.NaN if x == "Bundestagswahl" else x
    )

    # Add Region and Institut columns
    data["Region"] = region
    data["Institut"] = institut

    # Remove entries without date or Zeitraum
    data.dropna(
        subset=["Tag", "Monat", "Jahr", "Zeitraum"],
        how="all",
        inplace=True
    )

    # Backfill missing years
    data["Jahr"] = data["Jahr"].bfill()

    # Fill available days and months from Zeitraum
    if not data.Zeitraum.isnull().all():
        data["Tag"] = data["Tag"].fillna(pd.to_numeric(data["Zeitraum"].str[-6:-4], errors="coerce"))
        data["Monat"] = data["Monat"].fillna(pd.to_numeric(data["Zeitraum"].str[-3:-1], errors="coerce"))

    # Convert day, month, and year to integers
    data.Tag = data.Tag.astype("int")
    data.Monat = data.Monat.astype("int")
    data.Jahr = data.Jahr.astype("int")

    all_data.append(data)

# Combine all data into one DataFrame
complete_data = pd.concat(all_data).reset_index(drop=True)

# Remove duplicates for elections
complete_data.drop_duplicates(
    subset=["Tag", "Monat", "Jahr", "Partei", "Art", "Institut"],
    inplace=True
)

# Create Datum column
complete_data["Datum"] = pd.to_datetime(
    dict(year=complete_data.Jahr, month=complete_data.Monat, day=complete_data.Tag),
    errors="coerce"
)

# === Start cleaning for charts ===

# Adjust desired_parties to include 'Übrige' and 'BSW'
desired_parties = ['Union', 'SPD', 'Grüne', 'FDP', 'Linke', 'AfD', 'Übrige', 'BSW']

# Exclude 'FW', 'Nichtwähler/ Unentschl.', and 'PIRATEN'
filtered_data = complete_data[~complete_data["Partei"].isin(["FW", "Nichtwähler/ Unentschl.", "PIRATEN"])].copy()

# Map party names
filtered_data['Partei'] = filtered_data['Partei'].replace({
    'CDU/CSU': 'Union',
    'GRÜNE': 'Grüne',
    'LINKE': 'Linke',
    'Sonstige': 'Übrige'
})

# Optional: Print unique party names to verify
print("Available parties after mapping:", filtered_data['Partei'].unique())

# Keep only desired parties
filtered_data = filtered_data[filtered_data['Partei'].isin(desired_parties)].copy()

# Filter data
cutoff_date = pd.to_datetime("2019-01-01")
filtered_data = filtered_data[filtered_data["Datum"] > cutoff_date]

# Convert 'Ergebnis' and 'Befragte' to numeric
filtered_data['Ergebnis'] = pd.to_numeric(filtered_data['Ergebnis'], errors='coerce')
filtered_data['Befragte'] = pd.to_numeric(filtered_data['Befragte'], errors='coerce')

# === Create the Latest Polls Table ===

# Format party colors
party_colors = {
    "Union": "#0a0a0a",
    "AfD": "#0084c7",
    "SPD": "#c31906",
    "Grüne": "#66a622",
    "BSW": "#da467d",
    "FDP": "#d1cc00",
    "Linke": "#8440a3"
}

# Format the party column headers
formatted_columns = {party: f'<span style="color:{party_colors[party]}">{party}</span>' for party in party_colors}

# Pivot the filtered_data to wide format
wide_polls_table = filtered_data.pivot_table(
    index=["Institut", "Datum", "Zeitraum", "Befragte"],
    columns="Partei",
    values="Ergebnis",
    aggfunc="last"
).reset_index()

# Convert "Befragte" to string with the thin white space character and add "Teiln."
wide_polls_table["Befragte"] = wide_polls_table["Befragte"].apply(
    lambda x: f'{int(x):,}'.replace(",", " ") + " Teiln." if pd.notna(x) else ""
)

# Sort by publication date (Datum) descending
wide_polls_table.sort_values(by="Datum", ascending=False, inplace=True)

# Keep only the 300 most recent polls
wide_polls_table = wide_polls_table.head(75)

# Create the formatted "Institut" column
wide_polls_table["Institut"] = (
    wide_polls_table["Institut"] + "<br>" +
    '<span style="font-size: x-small; color: #69696c">' +
    wide_polls_table["Zeitraum"].fillna("") + "<br>" +
    wide_polls_table["Befragte"] + "</span>"
)

# Keep only relevant columns (formatted parties + Institut)
wide_polls_table = wide_polls_table[["Institut"] + list(party_colors.keys())]

"""
# OLD DATAWRAPPER TABLE Format percentages with thin spaces for integers and commas for floats, and wrap in HTML tags
for party in party_colors.keys():
    if party in wide_polls_table.columns:
        wide_polls_table[party] = wide_polls_table[party].apply(
            lambda x: (
                f'<span style="font-weight:500">{int(x):,}'.replace(",", " ") + "%</span>"
                if pd.notna(x) and x != 0 and x.is_integer()
                else f'<span style="font-weight:500">{x:.1f}'.replace(".", ",") + "%</span>"
                if pd.notna(x) and x != 0
                else ""
            )
        )
    else:
        wide_polls_table[party] = ""  # Ensure missing parties have empty columns
"""
# Format percentages with thin spaces for integers and commas for floats, and colorize according to party colors
for party, color in party_colors.items():
    if party in wide_polls_table.columns:
        wide_polls_table[party] = wide_polls_table[party].apply(
            lambda x: (
                f'<span style="color:{color}">{int(x):,}'.replace(",", " ") + "%</span>"
                if pd.notna(x) and x != 0 and x.is_integer()
                else f'<span style="color:{color}">{x:.1f}'.replace(".", ",") + "%</span>"
                if pd.notna(x) and x != 0
                else ""
            )
        )
    else:
        wide_polls_table[party] = ""  # Ensure missing parties have empty columns

# Rename columns with formatted party headers
wide_polls_table.rename(columns={"Institut": "Institut", **formatted_columns}, inplace=True)

# Rename columns with formatted party headers
wide_polls_table.rename(columns={"Institut": "Institut", **formatted_columns}, inplace=True)

# --- Compute data_pivot and average_data for individual institutes ---

# Pivot the data to have parties as columns
data_pivot = filtered_data.pivot_table(
    index=['Institut', 'Datum'],
    columns='Partei',
    values='Ergebnis'
).reset_index()

# Map institute names to desired abbreviations
institute_mapping = {
    'Insa': 'insa',
    'FG Wahl.': 'fgw',
    'Forsa': 'forsa',
    'Verian': 'emnid',
    'Allensb.': 'allensbach',
    'GMS': 'gms',
    'Infratest': 'infratest',
    'YouGov': 'yougov',
    'average': 'average'
}

# Apply the mapping to the 'Institut' column in data_pivot
data_pivot['Institut'] = data_pivot['Institut'].replace(institute_mapping)

# Round percentages to one decimal place
data_pivot[desired_parties] = data_pivot[desired_parties].round(1)

# --- Proceed with the line chart calculations ---

# === Calculate Rolling Average ===

# Group by 'Datum' and 'Partei' and calculate mean 'Ergebnis' per date per party
daily_party_means = filtered_data.groupby(['Datum', 'Partei'])['Ergebnis'].mean().reset_index()

# Sort by 'Partei' and 'Datum'
daily_party_means.sort_values(by=['Partei', 'Datum'], inplace=True)

# OLD Compute rolling average with window=10
# daily_party_means['Ergebnis_RA'] = daily_party_means.groupby('Partei', group_keys=False)['Ergebnis'].rolling(window=10, min_periods=1).mean().reset_index(level=0, drop=True)

# Calculate Exponentially Weighted Moving Average (EWMA)
daily_party_means['Ergebnis_RA'] = daily_party_means.groupby('Partei', group_keys=False)['Ergebnis']\
    .apply(lambda x: x.ewm(span=10, adjust=False).mean())

# Round 'Ergebnis_RA' to one decimal place
daily_party_means['Ergebnis_RA'] = daily_party_means['Ergebnis_RA'].round(1)

# Replace NaN with None for JSON serialization
daily_party_means['Ergebnis_RA'] = daily_party_means['Ergebnis_RA'].where(pd.notnull(daily_party_means['Ergebnis_RA']), None)

# Pivot the data to have 'Datum' as index, 'Partei' as columns, 'Ergebnis_RA' as values
data_pivot_ra = daily_party_means.pivot(index='Datum', columns='Partei', values='Ergebnis_RA').reset_index()

# Add 'Institut' column with value 'average'
data_pivot_ra['Institut'] = 'average'

# Combine data_pivot (individual institutes) and data_pivot_ra (rolling averages)
# First, prepare data_pivot for merging

# Rename 'Institut' to 'institute' and 'Datum' to 'date'
data_pivot.rename(columns={'Institut': 'institute', 'Datum': 'date'}, inplace=True)
data_pivot_ra.rename(columns={'Institut': 'institute', 'Datum': 'date'}, inplace=True)

# Convert 'date' to string in 'YYYY-MM-DD' format in both DataFrames
data_pivot['date'] = pd.to_datetime(data_pivot['date']).dt.strftime('%Y-%m-%d')
data_pivot_ra['date'] = pd.to_datetime(data_pivot_ra['date']).dt.strftime('%Y-%m-%d')

# Reorder columns to match desired_parties
data_pivot = data_pivot[['institute', 'date'] + desired_parties]
data_pivot_ra = data_pivot_ra[['institute', 'date'] + desired_parties]

# Concatenate the DataFrames
full_line_chart_data = pd.concat([data_pivot, data_pivot_ra], ignore_index=True)

# Sort the data by date and institute
full_line_chart_data.sort_values(by=['date', 'institute'], inplace=True)

# Replace NaN values with 0.0
full_line_chart_data.fillna(0.0, inplace=True)

# Convert the DataFrame to a list of dictionaries for JSON output
json_data = full_line_chart_data.to_dict(orient='records')

# Save the data in a JSON file
with open('./data/lineChart.json', 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=1)

print("JSON file 'lineChart.json' has been created successfully.")

# --- Proceed with projection chart and coalition seats calculations ---

# === Compute Margin of Error Based on Respondents ===

# Remove entries with missing 'Ergebnis' or 'Befragte'
filtered_data_nonan = filtered_data.dropna(subset=['Ergebnis', 'Befragte']).copy()

# Define eligible voters size N in 2021 with underscores for readability (update for 2025)
N = 60_400_000

# Compute proportions and standard error
p = filtered_data_nonan['Ergebnis'] / 100
n = filtered_data_nonan['Befragte']

# Handle cases where n is zero to avoid division errors
n = n.replace(0, np.nan)

# Standard error calculation
se = np.sqrt(p * (1 - p) / n) * np.sqrt((N - n) / (N - 1))

# Calculate 95% confidence interval
filtered_data_nonan['ci'] = 1.96 * se * 100

# This won't work with Pandas 3
"""
# For each party, take the last 30 entries (sorted by 'Datum')
def get_last_n_entries(group, n=30):
    group = group.sort_values('Datum', ascending=True).tail(n)
    return group

last_n_data = (
    filtered_data_nonan.groupby("Partei", group_keys=False)
    .apply(get_last_n_entries, n=30)
    .reset_index(drop=True)
)

# For each party, compute mean 'ci'
mean_ci_per_party = last_n_data.groupby('Partei')['ci'].mean().reset_index()
mean_ci_per_party.rename(columns={'ci': 'mean_ci'}, inplace=True)
"""

# For each party, take the last 30 entries (sorted by 'Datum')
last_n_data = filtered_data_nonan.sort_values("Datum").groupby("Partei").tail(30)

# For each party, compute mean 'ci'
mean_ci_per_party = (
    last_n_data.groupby("Partei", as_index=False)["ci"].mean()
    .rename(columns={"ci": "mean_ci"})
)

# moe formula derived from https://goodcalculators.com/margin-of-error-calculator/
# population size (german eligible voters) derived from https://www.bundeswahlleiter.de/info/presse/mitteilungen/bundestagswahl-2021/01_21_wahlberechtigte-geschaetzt.html

# === Projection Chart ===

# Use the latest rolling averages for the projection chart
# Get the latest date
latest_date = daily_party_means['Datum'].max()

# Get the latest rolling averages for each party
latest_rolling_averages = daily_party_means[daily_party_means['Datum'] == latest_date][['Partei', 'Ergebnis_RA']]
latest_rolling_averages.rename(columns={'Ergebnis_RA': 'average'}, inplace=True)

# Merge 'mean_ci_per_party' with 'latest_rolling_averages'
projection_data = pd.merge(latest_rolling_averages, mean_ci_per_party, on='Partei', how='left')

# Compute upper and lower bounds
projection_data['upperBound'] = projection_data['average'] + projection_data['mean_ci']
projection_data['lowerBound'] = projection_data['average'] - projection_data['mean_ci']

# Create last election results DataFrame, manually update with last election
last_election_results = pd.DataFrame({
    'party': desired_parties,
    'lastElection': [24.1, 25.7, 14.8, 11.5, 4.9, 10.3, 8.7, 0.0]
})

# Add last election results
last_election_results.rename(columns={'party': 'Partei'}, inplace=True)
projection_data = pd.merge(projection_data, last_election_results, on='Partei', how='left')

# Rename 'Partei' back to 'party'
projection_data.rename(columns={'Partei': 'party'}, inplace=True)

# Select relevant columns
projection_data = projection_data[['party', 'lastElection', 'lowerBound', 'average', 'upperBound']]

# Exclude 'Übrige' from the projection data
projection_data = projection_data[projection_data['party'] != 'Übrige']

# Round values
projection_data[['lowerBound', 'average', 'upperBound']] = projection_data[['lowerBound', 'average', 'upperBound']].round(4)

# Write to JSON
projection_chart_data = projection_data.to_dict(orient='records')

with open('./data/projectionChart.json', 'w', encoding='utf-8') as f:
    json.dump(projection_chart_data, f, ensure_ascii=False, indent=1)

print("JSON file 'projectionChart.json' has been created successfully.")

# === Coalition Seats Calculation ===

# Map party names to color codes and Q IDs
party_metadata = {
    "Union": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909830-658639605", "colorCode": "#0a0a0a"},
    "SPD": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909830-820461104", "colorCode": "#c31906"},
    "Grüne": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909830-681841949", "colorCode": "#66a622"},
    "FDP": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909831-568178765", "colorCode": "#d1cc00"},
    "Linke": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909831-21531609", "colorCode": "#8440a3"},
    "AfD": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909831-211145954", "colorCode": "#0084c7"},
    "BSW": {"id": "0d50b45e538faa45f768d3204450d0e7-1732637074764-908994801", "colorCode": "#da467d"}
}

# Use the latest rolling averages for coalition calculations
coalition_data = latest_rolling_averages[(latest_rolling_averages['Partei'] != 'Übrige') & 
                                         (latest_rolling_averages['average'] >= 5)].copy()

# Compute value_5pct
value_sum = coalition_data['average'].sum()
coalition_data['value_5pct'] = 100 * coalition_data['average'] / value_sum

# Compute seats projected to 630 seats
total_seats = 630  # Maximum allowed seats
coalition_data['seats'] = (coalition_data['value_5pct'] * total_seats / 100).round(0).astype(int)

# Adjust the seats to ensure the total matches total_seats
seats_difference = total_seats - coalition_data['seats'].sum()
if seats_difference != 0:
    # Sort by fractional part of seat allocation to decide which party to adjust
    coalition_data['fraction'] = coalition_data['value_5pct'] * total_seats / 100 - coalition_data['seats']
    coalition_data = coalition_data.sort_values(by='fraction', ascending=(seats_difference < 0))
    
    # Adjust seats one by one
    for i in range(abs(seats_difference)):
        idx = coalition_data.index[i % len(coalition_data)]
        coalition_data.at[idx, 'seats'] += int(np.sign(seats_difference))
    
    # Drop the 'fraction' column after adjustment
    coalition_data = coalition_data.drop(columns=['fraction'])

# Generate the coalitionSeats as a list of dictionaries
coalitionSeats = []

# Add parties with >= 5% and their calculated seats
for _, row in coalition_data.iterrows():
    party_name = row['Partei']
    if party_name in party_metadata:
        coalitionSeats.append({
            "id": party_metadata[party_name]["id"],
            "color": {"colorCode": party_metadata[party_name]["colorCode"]},
            "name": party_name,
            "seats": int(row['seats'])
        })

# Add parties with <5% and assign 0 seats
for party_name, metadata in party_metadata.items():
    if party_name not in coalition_data['Partei'].values:
        coalitionSeats.append({
            "id": metadata["id"],
            "color": {"colorCode": metadata["colorCode"]},
            "name": party_name,
            "seats": 0
        })

# Check for the presence of FDP and BSW in the coalition_data
has_fdp = "FDP" in coalition_data['Partei'].values and coalition_data.loc[coalition_data['Partei'] == "FDP", 'seats'].iloc[0] > 0
has_bsw = "BSW" in coalition_data['Partei'].values and coalition_data.loc[coalition_data['Partei'] == "BSW", 'seats'].iloc[0] > 0

# Determine the file to load based on the conditions
if not has_fdp and not has_bsw:
    coalition_file = "./data/coalitions_nofdp_nobsw.json"
elif not has_fdp and has_bsw:
    coalition_file = "./data/coalitions_nofdp.json"
elif has_fdp and not has_bsw:
    coalition_file = "./data/coalitions_nobsw.json"
elif has_fdp and has_bsw:
    coalition_file = "./data/coalitions_fdp_bsw.json"

# Load the selected JSON file into a variable
with open(coalition_file, 'r', encoding='utf-8') as f:
    coalition_set = json.load(f)

print(f"Loaded coalition file: {coalition_file}")

def convert_befragtenzahl(value):
    """
    Convert 'Befragtenzahl\nNo. of respondents' values to numeric,
    handling cases like '791+545' by performing addition.
    """
    if pd.isna(value):
        return np.nan
    value = str(value).strip()
    if "+" in value:
        parts = re.findall(r"\d+", value)
        return sum(map(int, parts))
    elif value.isdigit():
        return int(value)
    return np.nan

def fetch_kanzlerkandidat_data(candidate_names):
    # Define the URL for the Google Sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1aT2f8yc8p9-XjOqFCTQ1nDeP5GEORu9QZDOtUwF8smI/export?format=csv&gid=1579897364"

    # Retry logic
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Attempt to fetch the data
            response = requests.get(sheet_url)
            response.raise_for_status()  # Raise an error for HTTP issues
            csv_data = response.content.decode("utf-8")
            break  # Successfully fetched data, break out of the retry loop
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} of {max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Pause for 1 second before retrying
            else:
                print("Failed to fetch Google Sheet data after 5 attempts. Aborting script.")
                exit(1)  # Exit the script with error status

    # Read the CSV data into a DataFrame
    df = pd.read_csv(StringIO(csv_data), skiprows=5)  # Skip metadata rows
    df = df.reset_index(drop=True)

    # Rename the first row as the header if it contains column names
    header_row = df.iloc[0]
    if header_row.isnull().sum() < len(header_row) / 2:  # Heuristic: Mostly non-null
        df.columns = header_row
        df = df[1:].reset_index(drop=True)

    # Ensure consistent column naming
    df.columns = [str(col).strip() for col in df.columns]

    # Drop the first row after the header as it contains irrelevant data
    df = df.iloc[1:].reset_index(drop=True)

    # Rename and clean up the date column
    if "Datum" not in df.columns:
        df = df.rename(columns={df.columns[0]: "Datum"})
    
    # Ensure the "Institut" column exists, rename dynamically if needed
    if "Institut" not in df.columns:
        potential_institut_column = next((col for col in df.columns if "Institut" in col), None)
        if potential_institut_column:
            df = df.rename(columns={potential_institut_column: "Institut"})
        else:
            raise ValueError("The 'Institut' column is missing and could not be identified.")

    # Handle 'Befragtenzahl\nNo. of respondents' column
    if "Befragtenzahl\nNo. of respondents" in df.columns:
        df["Befragtenzahl"] = df["Befragtenzahl\nNo. of respondents"].apply(convert_befragtenzahl)
    else:
        df["Befragtenzahl"] = np.nan

    # Forward-fill missing dates and institute names
    df["Datum"] = df["Datum"].ffill()
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    df["Institut"] = df["Institut"].ffill()

    # Drop everything below the date "19.07.2022" (new header appears afterwards with other candidates)
    cutoff_date = pd.to_datetime("19.07.2022", format="%d.%m.%Y")
    df = df[df["Datum"] >= cutoff_date]

    # Dynamically find relevant candidate columns
    candidate_columns = {}
    for candidate in candidate_names:
        matched_column = next((col for col in df.columns if candidate in str(col)), None)
        if matched_column:
            candidate_columns[candidate] = matched_column

    if not candidate_columns:
        raise ValueError("No matching candidate columns found in the dataset.")

    # List of columns to clean, including candidates and exclusion columns
    columns_to_clean = list(candidate_columns.values()) + ["Wagenknecht", "Weidel", "Pistorius", "Söder", "Wüst", "Baerbock"]
    columns_to_clean = [col for col in columns_to_clean if col in df.columns]  # Ensure these columns exist

    # Replace "—" with NaN and clean up numeric columns
    for col in columns_to_clean:
        df[col] = df[col].replace("—", np.nan).str.replace("%", "").str.strip()

    # Exclude polls with non-NaN values in the specified exclusion columns
    excluded_columns = ["Wagenknecht", "Weidel", "Pistorius", "Söder", "Wüst", "Baerbock"]
    excluded_columns_in_df = [col for col in excluded_columns if col in df.columns]  # Ensure these columns exist

    if excluded_columns_in_df:  # Proceed if excluded columns exist in the DataFrame
        df = df[df[excluded_columns_in_df].isna().all(axis=1)]  # Keep rows where all excluded columns are NaN

    # Ensure that rows with all key candidates present are retained
    key_candidates = ["Scholz", "Habeck", "Merz"]
    key_columns = [candidate_columns[c] for c in key_candidates if c in candidate_columns]

    # Drop rows where any of the key candidates has no valid value
    df = df.dropna(subset=key_columns, how="any")  # Drop if any key candidate value is missing

    # Create a new DataFrame for output
    output = pd.DataFrame()
    output["Datum"] = df["Datum"]

    # Add 'Befragtenzahl' column to output
    output["Befragtenzahl"] = df["Befragtenzahl"]

    # Process each candidate's data
    for candidate, column in candidate_columns.items():
        # Convert to numeric and ignore invalid rows
        output[candidate] = pd.to_numeric(df[column], errors="coerce")

        # Add a column to indicate real poll data for this candidate
        output[f"{candidate}_real"] = output[candidate]

    return output

# Define the candidate names to include in the analysis, optional: include Weidel
candidate_names = ["Merz", "Habeck", "Scholz"]

# Fetch and process the data
kanzlerkandidat_data = fetch_kanzlerkandidat_data(candidate_names)

# Calculate weighted averages by "Befragtenzahl" for each candidate
weighted_data = []
for candidate in candidate_names:
    # Filter for non-NaN values in the candidate's column
    valid_data = kanzlerkandidat_data.loc[kanzlerkandidat_data[candidate].notna()]

    # Replace NaN values in 'Befragtenzahl' with a default value (2500)
    valid_data["Befragtenzahl"] = valid_data["Befragtenzahl"].fillna(2500)

    # Group by 'Datum' and compute the weighted average
    weighted_avg = (
        valid_data
        .groupby("Datum", as_index=False)[[candidate, "Befragtenzahl"]]
        .apply(lambda g: pd.Series({
            candidate: np.sum(g[candidate] * g["Befragtenzahl"]) / np.sum(g["Befragtenzahl"])
        }))
    )
    
    # Preserve real poll data
    weighted_avg[f"{candidate}_real"] = valid_data.groupby("Datum")[candidate].first().reset_index(drop=True)
    weighted_data.append(weighted_avg)

# Merge weighted averages for all candidates
weighted_kanzlerkandidat_data = pd.DataFrame({"Datum": kanzlerkandidat_data["Datum"].unique()})
for weighted_avg in weighted_data:
    weighted_kanzlerkandidat_data = weighted_kanzlerkandidat_data.merge(weighted_avg, on="Datum", how="left")

# Replace the main DataFrame with weighted results
kanzlerkandidat_data = weighted_kanzlerkandidat_data

# Generate a complete range of dates from the minimum to the maximum
date_range = pd.date_range(
    start=kanzlerkandidat_data["Datum"].min(),
    end=kanzlerkandidat_data["Datum"].max(),
    freq="D"  # Daily frequency
)

# Reindex the DataFrame to include all dates in the range
kanzlerkandidat_data = kanzlerkandidat_data.set_index("Datum").reindex(date_range)

# Reset the index and rename it to "Datum"
kanzlerkandidat_data = kanzlerkandidat_data.reset_index().rename(columns={"index": "Datum"})

# Interpolate missing values linearly for candidate columns
kanzlerkandidat_data[candidate_names] = kanzlerkandidat_data[candidate_names].interpolate(method="linear")

# Apply EWMA for smoothing and weighting more recent polls higher
for candidate in candidate_names:
    kanzlerkandidat_data[candidate] = (
        kanzlerkandidat_data[candidate]
        .rolling(window=10, min_periods=1, center=True)
        .mean()
    )

# Add two new columns with 0 at the earliest date and NaN for the rest
kanzlerkandidat_data["Punkte: einzelne Umfragen"] = np.nan
kanzlerkandidat_data["Linie: Durchschnitt"] = np.nan

# Drop the 'Befragtenzahl' column if it exists
if "Befragtenzahl" in kanzlerkandidat_data.columns:
    kanzlerkandidat_data.drop(columns=["Befragtenzahl"], inplace=True)

# Set the value 0 at the earliest date
earliest_date_index = kanzlerkandidat_data["Datum"].idxmin()
kanzlerkandidat_data.at[earliest_date_index, "Punkte: einzelne Umfragen"] = 0
kanzlerkandidat_data.at[earliest_date_index, "Linie: Durchschnitt"] = 0

kanzlerkandidat_data_all = kanzlerkandidat_data.copy()

# === SAME AS ABOVE BUT WITH WEIDEL ===

def fetch_kanzlerkandidat_data(candidate_names):
    # Define the URL for the Google Sheet
    sheet_url = "https://docs.google.com/spreadsheets/d/1aT2f8yc8p9-XjOqFCTQ1nDeP5GEORu9QZDOtUwF8smI/export?format=csv&gid=1579897364"

    # Retry logic
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Attempt to fetch the data
            response = requests.get(sheet_url)
            response.raise_for_status()  # Raise an error for HTTP issues
            csv_data = response.content.decode("utf-8")
            break  # Successfully fetched data, break out of the retry loop
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} of {max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Pause for 1 second before retrying
            else:
                print("Failed to fetch Google Sheet data after 5 attempts. Aborting script.")
                exit(1)  # Exit the script with error status

    # Read the CSV data into a DataFrame
    df = pd.read_csv(StringIO(csv_data), skiprows=5)  # Skip metadata rows
    df = df.reset_index(drop=True)

    # Rename the first row as the header if it contains column names
    header_row = df.iloc[0]
    if header_row.isnull().sum() < len(header_row) / 2:  # Heuristic: Mostly non-null
        df.columns = header_row
        df = df[1:].reset_index(drop=True)

    # Ensure consistent column naming
    df.columns = [str(col).strip() for col in df.columns]

    # Drop the first row after the header as it contains irrelevant data
    df = df.iloc[1:].reset_index(drop=True)

    # Rename and clean up the date column
    if "Datum" not in df.columns:
        df = df.rename(columns={df.columns[0]: "Datum"})
    
    # Ensure the "Institut" column exists, rename dynamically if needed
    if "Institut" not in df.columns:
        potential_institut_column = next((col for col in df.columns if "Institut" in col), None)
        if potential_institut_column:
            df = df.rename(columns={potential_institut_column: "Institut"})
        else:
            raise ValueError("The 'Institut' column is missing and could not be identified.")

    # Handle 'Befragtenzahl\nNo. of respondents' column
    if "Befragtenzahl\nNo. of respondents" in df.columns:
        df["Befragtenzahl"] = df["Befragtenzahl\nNo. of respondents"].apply(convert_befragtenzahl)
    else:
        df["Befragtenzahl"] = np.nan

    # Forward-fill missing dates and institute names
    df["Datum"] = df["Datum"].ffill()
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    df["Institut"] = df["Institut"].ffill()

    # Drop everything below the date "19.07.2022" (new header appears afterwards with other candidates)
    cutoff_date = pd.to_datetime("19.07.2022", format="%d.%m.%Y")
    df = df[df["Datum"] >= cutoff_date]

    # Dynamically find relevant candidate columns
    candidate_columns = {}
    for candidate in candidate_names:
        matched_column = next((col for col in df.columns if candidate in str(col)), None)
        if matched_column:
            candidate_columns[candidate] = matched_column

    if not candidate_columns:
        raise ValueError("No matching candidate columns found in the dataset.")

    # List of columns to clean, including candidates and exclusion columns
    exclusion_candidates = ["Wagenknecht", "Pistorius", "Söder", "Wüst", "Baerbock"]
    columns_to_clean = list(candidate_columns.values()) + exclusion_candidates
    columns_to_clean = [col for col in columns_to_clean if col in df.columns]  # Ensure these columns exist

    # Replace "—" with NaN and clean up numeric columns
    for col in columns_to_clean:
        df[col] = (
            df[col].astype(str)
            .replace("nan", "")
            .replace("—", np.nan)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")  # Convert back to numeric

    # Ensure that rows with all key candidates present are retained
    key_candidates = ["Scholz", "Habeck", "Merz", "Weidel"]
    key_columns = [candidate_columns[c] for c in key_candidates if c in candidate_columns]
    df = df.dropna(subset=key_columns, how="any")

    # Exclude polls with non-NaN values in exclusion columns
    exclusion_columns = [col for col in exclusion_candidates if col in df.columns]
    if exclusion_columns:
        df = df[df[exclusion_columns].isna().all(axis=1)]

    # Create a new DataFrame for output
    output = pd.DataFrame()
    output["Datum"] = df["Datum"]

    # Add 'Befragtenzahl' column to output
    output["Befragtenzahl"] = df["Befragtenzahl"]

    # Process each candidate's data
    for candidate, column in candidate_columns.items():
        output[candidate] = pd.to_numeric(df[column], errors="coerce")
        output[f"{candidate}_real"] = output[candidate]

    return output

# Define the candidate names to include in the analysis
candidate_names = ["Merz", "Habeck", "Scholz", "Weidel"]

# Fetch and process the data
kanzlerkandidat_data = fetch_kanzlerkandidat_data(candidate_names)

# Create a new DataFrame for the weighted data to store the weighted averages
weighted_kanzlerkandidat_data = pd.DataFrame({"Datum": kanzlerkandidat_data["Datum"].unique()})

# Add the real data (e.g., 'Merz_real', 'Habeck_real', etc.)
for candidate in candidate_names:
    weighted_kanzlerkandidat_data[f"{candidate}_real"] = kanzlerkandidat_data[f"{candidate}_real"]

# Calculate weighted averages by "Befragtenzahl" for each candidate
for candidate in candidate_names:
    # Filter for non-NaN values in the candidate's column
    valid_data = kanzlerkandidat_data.loc[kanzlerkandidat_data[candidate].notna()]
    
    # Group by 'Datum' and compute the weighted average
    weighted_avg = (
        valid_data
        .groupby("Datum", as_index=False)[[candidate, "Befragtenzahl"]]
        .apply(lambda g: pd.Series({
            candidate: np.sum(g[candidate] * g["Befragtenzahl"].fillna(1)) / np.sum(g["Befragtenzahl"].fillna(1))
        }))
    )
    
    # Merge the weighted averages into the DataFrame
    weighted_kanzlerkandidat_data = weighted_kanzlerkandidat_data.merge(weighted_avg[["Datum", candidate]], on="Datum", how="left")

# Reset the index and rename columns as needed
weighted_kanzlerkandidat_data = weighted_kanzlerkandidat_data.set_index("Datum")

# Add the 'Punkte: einzelne Umfragen' and 'Linie: Durchschnitt' columns with NaN initially
weighted_kanzlerkandidat_data["Punkte: einzelne Umfragen"] = np.nan
weighted_kanzlerkandidat_data["Linie: Durchschnitt"] = np.nan

# Define the new cutoff date
new_cutoff_date = pd.to_datetime("2024-10-16", format="%Y-%m-%d")

# Set the value 0 after the second cut-off
first_valid_index_after_cutoff = weighted_kanzlerkandidat_data.index[weighted_kanzlerkandidat_data.index >= new_cutoff_date].min()
weighted_kanzlerkandidat_data.at[first_valid_index_after_cutoff, "Punkte: einzelne Umfragen"] = 0
weighted_kanzlerkandidat_data.at[first_valid_index_after_cutoff, "Linie: Durchschnitt"] = 0

# Filter the data to include only rows from the new cutoff date onward
weighted_kanzlerkandidat_data = weighted_kanzlerkandidat_data[weighted_kanzlerkandidat_data.index >= new_cutoff_date].reset_index(drop=True)

# Generate a complete range of dates from the minimum to the maximum
date_range = pd.date_range(
    start=kanzlerkandidat_data["Datum"].min(),
    end=kanzlerkandidat_data["Datum"].max(),
    freq="D"  # Daily frequency
)

# Drop duplicates based on "Datum" before reindexing
kanzlerkandidat_data = kanzlerkandidat_data.drop_duplicates(subset=["Datum"])

# Now, set "Datum" as the index and reindex
kanzlerkandidat_data = kanzlerkandidat_data.set_index("Datum").reindex(date_range)

# Reset the index and rename it to "Datum"
kanzlerkandidat_data = kanzlerkandidat_data.reset_index().rename(columns={"index": "Datum"})

# Interpolate missing values linearly for candidate columns
kanzlerkandidat_data[candidate_names] = kanzlerkandidat_data[candidate_names].interpolate(method="linear")

# Apply EWMA for smoothing and weighting recent polls higher
for candidate in candidate_names:
    kanzlerkandidat_data[candidate] = (
        kanzlerkandidat_data[candidate]
        .ewm(span=10, adjust=False)  # Span adjusts the weighting; smaller = more weight on recent data
        .mean()
    )

# Add two new columns with NaN initially
kanzlerkandidat_data["Punkte: einzelne Umfragen"] = np.nan
kanzlerkandidat_data["Linie: Durchschnitt"] = np.nan

# Define the new cutoff date
new_cutoff_date = pd.to_datetime("2024-10-16", format="%Y-%m-%d")

# Set the value 0 after the second cut-off
first_valid_index_after_cutoff = kanzlerkandidat_data.index[kanzlerkandidat_data["Datum"] >= new_cutoff_date].min()
kanzlerkandidat_data.at[first_valid_index_after_cutoff, "Punkte: einzelne Umfragen"] = 0
kanzlerkandidat_data.at[first_valid_index_after_cutoff, "Linie: Durchschnitt"] = 0

# Filter the data to include only rows from the new cutoff date onward
kanzlerkandidat_data = kanzlerkandidat_data[kanzlerkandidat_data["Datum"] >= new_cutoff_date].reset_index(drop=True)

# Drop the 'Befragtenzahl' column if it exists
if "Befragtenzahl" in kanzlerkandidat_data.columns:
    kanzlerkandidat_data.drop(columns=["Befragtenzahl"], inplace=True)

def adjust_consecutive_dates(df, column):
    """
    Adjust consecutive dates where there is a value in the specified column 
    to ensure the latter date matches the earlier one due to Datawrapper limitations.
    """
    for i in range(1, len(df)):
        # Check for consecutive dates and non-null values in the specified column
        if (
            (df.loc[i, "Datum"] - df.loc[i - 1, "Datum"]).days == 1
            and not pd.isna(df.loc[i, column])
            and not pd.isna(df.loc[i - 1, column])
        ):
            # Adjust the current date to match the previous date
            df.loc[i, "Datum"] = df.loc[i - 1, "Datum"]
    return df
# Adjust dates in kanzlerkandidat_data
kanzlerkandidat_data = adjust_consecutive_dates(kanzlerkandidat_data, "Merz_real")
# Adjust dates in kanzlerkandidat_data_all
kanzlerkandidat_data_all = adjust_consecutive_dates(kanzlerkandidat_data_all, "Merz_real")
# Ensure there are no duplicate rows after the adjustment
kanzlerkandidat_data = kanzlerkandidat_data.drop_duplicates(subset=["Datum", "Merz_real"])
kanzlerkandidat_data_all = kanzlerkandidat_data_all.drop_duplicates(subset=["Datum", "Merz_real"])

kanzlerkandidat_data.to_clipboard()

# prepare data for q.config.json
assets = [
            {
                "name": "jsonFiles",
                "assets": [
                    {
                        "path": "./data/lineChart.json"
                    },
                    {
                        "path": "./data/projectionChart.json"
                    }
                ]
            }
        ]

# create dates for chart notes
timecode_all = kanzlerkandidat_data_all["Datum"].iloc[-1]
timecode = kanzlerkandidat_data["Datum"].iloc[-1]
full_line_chart_data["date"] = pd.to_datetime(full_line_chart_data["date"])
timecode_line = full_line_chart_data["date"].iloc[-1]
timecode_str_all = timecode_all.strftime("%-d. %-m. %Y")
timecode_str = timecode.strftime("%-d. %-m. %Y")
timecode_str_line = timecode_line.strftime("%-d. %-m. %Y")
notes_chart_line = "Stand: " + timecode_str_line

# update Kanzlerfragen chart #1
dw_chart = dw.add_data(chart_id=dw_id, data=kanzlerkandidat_data_all)
date = {"annotate": {
    "notes": f"Stand: {timecode_str_all}"}}
dw.update_metadata(chart_id=dw_id, metadata=date)
dw.update_description(chart_id=dw_id, source_name="@Wahlen_DE, eigene Berechnungen", intro="So würden die Befragten bei einer Direktwahl des Kanzlers abstimmen")
dw.publish_chart(chart_id=dw_id, display=False)

# update Kanzlerfragen chart #2
dw_chart = dw.add_data(chart_id=dw_id_weidel, data=kanzlerkandidat_data)
date = {"annotate": {
    "notes": f"Stand: {timecode_str}"}}
dw.update_metadata(chart_id=dw_id_weidel, metadata=date)
dw.update_description(chart_id=dw_id_weidel, source_name="@Wahlen_DE, eigene Berechnungen", intro="So würden die Befragten bei einer Direktwahl des Kanzlers abstimmen, würde auch Alice Weidel zur Wahl stehen")
dw.publish_chart(chart_id=dw_id_weidel, display=False)

"""
# OLD update table
dw_table = dw.add_data(chart_id=dw_id_table, data=wide_polls_table)
dw.update_description(chart_id=dw_id_table, source_name="Wahlrecht.de", intro="So würden die Befragten wählen, wenn am Sonntag Bundestagswahl wäre")
dw.publish_chart(chart_id=dw_id_table, display=False)
"""

# run Q function for poll table
wide_polls_table.set_index("Institut", inplace=True)
update_chart(id="94c15a6eadd659eb977086455eb67467",data=wide_polls_table, notes=notes_chart_line)

# run Q function for main custom code chart
update_chart(id="ef14d4bef9f51a1c17bc9cb6e2f8a8d0",assetGroups=assets)

# run Q function for coalition chart
update_chart(id="0d50b45e538faa45f768d3204450d0e7",parties=coalitionSeats, possibleCoalitions=coalition_set, notes=notes_chart_line)
