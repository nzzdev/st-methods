import pandas as pd
import os
import re
from datetime import datetime, timedelta
from calendar import monthrange
import numpy as np
import json
import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

def update_chart(id, title="", subtitle="", notes="", data="", files="", options=""):  # Q helper function
    # read qConfig file
    json_file = open('./q.config.json')
    qConfig = json.load(json_file)
    # update chart properties
    for item in qConfig.get('items'):
        for environment in item.get('environments'):
            if environment.get('id') == id:
                if title != '':
                    item.get('item').update({'title': title})
                if subtitle != '':
                    item.get('item').update({'subtitle': subtitle})
                if notes != '':
                    item.get('item').update({'notes': notes})
                if len(data) > 0:
                    item['item']['data'] = data
                if len(files) > 0:
                    item['item']['files'] = files
                print('Successfully updated item with id', id,
                      'on', environment.get('name'), 'environment')
                if options != '':
                    item.get('item').update({'options': options})

    # write qConfig file
    with open('./q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False,
                  indent=1, default=str)
    json_file.close()

# Change directory to the script's directory
os.chdir(os.path.dirname(__file__))

# Generate the list of CSV file names for the date range 2022-04-13 to 2022-12-31
csv_files = [
    f'../data/2022-{month:02d}-{day:02d}-rewe.csv'
    for month in range(4, 13)
    for day in range(1, monthrange(2022, month)[1] + 1)
    if not (month == 4 and day < 13)  # Exclude days before April 13
]

# Function to read CSV files and include the date from the filename
def read_csv_with_date(file_path):
    df = pd.read_csv(file_path, sep=';')
    # Extract date from filename, assuming filename format is '../data/YYYY-MM-DD-rewe.csv'
    date_str = re.search(r'\d{4}-\d{2}-\d{2}', file_path).group()
    df['Date'] = date_str
    return df

# Read all CSV files into a list of DataFrames
data_frames = []
for csv_file in csv_files:
    if os.path.exists(csv_file):
        df = read_csv_with_date(csv_file)
        data_frames.append(df)
    else:
        print(f"File not found: {csv_file}")

# Concatenate all DataFrames into one
merged_df = pd.concat(data_frames, ignore_index=True)

# Replace contents in the column "Marke"
brand_replacements = {
    'ja!': 1,
    'REWE Beste Wahl': 2,
    'REWE': 2,
    'REWE Bio': 3
}
# Replace using the map method, which explicitly maps values
merged_df['Marke'] = merged_df['Marke'].map(brand_replacements).astype('int32')

# Update 'Marke' column for IDs with incorrect brands
brand_updates = {
    8458258: 3,
    7741450: 3,
    7986657: 3,
    8114415: 3
}
for id_val, brand_val in brand_updates.items():
    merged_df.loc[merged_df['ID'] == int(id_val), 'Marke'] = brand_val

# Remove "ca." in the "Name" column
merged_df.loc[merged_df['Gewicht'].notna(), 'Name'] = merged_df.loc[merged_df['Gewicht'].notna(), 'Name'].str.replace(r'ca\..*$', '', regex=True).str.strip()

# Load exceptions and replacements from JSON file
with open('create-shop-file-exceptions.json', 'r') as f:
    exceptions = json.load(f)

# Load exceptions and replacements from JSON file
name_string_replacements = exceptions['name_string_replacements']
name_exceptions = exceptions['name_exceptions']
weight_exceptions = exceptions['weight_exceptions']
name_replacements = exceptions['name_replacements']
weight_replacements = exceptions['weight_replacements']

# Replace specified strings in the "Name" column
for old, new in name_string_replacements.items():
    merged_df['Name'] = merged_df['Name'].str.replace(old, new, regex=False)

# Define the keep strings and patterns
keep_strings = [
    "1,5%", "3,5%", "0,1%", "3,8%", "1,8%", "72%", "100%", "30%", "45%", "48%", "7,5%", "0%", "20%", "51%", "15%", "4%", "60%", "5%"
]
keep_patterns = [r'\b\d{1,3} Stück\b']

# Function to clean the name column
def clean_name(name):
    pattern = r'(\d+(?:,\d+)?%?(?: Stück)?)'
    parts = re.split(pattern, name)
    new_name = ""
    for part in parts:
        if any(keep_str in part for keep_str in keep_strings) or any(re.match(keep_pat, part) for keep_pat in keep_patterns):
            new_name += part
        elif re.match(pattern, part):
            break
        else:
            new_name += part
    return new_name.strip()

merged_df['Name'] = merged_df['Name'].apply(clean_name)

# Clean up the "Gewicht" column
merged_df['Gewicht'] = merged_df['Gewicht'].str.replace(r'\(.*$', '', regex=True).str.strip()

# Remove specific strings from the start of the "Name" column
def clean_start_of_name(name):
    patterns_to_remove = ["ja! ", "Ja! ", "nein! ", "REWE Best Wahl ", "REWE Beste Wahl ", "REWE Beste Wahl-", "REWE beste Wahl ", "Rewe Beste Wahl ", "REWE Bestel Wahl ", "REWE ", "Rewe "]
    for pattern in patterns_to_remove:
        if name.startswith(pattern):
            name = name[len(pattern):]
    return name

merged_df['Name'] = merged_df['Name'].apply(clean_start_of_name)

###############################################
# In case REWE changed the ID, update it here #
###############################################
id_replacements = {
    9689079: 8994273,  # Toilettenpapier 16x200, now 10x200 (update new weight and calculate new price later)
    5499259: 7642029,  # Toilettenpapier 16x200, now 10x200 (update new weight and calculate new price later)
    6697038: 7568160, # Schalotten bio
    1311281: 8919738  # Rote Zwiebeln bio
}
# Replace 'id' values in the DataFrame using the dictionary
merged_df['ID'] = merged_df['ID'].replace(id_replacements)
# Update IDs in the JSON file aswell
with open('create-shop-file.json', 'r') as f:
    category_icon_map = json.load(f)
# Apply ID replacements to the JSON data
for old_id, new_id in id_replacements.items():
    old_id_str = str(old_id)
    new_id_str = str(new_id)
    if old_id_str in category_icon_map:
        # Update the new ID with the same values as the old ID
        category_icon_map[new_id_str] = category_icon_map.pop(old_id_str)
        print(f"Updated ID: {old_id_str} -> {new_id_str}")
    else:
        print(f"ID {old_id_str} not found in JSON file, no update needed.")
# Save the updated JSON back to the file
with open('create-shop-file.json', 'w') as f:
    json.dump(category_icon_map, f, indent=4, ensure_ascii=False)

# Apply exceptions for name
for id_val, name_val in name_exceptions.items():
    merged_df.loc[merged_df['ID'] == int(id_val), 'Name'] = name_val

# Apply exceptions for weight
for id_val, weight_val in weight_exceptions.items():
    merged_df.loc[merged_df['ID'] == int(id_val), 'Gewicht'] = weight_val

# Overwrite the 'Name' column directly based on the 'ID' values
for id_val, name_val in name_replacements.items():
    merged_df.loc[merged_df['ID'] == int(id_val), 'Name'] = name_val

# Overwrite the 'Gewicht' column directly based on the 'ID' values
for id_val, weight_val in weight_replacements.items():
    merged_df.loc[merged_df['ID'] == int(id_val), 'Gewicht'] = weight_val

# Drop specific IDs
merged_df = merged_df[merged_df['ID'] != 8032701]  # REWE Beste Wahl Apfelsaft "Bienen-Edition"
merged_df = merged_df[merged_df['ID'] != 8025058]  # REWE Beste Wahl Romatomaten (no old price)
merged_df = merged_df[merged_df['ID'] != 2224358]  # Bio Cherry Romatomaten (no old price)
# drop "duplicate" Beste Wahl products to avoid confusion with ja! version
merged_df = merged_df[merged_df['ID'] != 1290607] # Tomaten-Cremesuppe
merged_df = merged_df[merged_df['ID'] != 112237] # Sprühsahne
merged_df = merged_df[merged_df['ID'] != 1211124] # Weizenmehl Type 405
merged_df = merged_df[merged_df['ID'] != 134745] # Delikatess-Lachsschinken
merged_df = merged_df[merged_df['ID'] != 1977824] # Erbsen extra fein
merged_df = merged_df[merged_df['ID'] != 2316984] # Lasagne Bolognese
merged_df = merged_df[merged_df['ID'] != 197010] # Gulaschsuppe
merged_df = merged_df[merged_df['ID'] != 2386391] # Gulaschsuppe
merged_df = merged_df[merged_df['ID'] != 1236141] # Hühner-Nudeltopf
merged_df = merged_df[merged_df['ID'] != 7262335] # Tomatenketchup
merged_df = merged_df[merged_df['ID'] != 1400294] # Zartbitter Schokolade
merged_df = merged_df[merged_df['ID'] != 975749] # Feta-Hirtenkäse
merged_df = merged_df[merged_df['ID'] != 2632428] # Spaghetti
merged_df = merged_df[merged_df['ID'] != 8282037] # Frischei-Spaghetti
merged_df = merged_df[merged_df['ID'] != 1387339] # fünflagiges Toilettenpapier
merged_df = merged_df[merged_df['ID'] != 7077819] # Weidemilch-Butter Süßrahm
merged_df = merged_df[merged_df['ID'] != 112068] # Schlagsahne 500g
merged_df = merged_df[merged_df['ID'] != 555425] # Schlagsahne 200g
merged_df = merged_df[merged_df['ID'] != 7288865] # Olivenöl raffiniert 
merged_df = merged_df[merged_df['ID'] != 8087752] # Räucerlachs

# Final sorting by 'Marke' and 'Name'
merged_df = merged_df.sort_values(by=['Marke', 'Name'])

# Now, we need to get 'first_price' as the earliest price found for each product
# and 'first_seen' as the earliest date the product appeared
# We also need 'last_seen' as the last date the product was seen (in 2022 data)

# Convert 'Date' column to datetime
merged_df['Date'] = pd.to_datetime(merged_df['Date'])

# Group by 'ID' and get the earliest and latest dates and corresponding prices
grouped = merged_df.groupby('ID').agg({
    'Marke': 'first',
    'Name': 'first',
    'Gewicht': 'first',
    'Preis': [('first_price', lambda x: x.iloc[x.index.get_loc(x.index.min())]),
              ('last_price', lambda x: x.iloc[x.index.get_loc(x.index.max())])],
    'Date': [('first_seen', 'min'), ('last_seen', 'max')]
})

# Flatten MultiIndex columns
grouped.columns = ['brand', 'name', 'weight', 'first_price', 'last_price', 'first_seen', 'last_seen']
grouped = grouped.reset_index()

# Now, read recent CSV files (last 30 days), including the date
def get_recent_csv_files(n=30):
    recent_files = []
    for days_ago in range(0, n + 50):  # Check for 50 days to get at least 30 files
        date = datetime.today() - timedelta(days=days_ago)
        date_str = date.strftime('%Y-%m-%d')
        csv_path = f'../data/{date_str}-rewe.csv'
        if os.path.exists(csv_path):
            recent_files.append(csv_path)
        if len(recent_files) == n:
            break
    return recent_files

recent_csv_files = get_recent_csv_files()

# Read recent files and include the date
recent_data_frames = []
for csv_file in recent_csv_files:
    if os.path.exists(csv_file):
        df = read_csv_with_date(csv_file)
        recent_data_frames.append(df)
    else:
        print(f"File not found: {csv_file}")

# Concatenate recent DataFrames
if recent_data_frames:
    recent_merged_df = pd.concat(recent_data_frames, ignore_index=True)
    recent_merged_df['Date'] = pd.to_datetime(recent_merged_df['Date'])

    # Get the most recent price and date for each product
    recent_grouped = recent_merged_df.groupby('ID').agg({
        'Preis': 'last',
        'Date': 'max'
    }).rename(columns={'Preis': 'last_price', 'Date': 'recent_date'}).reset_index()

    # Merge recent data with grouped data
    merged_result = pd.merge(grouped, recent_grouped, on='ID', how='left')

    # Update 'last_seen' where recent data is available
    merged_result['last_seen'] = merged_result['recent_date'].combine_first(merged_result['last_seen'])

    # Set 'last_price' directly from recent data
    merged_result['last_price'] = merged_result['last_price_y']

    # Drop unnecessary columns
    merged_result.drop(columns=['last_price_x', 'last_price_y', 'recent_date'], inplace=True)

else:
    # If no recent data is available, use the grouped data
    merged_result = grouped.copy()
    # Since there's no 'last_price_y', ensure 'last_price' is set to NaN
    merged_result['last_price'] = pd.NA

# Convert 'last_price' to nullable integer type 'Int64'
merged_result['last_price'] = merged_result['last_price'].astype('Int64')

# Rename columns
merged_result.rename(columns={'ID': 'id'}, inplace=True)

# Reorder columns
merged_result = merged_result[['id', 'brand', 'name', 'weight', 'first_price', 'last_price', 'first_seen', 'last_seen']]

# Convert 'id' to string for consistency
merged_result['id'] = merged_result['id'].astype(str)

# Load 'category_icon_map' from JSON
with open('create-shop-file.json', 'r') as f:
    category_icon_map = json.load(f)

# Assign 'cat' and 'icon' with default values for missing entries
merged_result['cat'] = merged_result['id'].apply(
    lambda x: category_icon_map.get(x, {'cat': 'other'})['cat']
)
merged_result['icon'] = merged_result['id'].apply(
    lambda x: category_icon_map.get(x, {'value': 18})['value']
)
#########################
# Add products manually #
#########################
# Source: https://web.archive.org/web/20220129021400/https://www.aldi-nord.de/sortiment/getraenke/bier.html
# Source 2: https://web.archive.org/web/20220322123345/https://www.aldi-nord.de/sortiment/babyprodukte.html
# Setup dates
date = datetime.today() - timedelta(days=7) # fake date
first_seen_date = pd.to_datetime("2022-01-29")
last_seen_date = pd.to_datetime(date.strftime('%Y-%m-%d'))  # Ensure correct format

# URLs for the product pages
product_urls = [
    "https://www.aldi-nord.de/produkt/pilsener-0313-1-1.article.html",
    "https://www.aldi-nord.de/produkt/premium-pilsener-0312-0-0.article.html",
    "https://www.aldi-nord.de/produkt/premium-windeln-groesse-3-midi-1003349-0-0.article.html",
    "https://www.aldi-nord.de/produkt/baby-pflegetu_cher-1016069-0-0.article.html"
]

# Default fallback prices
default_prices = [45, 269, 555, 275]

# Function to generate headers for the request
def generate_headers():
    return {
        'user-agent': generate_user_agent(),
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

# Function to scrape price from a product page
def scrape_price(url):
    try:
        headers = generate_headers()
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find the price in the span with class 'price__wrapper'
        price_span = soup.find("span", class_="price__wrapper")
        if price_span:
            price_text = price_span.get_text(strip=True)
            # Remove the period and convert to integer (assumes price in format "2.69")
            return int(float(price_text.replace(".", "")))
        else:
            print(f"Price not found on page: {url}")
            return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

# Scrape prices from both product pages
scraped_prices = [scrape_price(url) for url in product_urls]

# Replace None values in scraped_prices with default prices
final_prices = [
    scraped_price if scraped_price is not None else default_price
    for scraped_price, default_price in zip(scraped_prices, default_prices)
]

# Create a DataFrame for the new products with final prices
new_products = pd.DataFrame({
    'id': ['999999', '999990', '999991', '999992'],
    'brand': [1, 1, 1, 1],
    'name': ['Bier (Discounter-Pils)', 'Bier (Discounter-Pils)', 'Baby Windeln, diverse Grössen (Aldi)', 'Baby Feuchttücher (Aldi)'],
    'weight': ['0,5l', '6x0,5l', '32 bis 46 Stück', '3x80'],
    'first_price': [36, 179, 525, 248],
    'last_price': final_prices,  # Use final prices here
    'first_seen': [first_seen_date, first_seen_date, first_seen_date, first_seen_date], # Ensure datetime format
    'last_seen': [last_seen_date, last_seen_date, last_seen_date, last_seen_date], # Ensure datetime format
    'cat': ['drinks', 'drinks', 'drugstore', 'drugstore'],
    'icon': [11, 24, 18, 18]
})

# Append the new products to the merged_result DataFrame
merged_result = pd.concat([merged_result, new_products], ignore_index=True)

# Print a summary of the scraping process
if all(price is not None for price in scraped_prices):
    print("Aldi prices scraped and updated successfully.")
else:
    print("One or more prices from Aldi failed to scrape. Default prices were used for those entries.")

##########################################
# Overwrite all prices from -pickup.csv #
##########################################
# **Add the sorting by 'brand' and 'name'**
merged_result = merged_result.sort_values(by=['brand', 'name'])

# Define a function to get the most recent "-pickup" CSV file
def get_most_recent_pickup_file():
    for days_ago in range(0, 10):  # Check the last 10 days
        date = datetime.today() - timedelta(days=days_ago)
        date_str = date.strftime('%Y-%m-%d')
        pickup_csv_path = f'../data/{date_str}-rewe-pickup.csv'
        if os.path.exists(pickup_csv_path):
            return pickup_csv_path, date_str
    return None, None  # Return None if no recent file is found

# Get the most recent '-pickup' file
most_recent_pickup_file, pickup_date = get_most_recent_pickup_file()

if most_recent_pickup_file:
    print(f"Using backup file: {most_recent_pickup_file}")
    
    # Load the backup results from the most recent '-pickup' file
    backup_results = pd.read_csv(most_recent_pickup_file, sep=';')
    
    # Ensure IDs are treated consistently as strings
    backup_results['ID'] = backup_results['ID'].astype(str)
    merged_result['id'] = merged_result['id'].astype(str)
    
    # Rename 'Preis' in the backup to 'last_price' for alignment
    backup_results = backup_results.rename(columns={'Preis': 'last_price'})
    
    # Save old prices before merging
    merged_result['old_last_price'] = merged_result['last_price'].copy()
    
    # Merge `merged_result` with `backup_results` to overwrite prices
    merged_result = merged_result.merge(
        backup_results[['ID', 'last_price']],  # Select only relevant columns
        left_on='id', right_on='ID', how='left', suffixes=('', '_backup')
    )
    
    # If a backup price exists, overwrite the `last_price` and `last_seen`
    merged_result['last_price'] = merged_result['last_price_backup'].combine_first(merged_result['last_price'])
    merged_result['last_seen'] = merged_result['last_seen'].combine_first(
        pd.Series([pickup_date] * len(merged_result), index=merged_result.index)
    )
    
    # Drop unnecessary columns
    merged_result = merged_result.drop(columns=['ID', 'last_price_backup'])
    
    # Identify which rows had their prices updated
    updated_prices_mask = merged_result['old_last_price'] != merged_result['last_price']

    # Filter out rows where the price remained unchanged or was NaN
    updated_ids = merged_result.loc[updated_prices_mask & merged_result['last_price'].notna(), 'id']

    # Identify rows where `last_price` was filled from the backup
    filled_prices_mask = merged_result['old_last_price'].isna() & merged_result['last_price'].notna()

    # Print the list of IDs that had their prices updated
    print("IDs with overwritten prices from the -pickup.csv:")
    print(updated_ids.tolist())

    # Log IDs where prices were filled
    filled_ids = merged_result.loc[filled_prices_mask, 'id']
    print("IDs with prices filled from the -pickup.csv (previously missing):")
    print(filled_ids.tolist())

    print("Prices updated from the most recent '-pickup.csv' file.")

else:
    print("No recent '-pickup' file found. No prices updated.")

##################################################
# Get old prices manually for important products #
##################################################
updates = {
    "687999": {"first_price": 65, "first_seen": "2022-01-29"},
    "688014": {"first_price": 65, "first_seen": "2022-01-29"},
    "6564984": {"first_price": 99, "first_seen": "2022-01-29"},
    "7196141": {"first_price": 59, "first_seen": "2022-01-29"},
    "7197142": {"first_price": 59, "first_seen": "2022-01-29"},
    "8994273": {"first_price": 431, "first_seen": "2022-01-29"},
    "8125186": {"first_price": 399, "first_seen": "2022-01-29"},
    "8125487": {"first_price": 399, "first_seen": "2022-01-29"},
    "6243827": {"first_price": 349, "first_seen": "2022-01-29"},
    "6243711": {"first_price": 219, "first_seen": "2022-01-29"},
    "3151583": {"first_price": 249, "first_seen": "2022-01-29"},
    "7642029": {"first_price": 325, "first_seen": "2022-01-29"},
    "5883121": {"first_price": 165, "first_seen": "2022-01-29"},
    "559003": {"first_price": 229, "first_seen": "2022-01-29"},
    "8919738": {"first_price": 129, "first_seen": "2022-01-29"},
    "6878636": {"first_price": 39, "first_seen": "2022-01-29"},
    "6953115": {"first_price": 79, "first_seen": "2022-01-29"},
    "8260720": {"first_price": 79, "first_seen": "2022-01-29"},
    "165932": {"first_price": 49, "first_seen": "2022-01-29"},
    "2737743": {"first_price": 99, "first_seen": "2022-01-29"},
    "8023655": {"first_price": 89, "first_seen": "2022-01-29"},
    "2030321": {"first_price": 119, "first_seen": "2022-01-29"},
    "7291190": {"first_price": 79, "first_seen": "2022-01-29"},
    "8359468": {"first_price": 189, "first_seen": "2022-01-29"}}
# Source noodles: https://web.archive.org/web/20220129132817/https://www.aldi-nord.de/sortiment/nahrungsmittel/nudeln-reis.html
# Source toilet paper: https://web.archive.org/web/20220126073117/https://www.aldi-nord.de/sortiment/haushalt/papierprodukte.html
# Source coffee: https://web.archive.org/web/20220118013242/https://www.aldi-nord.de/sortiment/kaffee-tee-kakao/kaffee/kaffee-gold-3307-3-0.article.html
# Source butter: https://web.archive.org/web/20220128003010/https://www.aldi-nord.de/sortiment/kuehlung-tiefkuehlung/kaese-milch-milchprodukte/butter-sahne-sauerrahm.html
# Source snacks: https://web.archive.org/web/20220125111927/https://www.aldi-nord.de/sortiment/aldi-eigenmarken/sunsnacks.html
# Source ketchup: https://web.archive.org/web/20211020205837/https://www.aldi-nord.de/sortiment/nahrungsmittel/saucen-oele-gewuerze/saucen.html

# Apply the updates to the 'first_price' and 'first_seen' columns
for id_val, values in updates.items():
    merged_result.loc[merged_result['id'] == id_val, 'first_price'] = values['first_price']
    merged_result.loc[merged_result['id'] == id_val, 'first_seen'] = values['first_seen']

# testing the logic for the alternative ids below
#merged_result.loc[merged_result['id'] == '2467008', 'last_price'] = None

# Add a percentage sign and a space to the "name" column if "brand" is 1
def append_note(name):
    if name.endswith("¹"):
        return name  # Avoid duplicate prefix
    return f"{name}¹"

if "brand" in merged_result.columns and "name" in merged_result.columns:
    merged_result.loc[merged_result["brand"] == 2, "name"] = merged_result.loc[
        merged_result["brand"] == 2, "name"
    ].apply(append_note)

# Save the final sorted and cleaned dataframe to a new CSV file
merged_result.to_csv('../data/products.csv', sep=';', index=False)

#################################
# LOOK FOR ALT IDs FOR PERSONAS #
#################################
# File paths
json_path = "./personas.json"
alternatives_csv_path = "./personas-alternatives.csv"
products_csv_path = "../data/products.csv"
error_log_path = "./error_log.txt"

# Step 1: Load the JSON file and convert product IDs to strings
with open(json_path, 'r') as f:
    personas = json.load(f)

for persona in personas:
    for product in persona["products"]:
        product["id"] = str(product["id"])  # Ensure IDs are stored as strings in the JSON

# Step 2: Load the personas-alternatives.csv file and ensure all values are strings or None
alternatives_df = pd.read_csv(alternatives_csv_path, dtype=str).fillna("")
alternatives_df.columns = ["id", "alt1", "alt2"]  # Ensure correct column names
#alternatives_df = alternatives_df.applymap(lambda x: str(int(x)) if x.isdigit() else None)  # Convert to strings or None
alternatives_df = alternatives_df.apply(lambda col: col.map(lambda x: str(int(x)) if x.isdigit() else None))

# Step 3: Load the products.csv file
products_df = pd.read_csv(products_csv_path, sep=';', dtype=str)
products_df = products_df[~products_df["last_price"].isna()]  # Drop rows with no last_price
products_df = products_df[["id"]]  # Keep only the 'id' column
valid_ids = set(products_df["id"])  # Set of valid IDs as strings

# Step 4: Prepare error logging
logged_errors = set()  # To avoid logging the same error multiple times
errors = []

# Step 5-8: Check IDs in the JSON and process alternatives
for persona in personas:
    for product in persona["products"]:
        current_id = product["id"]

        # Step 4: Check if the ID is valid
        if current_id in valid_ids:
            continue  # ID is valid, no action needed

        # Step 6: Look for alternatives (including the `id` column of the alternatives file)
        alternative_found = False
        row = alternatives_df[
            (alternatives_df["id"] == current_id) |
            (alternatives_df["alt1"] == current_id) |
            (alternatives_df["alt2"] == current_id)
        ]

        if not row.empty:
            row = row.iloc[0]  # Get the first match (assuming unique rows for each ID)
            for alt_id in [row["id"], row["alt1"], row["alt2"]]:
                if alt_id and alt_id in valid_ids:  # Check for valid alternative
                    # Replace the ID in the JSON file
                    product["id"] = alt_id
                    print(f"Replaced ID {current_id} with alternative {alt_id} in persona '{persona['id']}'")
                    alternative_found = True
                    break

        # Step 8: Log an error if no alternative is found
        if not alternative_found:
            error_message = f"ID {current_id} in persona '{persona['id']}' has no valid alternative."
            if error_message not in logged_errors:
                errors.append(error_message)
                logged_errors.add(error_message)
                print(error_message)

# Step 9: Write errors to a text file
if errors:
    with open(error_log_path, 'w') as f:
        f.write("\n".join(errors))
    print(f"Errors logged to {error_log_path}")
else:
    print("No errors encountered.")

# Save updated JSON
with open(json_path, 'w') as f:
    json.dump(personas, f, indent=4, ensure_ascii=False) # don't convert Umlaute etc.
    print(f"Updated JSON file saved to {json_path}")

# prepare some data for q.config.json
file = [{
    "loadSyncBeforeInit": False,
    "file": {
        "path": "../data/products.csv"
    }
    },
{
    "loadSyncBeforeInit": True,
    "file": {
        "path": "./favorites.json"
    }
    },
    {
    "loadSyncBeforeInit": True,
    "file": {
        "path": "./personas.json"
    }
}]

# run Q function
update_chart(id='9c34f843abc41325f7ff6d735fa0a49f', files=file)
    
###############################
# CALCULATE PERCENTAGE CHANGE #
###############################
# Read the CSV file into a DataFrame
df = pd.read_csv('../data/products.csv', sep=';')

# General calculations for all brands
df['percent_increase'] = ((df['last_price'] - df['first_price']) / df['first_price']) * 100
df['price_ratio'] = 1 + (df['percent_increase'] / 100)

# Function to calculate average price increase and geometric mean for a specific brand
def calculate_brand_stats(brand_df, brand_name):
    # Calculate average percent increase, ignoring NaNs
    average_increase = brand_df['percent_increase'].mean()

    # Filter out NaNs and ratios <= 0
    valid_price_ratios = brand_df['price_ratio'].dropna()
    valid_price_ratios = valid_price_ratios[valid_price_ratios > 0]

    if not valid_price_ratios.empty:
        geometric_mean_ratio = np.exp(np.nanmean(np.log(valid_price_ratios)))
        geometric_mean_percent = (geometric_mean_ratio - 1) * 100
    else:
        geometric_mean_percent = np.nan  # Set to NaN if no valid data

    # Round the output to integers for display, handle NaN
    avg_increase_str = f"{average_increase:.0f}%" if pd.notnull(average_increase) else "N/A"
    geom_mean_str = f"{geometric_mean_percent:.0f}%" if pd.notnull(geometric_mean_percent) else "N/A"

    print(f"\n{'='*50}\n{brand_name}: Average price increase: {avg_increase_str} "
          f"(geometric mean: {geom_mean_str}).\n")

# Function to calculate the geometric mean for categories
def calculate_geometric_mean_for_category(df):
    def geom_mean(group):
        valid_price_ratios = group.dropna()
        valid_price_ratios = valid_price_ratios[valid_price_ratios > 0]
        if not valid_price_ratios.empty:
            return (np.exp(np.nanmean(np.log(valid_price_ratios))) - 1) * 100
        else:
            return np.nan

    geometric_means = df.groupby('cat')['price_ratio'].apply(geom_mean)
    return geometric_means

# Calculate geometric mean price increase for all categories
category_price_increase_all_brands = calculate_geometric_mean_for_category(df)

# Calculate average percent increase and geometric mean percent for all brands
average_percent_increase = df['percent_increase'].mean()

valid_price_ratios = df['price_ratio'].dropna()
valid_price_ratios = valid_price_ratios[valid_price_ratios > 0]

if not valid_price_ratios.empty:
    geometric_mean_ratio = np.exp(np.nanmean(np.log(valid_price_ratios)))
    geometric_mean_percent = (geometric_mean_ratio - 1) * 100
else:
    geometric_mean_percent = np.nan

# Output for ALL BRANDS
avg_increase_str = f"{average_percent_increase:.0f}%" if pd.notnull(average_percent_increase) else "N/A"
geom_mean_str = f"{geometric_mean_percent:.0f}%" if pd.notnull(geometric_mean_percent) else "N/A"

print(f"\n{'='*50}\nALL BRANDS: Average price increase: {avg_increase_str} (geometric mean: {geom_mean_str}).\n")

# Print top 10 products for all brands
def print_top_products(brand_df, column, order, description, brand_name):
    if order == 'largest':
        top_products = brand_df[['name', column]].nlargest(10, column)
    else:
        top_products = brand_df[['name', column]].nsmallest(10, column)
    output = "\n".join([
        f"   {i+1}. {row['name']} ({row[column]:.0f}%)" 
        for i, (_, row) in enumerate(top_products.iterrows()) 
        if pd.notnull(row[column])
    ])
    print(f"{brand_name}: Top 10 products {description}:\n{output}\n")

# Identify and print the top 9 categories with the highest price increase for all brands
top_nine_increases_all_brands = category_price_increase_all_brands.dropna().nlargest(9)
top_nine_output_all_brands = "\n".join([
    f"   {i+1}. {category} ({increase:.0f}%)" 
    for i, (category, increase) in enumerate(top_nine_increases_all_brands.items())
])
print(f"ALL BRANDS: Categories with the highest price increase (geometric mean):\n{top_nine_output_all_brands}\n")

# Calculations for each brand
for brand, brand_name in [(1, 'JA!'), (2, 'BESTE WAHL'), (3, 'BIO')]:
    brand_df = df[df['brand'] == brand].copy()
    
    # Calculate and print average price increase for each brand
    calculate_brand_stats(brand_df, brand_name)
    
    # Calculate geometric mean for categories for the current brand
    category_price_increase_brand = calculate_geometric_mean_for_category(brand_df)
    
    # Identify and print the top 9 categories with the highest price increase for the current brand
    top_nine_increases_brand = category_price_increase_brand.dropna().nlargest(9)
    top_nine_output_brand = "\n".join([
        f"   {i+1}. {category} ({increase:.0f}%)" 
        for i, (category, increase) in enumerate(top_nine_increases_brand.items())
    ])
    print(f"{brand_name}: Categories with the highest price increase (geometric mean):\n{top_nine_output_brand}\n")
    
    # Print the top 10 highest and lowest price increases for the current brand
    print_top_products(brand_df, 'percent_increase', 'largest', "with the highest price increase", brand_name)
    print_top_products(brand_df, 'percent_increase', 'smallest', "that became cheaper", brand_name)