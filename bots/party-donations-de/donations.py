import os
os.chdir(os.path.dirname(__file__))
import subprocess
import pandas as pd
import re
import html
from datawrapper import Datawrapper
from datetime import datetime

# Datawrapper API key
dw_key = os.environ["DATAWRAPPER_API"]
dw = Datawrapper(access_token=dw_key)
dw_id_bar = "LE7we"
dw_id_bubble = "4kjsg"
dw_id_table = "7IRrV"

def remove_directory(path):
    # Walk the directory tree from the bottom up (so files are removed before directories)
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(path)

# -----------------------------
# 1. Download CSV files from Datawrapper charts
# -----------------------------
if not os.path.exists('data'):
    os.makedirs('data')

charts = {
    'parties_bar.csv': 'wtsPm',
    'parties_bubble.csv': 'waccT',
    'parties_table.csv': 'ift5g'
}

for filename, chart_id in charts.items():
    process = subprocess.Popen(
        ['node', 'dataunwrapper.js', chart_id],
        stdout=subprocess.PIPE
    )
    output = process.stdout.read()
    with open(os.path.join('data', filename), 'wb') as f:
        f.write(output)

df_bar = pd.read_csv('./data/parties_bar.csv', index_col=1, sep=';')
df_bubble = pd.read_csv('./data/parties_bubble.csv', index_col=1, sep=';')
df_bubble.reset_index(inplace=True)
df_table = pd.read_csv('./data/parties_table.csv', sep=';')

# -----------------------------
# 2. Clean df_bubble (unchanged)
# -----------------------------
#df_bubble.columns = [col.replace('<span style="opacity:0%">', '') for col in df_bubble.columns]

def clean_partei_style(val):
    if isinstance(val, str):
        # Remove wrapping span with background and color
        val_clean = re.sub(
            r'<span style="background:#(?:[0-9A-Fa-f]+); color:#(?:[0-9A-Fa-f]+);padding: 0px 3px;">(.*?)</span>',
            r'\1',
            val
        )
        mapping = {
            'CDU': '<span style="color:#0a0a0a">CDU</span>',
            'CSU': '<span style="color:#0a0a0a">CSU</span>',
            'AfD': '<span style="color:#0084c7">AfD</span>',
            'SPD': '<span style="color:#c31906">SPD</span>',
            'Grüne': '<span style="color:#66a622">Grüne</span>',
            'BSW': '<span style="color:#da467d">BSW</span>',
            'FDP': '<span style="color:#d1cc00">FDP</span>',
            'Linke': '<span style="color:#8440a3">Linke</span>'
        }
        return mapping.get(val_clean, val_clean)
    return val

if 'partei_style' in df_bubble.columns:
    df_bubble['partei_style'] = df_bubble['partei_style'].apply(clean_partei_style)

# -----------------------------
# 3. Clean df_table
# -----------------------------

# Step 3.1: Clean the column headers without dropping duplicates yet.
def clean_table_headers(columns, deduplicate=False):
    """
    Clean the headers by removing HTML tags and unescaping HTML entities.
    If deduplicate is False, return a list of headers with the same length as input.
    """
    cleaned = []
    for col in columns:
        # Remove any HTML tags
        col_clean = re.sub(r'<[^>]+>', '', col)
        # Unescape HTML entities (e.g., &nbsp;) and strip whitespace
        col_clean = html.unescape(col_clean).strip()
        # If header includes extra donation info (e.g., "in €" or '^' markers), set it to "Spende"
        if 'in €' in col_clean or ('Datum' in col_clean and '^' in col_clean):
            col_clean = 'Spende'
        cleaned.append(col_clean)
    # Optionally deduplicate if needed, but here we keep the same length.
    if deduplicate:
        final = []
        seen = set()
        for col in cleaned:
            if col not in seen:
                final.append(col)
                seen.add(col)
        return final
    else:
        return cleaned

# Clean headers (expecting 4 headers) and assign them.
df_table.columns = clean_table_headers(df_table.columns, deduplicate=False)

# Now drop the duplicate column(s). This will keep the first occurrence.
df_table = df_table.loc[:, ~df_table.columns.duplicated()]

# After cleaning, the headers should now be:
# ['Spende von', 'Spende', 'Partei']
# Later we will insert the "Datum" column.

# Step 3.2: Clean the "Partei" column by removing unwanted HTML wrappers.
def clean_partei(val):
    if isinstance(val, str):
        val_clean = re.sub(
            r'<span style="font-size:100%;background:#(?:[0-9A-Fa-f]+); color:#(?:[0-9A-Fa-f]+);padding: 0px 3px;">(.*?)</span>',
            r'\1',
            val
        )
        mapping = {
            'CDU': '<span style="color:#0a0a0a"><b>CDU</b></span>',
            'CSU': '<span style="color:#374e8e"><b>CSU</b></span>',
            'AfD': '<span style="color:#0084c7"><b>AfD</b></span>',
            'SPD': '<span style="color:#c31906"><b>SPD</b></span>',
            'Grüne': '<span style="color:#66a622"><b>Grüne</b></span>',
            'BSW': '<span style="color:#da467d"><b>BSW</b></span>',
            'FDP': '<span style="color:#d1cc00"><b>FDP</b></span>',
            'Linke': '<span style="color:#8440a3"><b>Linke</b></span>',
            'FW': '<span style="color:#ac5038"><b>FW</b></span>'
        }
        if val_clean in mapping:
            return mapping[val_clean]
        else:
            return f'<span style="color:#616161"><b>{val_clean}</b></span>'
    return val

if 'Partei' in df_table.columns:
    df_table['Partei'] = df_table['Partei'].apply(clean_partei)

# Step 3.3: Clean the "Spende" column by extracting donation amount and date.
def clean_spende(cell):
    donation = None
    date_str = None
    if isinstance(cell, str):
        # Use delimiter "@@" if available for direct extraction of donation amount.
        if '@@' in cell:
            donation_raw = cell.split('@@')[-1].strip()
            donation = donation_raw.replace('.', '')
        else:
            # Fallback: extract donation amount from an inner span.
            m = re.search(
                r'<span style="position: absolute; top: -8px; left: 50%; transform: translateX\(-50%\); font-size: 13px;">(.*?)</span>',
                cell
            )
            if m:
                donation = m.group(1).replace('.', '')
        # Extract the date from a <b> tag (expected DD.MM.YYYY format)
        m_date = re.search(r'<b[^>]*>(\d{2}\.\d{2}\.\d{4})</b>', cell)
        if m_date:
            try:
                date_obj = datetime.strptime(m_date.group(1), '%d.%m.%Y')
                date_str = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                date_str = None
    return donation, date_str

if 'Spende' in df_table.columns:
    spende_cleaned = []
    datum_list = []
    for cell in df_table['Spende']:
        donation, date_val = clean_spende(cell)
        spende_cleaned.append(donation)
        datum_list.append(date_val)
    df_table['Spende'] = spende_cleaned
    # Insert the "Datum" column as the first column.
    df_table.insert(0, 'Datum', datum_list)
    
# Rename table for Datawrapper
df_table.rename(columns={"Spende von": "Spender"}, inplace=True)

# Ensure the "Datum" column is in datetime format (if not already)
df_table['Datum'] = pd.to_datetime(df_table['Datum'], errors='coerce')

# Extract the maximum (latest) date
latest_date = df_table['Datum'].max()

# Format the latest date as specified: e.g. "1. 1. 2025"
latest_date_str = latest_date.strftime("%-d. %-m. %Y")

# Reset index for bar chart before Datawrapper update
df_bar.reset_index(inplace=True)

# Uüdate bar chart
dw_chart = dw.add_data(chart_id=dw_id_bar, data=df_bar)
date = {"annotate": {
    "notes": f"Stand: {latest_date_str}"}}
dw.update_metadata(chart_id=dw_id_bar, metadata=date)
dw.update_description(chart_id=dw_id_bar, source_name="Bundestag via ZDFheute", intro="Spenden ab 35 000 Euro seit Anfang November 2024")
dw.publish_chart(chart_id=dw_id_bar, display=False)

# Update bubble chart
dw_chart = dw.add_data(chart_id=dw_id_bubble, data=df_bubble)
date = {"annotate": {
    "notes": f"Alle Grossspenden ab 35 000 Euro seit März 2024.<br>Stand: {latest_date_str}"}}
dw.update_metadata(chart_id=dw_id_bubble, metadata=date)
dw.update_description(chart_id=dw_id_bubble, source_name="Bundestag via ZDFheute", intro="Je grösser der Kreis, desto höher der Spendenbetrag in Euro")
dw.publish_chart(chart_id=dw_id_bubble, display=False)

# Update table
dw_chart = dw.add_data(chart_id=dw_id_table, data=df_table)
date = {"annotate": {
    "notes": f"Stand: {latest_date_str}"}}
dw.update_metadata(chart_id=dw_id_table, metadata=date)
dw.update_description(chart_id=dw_id_table, source_name="Bundestag via ZDFheute", intro="Spenden ab 35 000 Euro seit März 2024")
dw.publish_chart(chart_id=dw_id_table, display=False)

# Delete all csv files
if os.path.exists('data'):
    remove_directory('data')