import pandas as pd
import numpy as np
import os
import csv
from io import StringIO
import json
import re
import requests
from datawrapper import Datawrapper
import time

# ============================================================
# README (manuelle Einstellungen)
# ============================================================
# Koalitionen (Templates werden pro Lauf automatisch erzeugt)
#
# 1) Varianten-Parteien (rein/raus):
#    - COALITION_VARIANT_PARTIES: Für diese Parteien gibt es Koalitions-Varianten-Dateien.
#      Beispiel: ["FDP","BSW","Linke"] erzeugt bis zu 2^3 Dateien:
#      coalitions.json, coalitions_fdp.json, coalitions_bsw.json, coalitions_fdp_bsw.json, ...
#      Geladen wird die Variante, die zum Basisszenario (Sitze > 0) passt.
#
# 2) Koalitions-Prioritäten:
#    - COALITIONS_SPEC: Liste der Koalitionen in gewünschter Reihenfolge.
#      Jede Koalition ist: {"name": "...", "parties": ["Union","SPD", ...]}
#
# 3) Ausgabeordner:
#    - COALITION_TEMPLATES_DIR: Hierhin werden die coalitions*.json geschrieben.
# ============================================================

COALITION_TEMPLATES_DIR = "./data"
COALITION_VARIANT_PARTIES = ["FDP", "BSW", "Linke"]

# Koalitionen in gewünschter Reihenfolge (Beispiel; hier nach Bedarf pflegen)
COALITIONS_SPEC = [
    {"name": "", "parties": ["Union", "SPD"]},
    {"name": "", "parties": ["Union", "Grüne"]},
    {"name": "", "parties": ["Union", "FDP"]},
    {"name": "", "parties": ["Union", "AfD"]},
    {"name": "", "parties": ["SPD", "Grüne"]},
    {"name": "", "parties": ["SPD", "Grüne", "Linke"]},
    {"name": "", "parties": ["SPD", "Grüne", "Linke", "BSW"]},
    {"name": "", "parties": ["SPD", "Grüne", "BSW"]},
    {"name": "", "parties": ["SPD", "Grüne", "FDP"]},
]

# Optional: Untervarianten unterdrücken, wenn eine "erweiterte" Variante existiert.
# Beispiel: SPD+Grüne nur anzeigen, wenn keine der Varianten mit Linke/BSW existiert.
COALITION_DEDUPE_BASES = [
    ["SPD", "Grüne"],
]

SWITCH_PARTIES = COALITION_VARIANT_PARTIES

def write_coalition_templates(data_dir: str = COALITION_TEMPLATES_DIR):
    """Schreibt coalitions*.json aus COALITIONS_SPEC (in definierter Reihenfolge).

    Pro Kombination der Varianten-Parteien wird eine Datei erzeugt.
    Eine Koalition wird nur dann in eine Variante geschrieben, wenn keine fehlende Varianten-Partei
    in der Koalition vorkommt.
    """
    os.makedirs(data_dir, exist_ok=True)

    from itertools import combinations

    switch = [p for p in SWITCH_PARTIES if p in party_metadata]

    # map party name -> id
    name_to_id = {name: meta["id"] for name, meta in party_metadata.items()}

    scenarios = []
    for r in range(0, len(switch) + 1):
        for comb in combinations(switch, r):
            scenarios.append(set(comb))

    for present_set in scenarios:
        suffix = "_" + "_".join(sorted([p.lower() for p in present_set])) if present_set else ""
        out_path = os.path.join(data_dir, f"coalitions{suffix}.json")

        out = []
        for c in COALITIONS_SPEC:
            parties = c.get("parties", [])
            if not parties:
                continue

            # Koalitionen überspringen, wenn eine Varianten-Partei fehlt
            if any((p in switch and p not in present_set) for p in parties):
                continue

            ids = []
            ok = True
            for p in parties:
                pid = name_to_id.get(p)
                if not pid:
                    ok = False
                    break
                ids.append({"id": pid})
            if not ok:
                continue

            out.append({"name": c.get("name", ""), "parties": ids})

        # Dedupe: Basiskoalitionen unterdrücken, wenn eine erweiterte Variante in derselben Datei existiert
        if COALITION_DEDUPE_BASES and out:
            # Build name-sets for each coalition
            # (COALITIONS_SPEC and out match in order and count, but out may be filtered by present_set)
            # So, we need to reconstruct the party name set for each out entry from ids.
            # Attach name sets to out entries for pruning
            out2 = []
            for entry in out:
                # reconstruct names from ids
                ids_here = [p.get("id") for p in entry.get("parties", []) if isinstance(p, dict)]
                names_here = []
                for nm, meta in party_metadata.items():
                    if meta.get("id") in ids_here:
                        names_here.append(nm)
                entry2 = dict(entry)
                entry2["_names"] = names_here
                out2.append(entry2)

            # Compute drop indices
            dedupe_bases = [set(x) for x in COALITION_DEDUPE_BASES]
            drop_idx = set()
            name_sets = [set(e.get("_names", [])) for e in out2]
            for i, si in enumerate(name_sets):
                if si in dedupe_bases:
                    for j, sj in enumerate(name_sets):
                        if i == j:
                            continue
                        if si < sj:
                            # Only prune if extras are variant parties present in this scenario
                            extra = sj - si
                            # Only consider extra parties that are in switch and present_set
                            if extra and all((e in switch and e in present_set) for e in extra):
                                drop_idx.add(i)
                                break
            if drop_idx:
                out2 = [e for k, e in enumerate(out2) if k not in drop_idx]
            # Remove helper field
            out = []
            for e in out2:
                e.pop("_names", None)
                out.append(e)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

# === Helper Functions ===

def convert_percentage_to_float(value):
    """Parse percentage-like cells from wahlrecht.de tables.

    - '', '-', '—', '–', '..' -> NaN (NOT 0)
    - ranges like '2-4' or '2,0–4,0' -> midpoint
    - single values -> float
    """
    if pd.isna(value):
        return np.nan

    s = str(value).strip()
    s_lower = s.lower()

    # Censored / not explicitly reported (e.g. "<3", "≤3", "unter 3") -> treat as missing value
    if "<" in s or "≤" in s or "unter" in s_lower:
        return np.nan

    if s in {"", "-", "—", "–", ".."}:
        return np.nan

    # normalize unicode dashes
    s = s.replace("–", "-").replace("—", "-")

    nums = re.findall(r"\d+(?:,\d+)?", s)
    if not nums:
        return np.nan

    vals = [float(x.replace(",", ".")) for x in nums]

    if "-" in s and len(vals) >= 2:
        return (vals[0] + vals[1]) / 2

    return vals[0]

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

# Helper: parse end of fieldwork period from Zeitraum (for trend weighting)
def parse_fieldwork_end_date(zeitraum, pub_date):
    """Parse the last day of the fieldwork period from `Zeitraum` and return a Timestamp.

    Expects patterns like '23.02.–26.02.' or '23.2.–26.2.' (often without year).
    Uses the year from `pub_date` as default; if pub_date is Jan and end month is Dec, assumes previous year.
    Returns NaT if parsing fails.
    """
    if pd.isna(zeitraum) or pd.isna(pub_date):
        return pd.NaT

    s = str(zeitraum).replace("\xa0", " ").strip()
    # Match 'dd.mm.–dd.mm.' / 'd.m.-d.m.'
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.?\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.?", s)
    if not m:
        return pd.NaT

    end_day = int(m.group(3))
    end_month = int(m.group(4))
    pub_dt = pd.to_datetime(pub_date)
    year = int(pub_dt.year)
    if int(pub_dt.month) == 1 and end_month == 12:
        year -= 1

    try:
        return pd.Timestamp(year=year, month=end_month, day=end_day)
    except Exception:
        return pd.NaT
    
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
                    transformed_data = data.astype(str).reset_index(
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

# Datawrapper API key (optional; keep script runnable even if not set)
dw_key = os.getenv("DATAWRAPPER_API")
dw = Datawrapper(access_token=dw_key) if dw_key else None
dw_id = "IWzhE"
dw_id_weidel = "hDqW6"
dw_id_table = "G0FzZ"

# Set the working directory
os.chdir(os.path.dirname(__file__))
# Ensure output directory exists (GitHub Actions runner starts from a clean workspace)
os.makedirs("./data", exist_ok=True)

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
    
    """
    # Extract "BSW" percentage from "Sonstige" for "GMS" polls (NO LONGER NEEDED DUE TO NEW BSW COLUMN)
    if institut == "GMS" and "Sonstige" in data.columns:
        def extract_bsw(sonstige):
            match = re.search(r"BSW (\d+)(,(\d+))?", str(sonstige))
            if match:
                return float(match.group(1) + "." + (match.group(3) if match.group(3) else "0"))
            return np.nan

        data["BSW"] = data["Sonstige"].apply(extract_bsw)
        data["Sonstige"] = data["Sonstige"].apply(lambda x: re.sub(r"BSW \d+(,\d+)? %?", "", str(x)).strip())
    """

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

    # Preserve raw cell values and flag whether a party was explicitly reported (numeric) in that poll
    data["Ergebnis_raw"] = data["Ergebnis"]

    def _is_reported_cell(x):
        if pd.isna(x):
            return False
        s = str(x).strip()
        s_lower = s.lower()
        # Censored / not explicitly reported
        if "<" in s or "≤" in s or "unter" in s_lower:
            return False
        if s in {"", "-", "—", "–", ".."}:
            return False
        return bool(re.search(r"\d", s))

    data["reported"] = data["Ergebnis_raw"].apply(_is_reported_cell)

    # Convert percentage strings to floats (unreported cells become NaN)
    data["Ergebnis"] = data["Ergebnis_raw"].apply(convert_percentage_to_float)

    # Remove entries without a clear date
    data["Datum"] = data["Datum"].fillna("..")
    data.Datum = data.Datum.apply(
        lambda x: ".." if "?" in x else x.strip("*")
    )

    # Hardcoded special cases
    data.Datum = data.Datum.apply(
        lambda x: "27.09.1998" if x == "Wahl 1998" else x
    )
    data.drop(data[data["Datum"] == "23.02.2025"].index, inplace=True) # DROP ELECTION DATE
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

    # Propagate the publication date (Datum) to all party rows of the same poll
    # so that every row keeps the correct release day, month and year.
    # Forward‑fill takes the date from the first row in a poll block and copies it down.
    data[["Tag", "Monat", "Jahr"]] = data[["Tag", "Monat", "Jahr"]].ffill()

    # As a safety net, if any component is still missing (very rare for older polls),
    # back‑fill remaining gaps from below.
    data[["Tag", "Monat", "Jahr"]] = data[["Tag", "Monat", "Jahr"]].bfill()

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
# desired_parties = ['Union', 'SPD', 'Grüne', 'FDP', 'Linke', 'AfD', 'Übrige', 'BSW'] # 2021
desired_parties = ['Union', 'AfD', 'SPD', 'Grüne', 'Linke', 'BSW', 'FDP', 'Übrige']

# Exclude 'FW', 'Nichtwähler/ Unentschl.', and 'PIRATEN'
filtered_data = complete_data[~complete_data["Partei"].isin(["FW", "Nichtwähler/ Unentschl.", "PIRATEN"])].copy()

# Map party names
filtered_data['Partei'] = filtered_data['Partei'].replace({
    'CDU/CSU': 'Union',
    'GRÜNE': 'Grüne',
    'LINKE': 'Linke',
    'Sonstige': 'Übrige'
})


# Keep only desired parties
filtered_data = filtered_data[filtered_data['Partei'].isin(desired_parties)].copy()

# Filter data
cutoff_date = pd.to_datetime("2021-07-12")
filtered_data = filtered_data[filtered_data["Datum"] > cutoff_date]

# Convert 'Ergebnis' and 'Befragte' to numeric
filtered_data['Ergebnis'] = pd.to_numeric(filtered_data['Ergebnis'], errors='coerce')
filtered_data['Befragte'] = pd.to_numeric(filtered_data['Befragte'], errors='coerce')

# Effective date for weighting: use end of fieldwork period when available, otherwise publication date
filtered_data["effective_date"] = filtered_data.apply(
    lambda r: parse_fieldwork_end_date(r.get("Zeitraum"), r.get("Datum")), axis=1
)
filtered_data["effective_date"] = filtered_data["effective_date"].where(
    filtered_data["effective_date"].notna(), filtered_data["Datum"]
)

# === Create the Latest Polls Table ===

# Format party colors
party_colors = {
    "Union": "#0a0a0a",
    "AfD": "#0084c7",
    "SPD": "#c31906",
    "Grüne": "#66a622",
    "BSW": "#da467d",
    "FDP": "#F3B030",
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
wide_polls_table = wide_polls_table.head(300)

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
    # 'YouGov': 'yougov',
    'average': 'average'
}

# Apply the mapping to the 'Institut' column in data_pivot
data_pivot['Institut'] = data_pivot['Institut'].replace(institute_mapping)

# Round percentages to one decimal place
data_pivot[desired_parties] = data_pivot[desired_parties].round(1)

# --- Proceed with the line chart calculations ---

# === Calculate Rolling Average (robust, responsive, handles censored "Sonstige") ===

# Parameters (simple + explainable)
HALF_LIFE_DAYS = 10.0  # polls from 10 days ago count only half as much
U_CENSORED = 3.0       # "not reported" means: value is below the display threshold (<3%)
U_CENSORED_EXPECTED = 2.0  # plausibler Erwartungswert unterhalb der Schwelle (zieht zensierte Werte Richtung ~2%)

#
# Build observations from polls; weight by end of fieldwork period (effective_date)
obs = filtered_data[["effective_date", "Partei", "Ergebnis", "Befragte", "reported"]].copy()
obs.rename(columns={"effective_date": "Datum"}, inplace=True)
obs["Befragte"] = pd.to_numeric(obs["Befragte"], errors="coerce")

fallback_n = float(np.nanmedian(obs["Befragte"])) if pd.notna(np.nanmedian(obs["Befragte"])) else 2000.0
obs["w"] = np.sqrt(obs["Befragte"].fillna(fallback_n).clip(lower=200.0))

# Aggregate per day & party (pandas 2.x/3.x safe):
# - if at least one institute reports a numeric value: weighted mean of reported values
# - otherwise (poll day but not reported): mark as censored
rep = obs["reported"] & obs["Ergebnis"].notna()

reported_only = obs.loc[rep, ["Datum", "Partei", "Ergebnis", "w"]].copy()
if len(reported_only) > 0:
    reported_only["wx"] = reported_only["Ergebnis"] * reported_only["w"]
    rep_sum = reported_only.groupby(["Datum", "Partei"], as_index=False).agg(
        w_sum=("w", "sum"),
        wx_sum=("wx", "sum")
    )
    rep_sum["Ergebnis_obs"] = rep_sum["wx_sum"] / rep_sum["w_sum"]
    rep_sum = rep_sum[["Datum", "Partei", "Ergebnis_obs"]]
else:
    rep_sum = pd.DataFrame(columns=["Datum", "Partei", "Ergebnis_obs"])

poll_count = obs.groupby(["Datum", "Partei"], as_index=False).size().rename(columns={"size": "poll_count"})

state = poll_count.merge(rep_sum, on=["Datum", "Partei"], how="left")
state["censored"] = state["Ergebnis_obs"].isna()

poll_dates = pd.Index(sorted(state["Datum"].dropna().unique()))

obs_wide = state.pivot(index="Datum", columns="Partei", values="Ergebnis_obs").reindex(poll_dates)
cen_wide = state.pivot(index="Datum", columns="Partei", values="censored").reindex(poll_dates)
cnt_wide = state.pivot(index="Datum", columns="Partei", values="poll_count").reindex(poll_dates)

# Ensure all desired parties exist as columns
for pty in desired_parties:
    if pty not in obs_wide.columns:
        obs_wide[pty] = np.nan
    if pty not in cen_wide.columns:
        cen_wide[pty] = False
    if pty not in cnt_wide.columns:
        cnt_wide[pty] = 0

obs_wide = obs_wide[desired_parties]
cen_wide = cen_wide[desired_parties].astype("boolean").fillna(False)
cnt_wide = cnt_wide[desired_parties].astype("Int64").fillna(0).astype(int)

# Time-based exponential smoothing with half-life
k = np.log(2.0) / HALF_LIFE_DAYS
trend_wide = pd.DataFrame(index=poll_dates, columns=desired_parties, dtype="float")
trend_wide.index.name = "Datum"

for pty in desired_parties:
    x = obs_wide[pty]
    cens = cen_wide[pty]
    cnt = cnt_wide[pty]

    # Start the trend only once the party is explicitly reported (numeric).
    # Purely censored observations before the first reported value do NOT initialize the series.
    reported_mask = (cnt > 0) & (~cens) & x.notna()
    first_reported_date = x.index[reported_mask].min() if reported_mask.any() else None

    s = []
    last = np.nan
    last_date = None

    for dt in poll_dates:
        poll_today = cnt.loc[dt] > 0

        # initialization: stay missing until first reported value exists
        if pd.isna(last):
            if first_reported_date is None or dt < first_reported_date:
                s.append(np.nan)
                continue
            if dt == first_reported_date:
                last = float(x.loc[dt])
                last_date = dt
                s.append(last)
                continue
            # safety net (should not happen)
            s.append(np.nan)
            continue

        # elapsed days since last update point
        delta_days = (dt - last_date).days
        if delta_days < 1:
            delta_days = 1
        alpha = 1.0 - np.exp(-k * delta_days)

        # Determine today's input
        if not poll_today:
            current_input = last  # no new information
        else:
            if (not cens.loc[dt]) and pd.notna(x.loc[dt]):
                current_input = float(x.loc[dt])
            else:
                # censored / "not reported": treat as left-censored (<U).
                # If the trend is above U, pull it down to U. If it is already below U,
                # shrink it gently towards a plausible sub-threshold value (~2%) to avoid
                # artificially keeping rarely-reported small parties near 3%.
                if last > U_CENSORED:
                    current_input = float(U_CENSORED)
                else:
                    current_input = float(min(last, U_CENSORED_EXPECTED))

        # Update trend
        last = last + alpha * (current_input - last)
        last_date = dt
        s.append(last)

    trend_wide[pty] = s

# Long format for downstream usage
# (this replaces the old event-based EWMA series)
daily_party_means = trend_wide.reset_index().melt(
    id_vars=["Datum"],
    value_vars=desired_parties,
    var_name="Partei",
    value_name="Ergebnis_RA"
)

daily_party_means["Ergebnis_RA"] = daily_party_means["Ergebnis_RA"].round(1)

# === Build lineChart.json (institute lines + average line) ===

# Rename for export (guarded to avoid double-renaming)
if "Institut" in data_pivot.columns:
    data_pivot.rename(columns={"Institut": "institute"}, inplace=True)
if "Datum" in data_pivot.columns:
    data_pivot.rename(columns={"Datum": "date"}, inplace=True)

# Ensure party columns exist in the institute table
for pty in desired_parties:
    if pty not in data_pivot.columns:
        data_pivot[pty] = np.nan

# Average line from trend
avg_line = trend_wide.reset_index().rename(columns={"Datum": "date"})
avg_line["institute"] = "average"

# Convert dates to strings
avg_line["date"] = pd.to_datetime(avg_line["date"]).dt.strftime("%Y-%m-%d")
data_pivot["date"] = pd.to_datetime(data_pivot["date"]).dt.strftime("%Y-%m-%d")

# Reorder columns
inst_lines = data_pivot[["institute", "date"] + desired_parties]
avg_line = avg_line[["institute", "date"] + desired_parties]

# Concatenate and serialize
full_line_chart_data = pd.concat([inst_lines, avg_line], ignore_index=True)
full_line_chart_data.sort_values(by=["date", "institute"], inplace=True)

# Keep missing values as null in JSON (strict JSON: no NaN)
# NOTE: `.where(..., None)` keeps NaN in float columns; `.replace({np.nan: None})` forces proper nulls.
full_line_chart_data = full_line_chart_data.replace({np.nan: None})
json_data = full_line_chart_data.to_dict(orient="records")

with open("./data/lineChart.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=1, allow_nan=False)

print("JSON file 'lineChart.json' has been created successfully.")

# --- Proceed with projection chart and coalition seats calculations ---

# === Compute Margin of Error Based on Respondents ===

# Remove entries with missing 'Ergebnis' or 'Befragte'
filtered_data_nonan = filtered_data.dropna(subset=['Ergebnis', 'Befragte']).copy()

# Define eligible voters size N in 2021 with underscores for readability (update for 2025)
N = 60_510_631

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
# population size (german eligible voters) derived from https://www.destatis.de/DE/Presse/Pressemitteilungen/2024/12/PD24_460_14.html

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
    # 'lastElection': [24.1, 25.7, 14.8, 11.5, 4.9, 10.3, 8.7, 0.0] #2021
    # order 2021: ['Union', 'SPD', 'Grüne', 'FDP', 'Linke', 'AfD', 'Übrige', 'BSW']
    # order 2025: ['Union', 'AfD', 'SPD', 'Grüne', 'Linke', 'BSW', 'FDP', 'Übrige']
    'lastElection': [28.5, 20.8, 16.4, 11.6, 8.8, 4.97, 4.3, 4.5]
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

# Round values (keep decimals)
projection_data[['lowerBound', 'average', 'upperBound']] = projection_data[['lowerBound', 'average', 'upperBound']].round(4)

# Write to JSON
projection_chart_data = projection_data.to_dict(orient='records')

with open('./data/projectionChart.json', 'w', encoding='utf-8') as f:
    json.dump(projection_chart_data, f, ensure_ascii=False, indent=1, allow_nan=False)

print("JSON file 'projectionChart.json' has been created successfully.")

# Map party names to color codes and Q IDs
party_metadata = {
    "Union": {
        "colorCode": "#0a0a0a",
        "id": "cdu_csu"
    },
    "AfD": {
        "colorCode": "#0084c7",
        "id": "afd"
    },
    "SPD": {
        "colorCode": "#c31906",
        "id": "spd"
    },
    "Grüne": {
        "colorCode": "#66a622",
        "id": "gruene"
    },
    "Linke": {
        "colorCode": "#8440a3",
        "id": "linke"
    },
    "BSW": {
        "colorCode": "#da467d",
        "id": "bsw"
    },
    "FDP": {
        "colorCode": "#F3B030",
        "id": "fdp"
    }
}

# --- Coalition scenarios around the 5%-threshold ---
# Baseline seats stay "hard" (point estimate). We additionally compute Low/High scenarios
# for parties close to 5% to label coalitions as stabil / wacklig / unmöglich.

TOTAL_SEATS = 630
MAJORITY = 316

# Party stats: latest trend + per-party mean CI
party_stats = latest_rolling_averages[latest_rolling_averages["Partei"] != "Übrige"].merge(
    mean_ci_per_party, left_on="Partei", right_on="Partei", how="left"
)
party_stats["mean_ci"] = pd.to_numeric(party_stats["mean_ci"], errors="coerce")

# If a party has no CI (should be rare), fall back to 3.0pp
party_stats["mean_ci"] = party_stats["mean_ci"].fillna(3.0)

# "Wacklig" if the CI interval around the point estimate crosses the 5%-threshold
party_stats["wacklig"] = (party_stats["average"] - 5.0).abs() <= party_stats["mean_ci"]

# Scenario membership rules
in_base = party_stats.loc[party_stats["average"] >= 5.0, ["Partei", "average"]].set_index("Partei")["average"]
in_low = party_stats.loc[(party_stats["average"] >= 5.0) & (~party_stats["wacklig"]), ["Partei", "average"]].set_index("Partei")["average"]
in_high = party_stats.loc[(party_stats["average"] >= 5.0) | (party_stats["wacklig"]), ["Partei", "average"]].set_index("Partei")["average"]


def _allocate_seats(avgs: pd.Series, total_seats: int = TOTAL_SEATS):
    """Allocate seats using Sainte-Laguë/Schepers (divisor method with standard rounding).

    We implement it via the equivalent highest-averages procedure (Webster/Sainte-Laguë):
    assign seats one-by-one to the party with the highest quotient votes/(2*s+1).

    Returns (seats_by_party, wasted_votes_pct).
    """
    seats_by_party = {p: 0 for p in party_metadata.keys()}

    if avgs is None or len(avgs) == 0:
        return seats_by_party, 100.0

    avgs = pd.to_numeric(avgs, errors="coerce").dropna()
    avgs = avgs[avgs > 0]
    if len(avgs) == 0 or float(avgs.sum()) <= 0:
        return seats_by_party, 100.0

    value_sum = float(avgs.sum())
    wasted = float(100.0 - value_sum)

    # Normalize to the in-parliament vote pool (as before)
    votes = (avgs / value_sum) * 100.0

    # Sainte-Laguë seat assignment
    s = pd.Series(0, index=votes.index, dtype="int64")

    for _ in range(int(total_seats)):
        quot = votes / (2 * s + 1)
        m = quot.max()
        top = quot[quot == m].index
        if len(top) > 1:
            # deterministic tie-break: higher votes, then name
            top_votes = votes.loc[top]
            mv = top_votes.max()
            top2 = top_votes[top_votes == mv].index
            winner = sorted(list(top2))[0]
        else:
            winner = top[0]
        s.loc[winner] += 1

    for p, seat_count in s.items():
        seats_by_party[str(p)] = int(seat_count)

    return seats_by_party, wasted


seats_base, wasted_base = _allocate_seats(in_base)
seats_low, wasted_low = _allocate_seats(in_low)
seats_high, wasted_high = _allocate_seats(in_high)

# Baseline coalitionSeats (this is what the chart uses for bars)
coalitionSeats = []
for party_name, meta in party_metadata.items():
    coalitionSeats.append({
        "id": meta["id"],
        "color": {"colorCode": meta["colorCode"]},
        "name": party_name,
        "seats": int(seats_base.get(party_name, 0))
    })

# Add wasted-votes info to notes (keeps the chart itself unchanged)
def _fmt_pct_de(x):
    try:
        return f"{float(x):.1f}".replace(".", ",")
    except Exception:
        return ""

notes_chart_seats_extra = "««Stabile/wackelige/unrealistische» Mehrheit geprüft anhand von Modellrechnung für Parteien nahe der 5-Prozent-Hürde. "

# Koalitions-Templates schreiben (pro Lauf neu)
write_coalition_templates(data_dir=COALITION_TEMPLATES_DIR)

# Pick coalition template file based on switch parties present in baseline parliament
present = [p.lower() for p in SWITCH_PARTIES if int(seats_base.get(p, 0)) > 0]
if present:
    suffix = "_" + "_".join(sorted(present))
else:
    suffix = ""

coalition_file = os.path.join(COALITION_TEMPLATES_DIR, f"coalitions{suffix}.json")

if not os.path.exists(coalition_file):
    raise FileNotFoundError(f"Missing coalition template: {coalition_file}")

with open(coalition_file, "r", encoding="utf-8") as f:
    coalition_set = json.load(f)

print(f"Loaded coalition file: {coalition_file}")

# --- Label each coalition as stabil / wacklig / unmöglich based on Low/Base/High scenarios ---
id_to_party = {meta["id"]: party for party, meta in party_metadata.items()}

for c in coalition_set:
    party_ids = [p.get("id") for p in c.get("parties", []) if isinstance(p, dict)]
    party_names = [id_to_party.get(pid) for pid in party_ids]
    party_names = [p for p in party_names if p is not None]

    base_total = sum(int(seats_base.get(p, 0)) for p in party_names)
    low_total = sum(int(seats_low.get(p, 0)) for p in party_names)
    high_total = sum(int(seats_high.get(p, 0)) for p in party_names)

    if low_total >= MAJORITY:
        status = "stabil"
    elif high_total < MAJORITY:
        status = "unmöglich"
    else:
        status = "wacklig"

    label_map = {
        "stabil": "stabile Mehrheit",
        "wacklig": "wackelige Mehrheit",
        "unmöglich": "Mehrheit unrealistisch",
    }
    label = label_map.get(status, status)

    # Replace any existing guillemet placeholder like «…» with a parenthetical label
    name = c.get("name", "")
    if isinstance(name, str):
        if "«" in name and "»" in name:
            # Remove the guillemet segment entirely and append the label
            name_clean = re.sub(r"\s*«.*?»\s*", "", name).strip()
            c["name"] = f"{name_clean} {label}".strip()
        else:
            c["name"] = f"{name} {label}".strip()
    else:
        c["name"] = f"{label}"

    # Optional: store totals for debugging/QA (chart will ignore unknown keys)
    c["_seats_base"] = int(base_total)
    c["_seats_low"] = int(low_total)
    c["_seats_high"] = int(high_total)

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

    # Exclude rows where "Institut" contains "INSA" or "Ipsos"
    df = df[~df["Institut"].str.contains("INSA|Ipsos", case=False, na=False)]

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

""" DISABLE FOR NOW
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
        .ewm(span=14, adjust=False) 
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

    # Drop everything below the date "01.04.2024" (new header appears afterwards with other candidates)
    cutoff_date = pd.to_datetime("01.04.2024", format="%d.%m.%Y")
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

    # Exclude rows where "Institut" contains "INSA" or "Ipsos"
    df = df[~df["Institut"].str.contains("INSA|Ipsos", case=False, na=False)]

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

# Define the new cutoff date
new_cutoff_date = pd.to_datetime("2024-12-10", format="%Y-%m-%d")
kanzlerkandidat_data = kanzlerkandidat_data[kanzlerkandidat_data["Datum"] >= cutoff_date]

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
        .ewm(span=14, adjust=False)  # Span adjusts the weighting; smaller = more weight on recent data
        .mean()
    )

# Add two new columns with NaN initially
kanzlerkandidat_data["Punkte: einzelne Umfragen"] = np.nan
kanzlerkandidat_data["Linie: Durchschnitt"] = np.nan

# Set the value 0 after the second cut-off
first_valid_index_after_cutoff = kanzlerkandidat_data.index[kanzlerkandidat_data["Datum"] >= new_cutoff_date].min()
kanzlerkandidat_data.at[first_valid_index_after_cutoff, "Punkte: einzelne Umfragen"] = 0
kanzlerkandidat_data.at[first_valid_index_after_cutoff, "Linie: Durchschnitt"] = 0

# Filter the data to include only rows from the new cutoff date onward
kanzlerkandidat_data = kanzlerkandidat_data[kanzlerkandidat_data["Datum"] >= new_cutoff_date].reset_index(drop=True)

# Drop the 'Befragtenzahl' column if it exists
if "Befragtenzahl" in kanzlerkandidat_data.columns:
    kanzlerkandidat_data.drop(columns=["Befragtenzahl"], inplace=True)

# Function to check consecutive days and set "_real" columns to NaN due to Datawrapper limitations
def handle_consecutive_days(data, real_columns):
    # Sort by date to ensure consecutive checking works
    data = data.sort_values("Datum").reset_index(drop=True)

    # Iterate through rows and check for consecutive days
    for i in range(1, len(data)):
        # Check if the current and previous rows have consecutive dates and non-NaN values in any "_real" column
        if (
            (data.loc[i, "Datum"] - data.loc[i - 1, "Datum"]).days == 1
            and any(~data.loc[i, real_columns].isna())
            and any(~data.loc[i - 1, real_columns].isna())
        ):
            # Set "_real" columns to NaN for the current row
            data.loc[i, real_columns] = np.nan

    return data

# List of "_real" columns
real_columns = [col for col in kanzlerkandidat_data.columns if col.endswith("_real")]
real_columns_all = [col for col in kanzlerkandidat_data_all.columns if col.endswith("_real")]

# Handle consecutive days in both datasets
kanzlerkandidat_data = handle_consecutive_days(kanzlerkandidat_data, real_columns)
kanzlerkandidat_data_all = handle_consecutive_days(kanzlerkandidat_data_all, real_columns_all)

"""

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
#timecode_all = kanzlerkandidat_data_all["Datum"].iloc[-1]
#timecode = kanzlerkandidat_data["Datum"].iloc[-1]
full_line_chart_data["date"] = pd.to_datetime(full_line_chart_data["date"])
timecode_line = full_line_chart_data["date"].iloc[-1]
#timecode_str_all = timecode_all.strftime("%-d. %-m. %Y")
#timecode_str = timecode.strftime("%-d. %-m. %Y")
timecode_str_line = timecode_line.strftime("%-d. %-m. %Y")
notes_chart_line = "Stand: " + timecode_str_line
notes_chart_seats = "Ohne Berücksichtigung der Grundmandatsklausel. " + notes_chart_seats_extra + "Stand: " + timecode_str_line

""" DISABLE FOR NOW
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
update_chart(id="0d50b45e538faa45f768d3204450d0e7",parties=coalitionSeats, possibleCoalitions=coalition_set, notes=notes_chart_seats)
