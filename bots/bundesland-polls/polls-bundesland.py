
import pandas as pd
import numpy as np
import os
import json
import re
import time
from decimal import Decimal, ROUND_HALF_UP

# ============================================================
# README (manuelle Einstellungen)
# ============================================================
# 1) Welche Bundesländer laufen?
#    - STATES_TO_RUN = ["bw", "rlp", ...]
#
# 2) Zielumgebung für die MAIN-Q-Items:
#    - TARGET_ENV = "production" | "staging"
#    (nur MAIN-IDs; Table/Coalitions bleiben auf "production")
#
# 3) Pro Bundesland (STATES):
#    Pflicht:
#      - url
#      - q_ids: {main, table, coalitions}
#      - seats (Regelgröße/Grundgröße; keine Überhang-/Ausgleichsmandate)
#      - election_cycle_years (in Deutschland i.d.R. 5)
#    Automatisch aus der Wahlrecht-Tabelle abgeleitet:
#      - last_election (Ergebnis der letzten Wahl)
#      - year / previous_year
#      - hot_phase (nahe am Zielwahltermin)
#      - Zykluslogik:
#        vor der ersten Nachwahl-Umfrage = alter Vorwahl-Zyklus,
#        ab der ersten Nachwahl-Umfrage = nur noch Umfragen nach der letzten Wahl
#      - variant_parties: Parteien, für die es "rein/raus"-Varianten der Koalitionsliste geben soll.
#        Das Skript erzeugt pro Kombination dieser Parteien automatisch eine eigene Koalitionsdatei:
#        coalitions.json, coalitions_fdp.json, coalitions_fdp_fw.json, ...
#        (Suffix = welche dieser Parteien im Basisszenario im Parlament sind).
#        Diese Datei wird dann geladen, damit z.B. eine Ampel nur erscheint, wenn die FDP drin ist.
#      - dedupe_bases: Optionaler Feinschliff gegen doppelte Anzeige.
#        Liste von Basiskoalitionen (z.B. ["CDU","AfD"]).
#        Wenn im selben Szenario eine "erweiterte" Variante existiert (z.B. CDU+AfD+FW),
#        wird die Basis (CDU+AfD) in diesem Szenario unterdrückt.
#      - coalitions_spec: Koalitionen in gewünschter Reihenfolge (Präferenzen)
#
# 4) Parteien/Parser:
#    - PARTY_MAP: Spaltennamen von wahlrecht.de -> Parteinamen
#    - EMBEDDED_TOKENS: Parteien, die in "Sonstige" auftauchen können
#    - party_colors: Farben für Bar + Tabelle
#
# 5) Dateien/Ordner:
#    - Pro Bundesland: ./<kürzel>/data.json und ./<kürzel>/coalitions*.json
#    - q.config.json wird pro Lauf dynamisch neu erzeugt.
# ============================================================

# ============================================================
# Landtagswahlen Deutschland – Umfrage-Schnitt (Balken)
# Quelle: https://www.wahlrecht.de/umfragen/landtage/
#
# Output:
# - ./<kürzel>/data.json  (party, lastElection, average)  ohne Sonstige
# ============================================================

# ============================
# STATES TO RUN (edit here)
# ============================
STATES_TO_RUN = ["bw", "rlp"]  # e.g. ["bw"], ["rlp"], or multiple

# ============================
# TARGET ENVIRONMENT (edit here)
# ============================

TARGET_ENV = "production"  # production | staging (Staging-Test-ID: d8380f0f8c7efbef50a21f6369a9bc0b)
# HOT_PHASE wird automatisch aus der Nähe zur Zielwahl abgeleitet.


HALF_LIFE_HOT = 30.0
HALF_LIFE_COLD = 180.0
# Hot phase wird automatisch über die Nähe zur Zielwahl bestimmt.
HOT_PHASE_DAYS = 60

# Zusätzliches Zeitfenster für den Schnitt:
WINDOW_HOT_DAYS = 90
WINDOW_COLD_DAYS = 730

# Sequenzgewicht pro Institut: verhindert, dass sehr aktive Institute den Schnitt dominieren.
# Neueste Umfrage eines Instituts: 1.0, zweitneueste: 0.5, drittneueste: 0.25, ...
USE_POLLSTER_SEQ_WEIGHT = True

# Zensierte Werte ("unter Sonstige" / nicht explizit ausgewiesen):
# U_CENSORED: Schwelle, unter der Institute oft nicht mehr ausweisen (typisch 3%)
# U_CENSORED_EXPECTED: plausibler Erwartungswert darunter (zieht selten ausgewiesene Kleinparteien Richtung ~2%)
U_CENSORED = 3.0
U_CENSORED_EXPECTED = 2.0

# Marker für Wahlzeilen auf Wahlrecht.de (Länder, Hamburg, Berlin)
ELECTION_CUTOFF_PATTERN = r"(?:Landtagswahl|Bürgerschaftswahl|Abgeordnetenhauswahl)"

# Einheitliches Parteien-Mapping (Wahlrecht-Spalte -> Parteiname)
# Hinweis: In den Ländern steht meist CDU; nur in Bayern kann CSU separat auftauchen.
PARTY_MAP = {
    "CDU": "CDU",
    "CSU": "CSU",
    "SPD": "SPD",
    "GRÜNE": "Grüne",
    "FDP": "FDP",
    "LINKE": "Linke",
    "AfD": "AfD",
}

# Einheitliche Farben (Bar + Tabelle)
party_colors = {
    "CDU": "#000000",
    "CSU": "#000000",
    "Grüne": "#579B2F",
    "SPD": "#BC0E18",
    "FDP": "#F3B030",
    "Linke": "#7B3A95",
    "AfD": "#167BBB",
    "BSW": "#DA467D",
    "FW": "#ac5038",
}

# Kürzel, die in der Zelle "Sonstige" auftauchen können
EMBEDDED_TOKENS = {
    "BSW": "BSW",
    "FW": "FW",
    "FDP": "FDP",
    "LINKE": "Linke",
    "Linke": "Linke",
}

# Konfiguration je Bundesland (URL, Q-IDs, letzte Wahl, Varianten/Koalitionen)
STATES = {
    "bw": {
        "url": "https://www.wahlrecht.de/umfragen/landtage/baden-wuerttemberg.htm",
        "seats": 120,
        "election_cycle_years": 5,
        "q_ids": {
            "table": "558bff2bbd2484d3de317f3f2d8d6367",
            "coalitions": "9ca9ff4a991547939c4a542ed29110e2",
            "main": "558bff2bbd2484d3de317f3f2d9147e3",
        },
        "variant_parties": ["FDP", "BSW", "Linke"],
        "dedupe_bases": [["CDU", "AfD"], ["Grüne", "SPD"]],
        "coalitions_spec": [
            {"name": "", "parties": ["CDU", "Grüne"]},
            {"name": "", "parties": ["CDU", "AfD"]},
            {"name": "", "parties": ["CDU", "SPD", "FDP"]},
            {"name": "", "parties": ["Grüne", "SPD"]},
            {"name": "", "parties": ["Grüne", "SPD", "Linke"]},
            {"name": "", "parties": ["Grüne", "SPD", "BSW"]},
            {"name": "", "parties": ["Grüne", "SPD", "FDP"]},
        ],
    },
    "rlp": {
        "url": "https://www.wahlrecht.de/umfragen/landtage/rheinland-pfalz.htm",
        "seats": 101,
        "election_cycle_years": 5,
        "q_ids": {
            "table": "558bff2bbd2484d3de317f3f2d8d721c",
            "coalitions": "4a85cfcfd9b989f3f6e5c2af5b8bd00a",
            "main": "558bff2bbd2484d3de317f3f2d9164e0",
        },
        "variant_parties": ["FDP", "FW", "Linke"],
        "dedupe_bases": [["CDU", "AfD"], ["SPD", "Grüne"]],
        "coalitions_spec": [
            {"name": "", "parties": ["SPD", "Grüne", "FDP"]},
            {"name": "", "parties": ["SPD", "Grüne"]},
            {"name": "", "parties": ["SPD", "Grüne", "Linke"]},
            {"name": "", "parties": ["CDU", "SPD"]},
            {"name": "", "parties": ["CDU", "AfD", "FW"]},
            {"name": "", "parties": ["CDU", "AfD"]},
            {"name": "", "parties": ["CDU", "FW"]},
        ],
    },
}

# ---- q.config.json dynamisch aus aktiven Bundesländern bauen ----
def build_q_config(states_to_run, target_env):
    """Schreibt ./q.config.json neu für die aktiven Bundesländer.

    Pro aktivem Bundesland werden drei Items erzeugt:
    - main: item enthält `assetGroups` und `notes`
    - table: item enthält `notes` und `data.table`
    - coalitions: item enthält `notes`, `parties`, `possibleCoalitions`

    Nur MAIN-Items nutzen `target_env` als environments[0].name; die anderen bleiben auf `production`.
    """
    items = []

    for sk in states_to_run:
        if sk not in STATES:
            continue
        qids = STATES[sk].get("q_ids", {})
        main_id = qids.get("main")
        table_id = qids.get("table")
        coal_id = qids.get("coalitions")

        if main_id:
            items.append({
                "environments": [{"name": target_env, "id": main_id}],
                "item": {"assetGroups": "", "notes": ""}
            })
        if table_id:
            items.append({
                "environments": [{"name": "production", "id": table_id}],
                "item": {"notes": "", "data": {"table": []}}
            })
        if coal_id:
            items.append({
                "environments": [{"name": "production", "id": coal_id}],
                "item": {"notes": "", "parties": [], "possibleCoalitions": []}
            })

    q = {"items": items}

    with open("./q.config.json", "w", encoding="utf-8") as f:
        json.dump(q, f, ensure_ascii=False, indent=2)


def convert_percentage_to_float(value):
    """Parse percentage-like cells from wahlrecht.

    - '', '-', '—', '–', '..' -> NaN
    - censored like '<3', '≤3', 'unter 3' -> NaN
    - ranges like '2-4' -> midpoint
    - single values -> float
    """
    if pd.isna(value):
        return np.nan

    s = str(value).strip()
    s_lower = s.lower()

    if "<" in s or "≤" in s or "unter" in s_lower:
        return np.nan

    if s in {"", "-", "—", "–", ".."}:
        return np.nan

    s = s.replace("–", "-").replace("—", "-")

    nums = re.findall(r"\d+(?:,\d+)?", s)
    if not nums:
        return np.nan

    vals = [float(x.replace(",", ".")) for x in nums]
    if "-" in s and len(vals) >= 2:
        return (vals[0] + vals[1]) / 2

    return vals[0]


# --- Helper for censored/unter Sonstige logic ---
def is_censored_cell(value) -> bool:
    """True, wenn eine Tabellenzelle eine zensierte Angabe enthält (z.B. '<3', '≤3', 'unter 3')."""
    if pd.isna(value):
        return False
    s = str(value).strip()
    s_lower = s.lower()
    return ("<" in s) or ("≤" in s) or ("unter" in s_lower)



def token_present_in_sonstige(sonstige_cell: str, token: str) -> bool:
    """True, wenn in 'Sonstige' das Token vorkommt (auch ohne Zahl)."""
    if pd.isna(sonstige_cell):
        return False
    s = str(sonstige_cell)
    return re.search(rf"\b{re.escape(token)}\b", s, flags=re.IGNORECASE) is not None


# --- Helper for round-half-up (kaufmännisch runden, nicht Banker's Rounding) ---
def round_half_up(x, ndigits=0):
    """Rundet kaufmännisch (0,5 immer weg von 0), nicht Banker's Rounding wie Python round()."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return np.nan
    q = Decimal("1") if ndigits == 0 else Decimal("1").scaleb(-ndigits)
    return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))


def parse_method_code_and_n(befragte_cell: str):
    """Extract method code (TSM/TOM/O/...) and n from Befragte cell."""
    if pd.isna(befragte_cell):
        return None, np.nan

    s = str(befragte_cell).replace("\xa0", " ").strip()

    m = re.search(r"\b(TSM|TOM|O|T|F)\b", s)
    method = m.group(1) if m else None

    nums = re.findall(r"\d[\d\.]*", s)
    n = np.nan
    if nums:
        n = int(nums[-1].replace(".", ""))
    return method, n


def extract_embedded_party(sonstige_cell: str, token: str):
    """Extract embedded party shares from the 'Sonstige' cell.

    Works with strings like:
    - 'BSW 4 % Sonst. 2 %'
    - 'FW 5%'
    - 'FDP 2 %'

    Returns float or NaN.
    """
    if pd.isna(sonstige_cell):
        return np.nan
    s = str(sonstige_cell)
    # allow token with optional dot and flexible spacing; case-insensitive
    pattern = rf"\b{re.escape(token)}\b\s*([0-9]+(?:,[0-9]+)?)\s*%?"
    m = re.search(pattern, s, flags=re.IGNORECASE)
    if not m:
        return np.nan
    return float(m.group(1).replace(",", "."))


def extract_son_value(sonstige_cell: str):
    """Extract remaining Sonstige value like 'Sonst. 4 %' or 'Sonstige 4 %'."""
    if pd.isna(sonstige_cell):
        return np.nan
    s = str(sonstige_cell)
    m = re.search(r"Sonst\.?\s*(\d+(?:,\d+)?)\s*%?", s, flags=re.IGNORECASE)
    if not m:
        return np.nan
    return float(m.group(1).replace(",", "."))


# ---- Q / update_chart helper (übernommen, IDs später ersetzen) ----

def update_chart(id, title="", subtitle="", notes="", data="", parties="", possibleCoalitions="", assetGroups="", options=""):
    json_file = open("./q.config.json")
    qConfig = json.load(json_file)

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
                    transformed_data = data.astype(str).reset_index(drop=False).T.reset_index().T.apply(list, axis=1).to_list()
                    if "table" in item.get("item").get("data"):
                        item.get("item").get("data").update({"table": transformed_data})
                    else:
                        item.get("item").update({"data": transformed_data})
                if len(parties) > 0:
                    item["item"]["parties"] = parties
                if len(possibleCoalitions) > 0:
                    item["item"]["possibleCoalitions"] = possibleCoalitions
                if len(assetGroups) > 0:
                    item["item"]["assetGroups"] = assetGroups
                if options != "":
                    item.get("item").update({"options": options})

    with open("./q.config.json", "w", encoding="utf-8") as json_out:
        json.dump(qConfig, json_out, ensure_ascii=False, indent=1, default=str)


# ----------------------------
# Per-state runner
# ----------------------------

def run_state(state_key: str):
    if state_key not in STATES:
        raise ValueError(f"Unknown state_key={state_key}. Add it to STATES.")

    URL = STATES[state_key]["url"]
    Q_ID_TABLE = STATES[state_key]["q_ids"]["table"]
    Q_ID_COALITIONS = STATES[state_key]["q_ids"]["coalitions"]
    Q_ID_MAIN_CUSTOM = STATES[state_key]["q_ids"]["main"]

    election_cycle_years = int(STATES[state_key].get("election_cycle_years", 5))
    # Per-state output/input directory (contains data.json and coalition template JSONs)
    state_dir = f"./{state_key}"
    os.makedirs(state_dir, exist_ok=True)

    # ---- Umfragetabelle von Wahlrecht laden ----
    tables = pd.read_html(URL)

    def _normalize_cols(t: pd.DataFrame) -> pd.DataFrame:
        tt = t.copy()
        tt.columns = [str(c).replace("\xa0", " ").strip() for c in tt.columns]
        return tt

    # Umfragetabelle wählen (manche Seiten haben mehrere Tabellen)
    poll_df = None
    for t in tables:
        tt = _normalize_cols(t)
        cols = set(tt.columns)
        if any("Datum" in c for c in cols) and any("Befrag" in c for c in cols) and any("Sonst" in c for c in cols):
            poll_df = tt
            break
    if poll_df is None:
        poll_df = _normalize_cols(tables[0])

    df = poll_df
    original_cols = set(df.columns)

    # Wichtige Spalten erkennen
    institute_col = next((c for c in df.columns if "Institut" in c), df.columns[0])
    befragte_col = next((c for c in df.columns if "Befrag" in c), None)
    date_col = next((c for c in df.columns if c == "Datum" or "Datum" in c), None)
    sonstige_col = next((c for c in df.columns if "Sonst" in c), None)

    if befragte_col is None or date_col is None or sonstige_col is None:
        raise KeyError(f"Missing expected columns on {state_key}: befragte_col={befragte_col}, date_col={date_col}, sonstige_col={sonstige_col}. Columns={list(df.columns)}")

    # Dynamische Ableitung der letzten Wahl aus der Wahlrecht-Tabelle
    def _extract_date_from_marker(text: str) -> pd.Timestamp:
        if pd.isna(text):
            return pd.NaT
        s = str(text)
        m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", s)
        if not m:
            return pd.NaT
        return pd.Timestamp(year=int(m.group(3)), month=int(m.group(2)), day=int(m.group(1)))

    def _parse_election_result_row(row: pd.Series) -> dict:
        res = {}

        # Hauptparteien aus eigenen Spalten
        for src_col, party in PARTY_MAP.items():
            if src_col in row.index:
                res[party] = convert_percentage_to_float(row.get(src_col))

        # Zusatzparteien aus eigenen Spalten
        for extra in ["FW", "BSW"]:
            if extra in row.index:
                res[extra] = convert_percentage_to_float(row.get(extra))

        # Fallback: aus "Sonstige" herausparsen
        if sonstige_col and sonstige_col in row.index:
            sonst_cell = row.get(sonstige_col)
            for token, party in EMBEDDED_TOKENS.items():
                if party not in res or pd.isna(res.get(party)):
                    val = extract_embedded_party(sonst_cell, token)
                    if pd.notna(val):
                        res[party] = val

        # Fehlende bekannte Parteien mit 0.0 auffuellen
        for p in ["CDU", "CSU", "SPD", "Grüne", "FDP", "AfD", "Linke", "FW", "BSW"]:
            if p not in res or pd.isna(res.get(p)):
                res[p] = 0.0

        return {k: float(v) for k, v in res.items()}

    marker_mask_all = df[institute_col].astype(str).str.contains(ELECTION_CUTOFF_PATTERN, na=False)
    election_rows = df.loc[marker_mask_all].copy()
    election_rows["_marker_date"] = election_rows[institute_col].apply(_extract_date_from_marker)
    election_rows = election_rows[election_rows["_marker_date"].notna()].copy()

    if len(election_rows) == 0:
        raise ValueError(f"No election row found on {state_key} page. Cannot derive last election automatically.")

    latest_election_idx = election_rows["_marker_date"].idxmax()
    latest_election_row = df.loc[latest_election_idx].copy()
    last_election_date = election_rows.loc[latest_election_idx, "_marker_date"]
    last_election_year = int(last_election_date.year)
    LAST_ELECTION = _parse_election_result_row(latest_election_row)

    # Rohblöcke rund um die neueste Wahlzeile sichern, damit die Tabelle später
    # Nachwahl-Polls + Wahlzeile + Vorwahl-Zyklus zeigen kann, auch wenn df danach
    # für den BAR-Chart strikt auf den neuen Zyklus reduziert wird.
    marker_rows_all = df.loc[df[institute_col].astype(str).str.contains(ELECTION_CUTOFF_PATTERN, na=False)].copy()
    marker_rows_all["_marker_date"] = marker_rows_all[institute_col].apply(_extract_date_from_marker)
    marker_rows_all = marker_rows_all[marker_rows_all["_marker_date"].notna()].copy()

    latest_marker_idx_raw = int(marker_rows_all["_marker_date"].idxmax())
    latest_marker_date_raw = marker_rows_all.loc[latest_marker_idx_raw, "_marker_date"]

    above_raw = df.loc[: latest_marker_idx_raw - 1].copy() if latest_marker_idx_raw > 0 else df.iloc[0:0].copy()
    below_all_raw = df.loc[latest_marker_idx_raw + 1 :].copy()

    has_post_poll_above_raw = False
    if len(above_raw) > 0 and date_col in above_raw.columns:
        above_dates_raw = pd.to_datetime(above_raw[date_col], format="%d.%m.%Y", errors="coerce")
        has_post_poll_above_raw = (above_dates_raw > latest_marker_date_raw).any()

    older_markers_raw = marker_rows_all[marker_rows_all.index > latest_marker_idx_raw].copy()
    if len(older_markers_raw) > 0:
        next_older_idx_raw = int(older_markers_raw.index.min())
        below_raw = df.loc[latest_marker_idx_raw + 1 : next_older_idx_raw - 1].copy()
    else:
        below_raw = below_all_raw.copy()

    election_row_raw = df.loc[[latest_marker_idx_raw]].copy()

    # Wahl-Markierungen ("Landtagswahl ...") behandeln:
    # - Für BAR/Koalitionen strikt nur den aktuell relevanten Zyklus verwenden.
    # - Vor der ersten Nachwahl-Umfrage: alter Vorwahl-Zyklus unterhalb der neuesten Wahlzeile.
    # - Ab der ersten Nachwahl-Umfrage: nur der neue Nachwahl-Zyklus oberhalb der neuesten Wahlzeile.
    if has_post_poll_above_raw:
        df = above_raw.copy()
    else:
        df = below_raw.copy()

    # Modus + Befragtenzahl aus "Befragte" extrahieren
    df["method"], df["n"] = zip(*df[befragte_col].apply(parse_method_code_and_n))

    # Veröffentlichungsdatum parsen
    df["Datum"] = pd.to_datetime(df[date_col], format="%d.%m.%Y", errors="coerce")
    df = df[df["Datum"].notna()].copy()

    # Dynamisch: Zielwahl, Vorwahl, HOT_PHASE aus Polls und Wahltermin ableiten
    latest_poll_date = df["Datum"].max()
    has_post_election_poll = pd.notna(latest_poll_date) and latest_poll_date > last_election_date

    if has_post_election_poll:
        ELECTION_YEAR = last_election_year + election_cycle_years
        PREVIOUS_ELECTION_YEAR = last_election_year
        target_election_date = last_election_date + pd.DateOffset(years=election_cycle_years)
    else:
        ELECTION_YEAR = last_election_year
        PREVIOUS_ELECTION_YEAR = last_election_year - election_cycle_years
        target_election_date = last_election_date

    days_to_target_election = (target_election_date - latest_poll_date).days if pd.notna(latest_poll_date) else 99999
    HOT_PHASE = days_to_target_election <= HOT_PHASE_DAYS
    HALF_LIFE_DAYS = HALF_LIFE_HOT if HOT_PHASE else HALF_LIFE_COLD

    # Letzten Feldtag aus "Befragte" parsen und als effektives Datum fürs Gewichten nutzen
    def _parse_field_end_date(befragte, pub_date):
        if pd.isna(befragte) or pd.isna(pub_date):
            return pd.NaT
        s = str(befragte).replace("\xa0", " ")
        # Match patterns like 23.2.–26.2. or 23.02.-26.02.
        m = re.search(r"(\d{1,2})\.(\d{1,2})\.\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.", s)
        if not m:
            return pd.NaT
        end_day = int(m.group(3))
        end_month = int(m.group(4))
        pub_dt = pd.to_datetime(pub_date)
        year = int(pub_dt.year)
        # Edge-case: if a poll is published in Jan but fieldwork end is Dec (rare), assume previous year.
        if int(pub_dt.month) == 1 and end_month == 12:
            year -= 1
        return pd.Timestamp(year=year, month=end_month, day=end_day)

    df["field_end"] = df.apply(lambda r: _parse_field_end_date(r.get(befragte_col, ""), r.get("Datum", pd.NaT)), axis=1)
    df["effective_date"] = df["field_end"].where(df["field_end"].notna(), df["Datum"])  # fallback to publication date

    # Parteispalten in Zahlen umwandeln
    for src_col, party in PARTY_MAP.items():
        if src_col in df.columns:
            df[party] = df[src_col].apply(convert_percentage_to_float)
        else:
            df[party] = np.nan

    # Manche Länder haben FW/BSW als eigene Spalten (nicht nur in "Sonstige")
    for extra_col in ["FW", "BSW"]:
        if extra_col in df.columns:
            df[extra_col] = df[extra_col].apply(convert_percentage_to_float)
        else:
            df[extra_col] = np.nan

    # Parteien aus "Sonstige" herausparsen (Fallback, falls keine eigene Spalte)
    for token, party in EMBEDDED_TOKENS.items():
        if party not in df.columns:
            df[party] = np.nan
        embedded_col = f"_embedded_{party}"
        df[embedded_col] = df[sonstige_col].apply(lambda x, t=token: extract_embedded_party(x, t))
        df[party] = df[party].where(df[party].notna(), df[embedded_col])

    # Restliche Sonstige (optional)
    df["Sonstige_rest"] = df[sonstige_col].apply(extract_son_value)

    # Flags: pro Partei markieren, ob der Wert explizit ausgewiesen (reported) oder zensiert/unter Sonstige (censored) ist.
    # Das verhindert, dass selten ausgewiesene Kleinparteien durch "nur hohe" Beobachtungen künstlich nach oben verzerrt werden.
    for src_col, party in PARTY_MAP.items():
        rep_col = f"_reported_{party}"
        cen_col = f"_censored_{party}"

        # reported: numerischer Wert vorhanden
        df[rep_col] = pd.to_numeric(df.get(party), errors="coerce").notna()

        # censored: eigene Spalte vorhanden und zensiert (<3/≤3/unter3)
        cens = False
        if src_col in df.columns:
            cens = df[src_col].apply(is_censored_cell)
        else:
            cens = pd.Series(False, index=df.index)

        df[cen_col] = (~df[rep_col]) & cens

    # Extra Parteien (FW/BSW) können eigene Spalten haben
    for extra in ["FW", "BSW"]:
        rep_col = f"_reported_{extra}"
        cen_col = f"_censored_{extra}"
        df[rep_col] = pd.to_numeric(df.get(extra), errors="coerce").notna()

        cens = pd.Series(False, index=df.index)
        if extra in df.columns:
            cens = df[extra].apply(is_censored_cell)

        df[cen_col] = (~df[rep_col]) & cens

    # Wenn eine Partei nur in 'Sonstige' genannt wird (Token vorhanden), aber kein expliziter Wert da ist,
    # behandeln wir das ebenfalls als zensiert.
    for token, party in EMBEDDED_TOKENS.items():
        rep_col = f"_reported_{party}"
        cen_col = f"_censored_{party}"
        if rep_col not in df.columns:
            df[rep_col] = pd.to_numeric(df.get(party), errors="coerce").notna()
        if cen_col not in df.columns:
            df[cen_col] = False

        token_present = df[sonstige_col].apply(lambda x, t=token: token_present_in_sonstige(x, t))
        df[cen_col] = df[cen_col] | ((~df[rep_col]) & token_present)

    # Presence flag used for "last two polls" inclusion: reported OR censored
    for p in set(list(PARTY_MAP.values()) + ["FW", "BSW"]):
        rep_col = f"_reported_{p}"
        cen_col = f"_censored_{p}"
        if rep_col in df.columns and cen_col in df.columns:
            df[f"_present_{p}"] = df[rep_col] | df[cen_col]

    # Tabellenquelle aus den zuvor gesicherten Rohblöcken bauen:
    # - Nach der Wahl: Nachwahl-Polls oben + Wahlzeile + Vorwahl-Zyklus darunter
    # - Sonst: nur der laufende Vorwahl-Zyklus
    if has_post_poll_above_raw:
        df_table_source = pd.concat([
            above_raw.copy(),
            election_row_raw.copy(),
            below_raw.copy(),
        ], axis=0).copy()
    else:
        df_table_source = below_raw.copy()

    # Nur Parteien behalten, die in den zwei neuesten Umfragen vorkommen
    last_dates = sorted(df["Datum"].dropna().unique())[-2:]
    recent_df = df[df["Datum"].isin(last_dates)].copy()

    def _present_in_recent(party_name: str) -> bool:
        flag = f"_present_{party_name}"
        if flag in recent_df.columns:
            return recent_df[flag].fillna(False).astype(bool).sum() >= 2
        if party_name not in recent_df.columns:
            return False
        return pd.to_numeric(recent_df[party_name], errors="coerce").notna().sum() >= 2

    present_parties = set()
    for p in list(PARTY_MAP.values()) + ["FW", "BSW"]:
        if _present_in_recent(p):
            present_parties.add(p)

    # Große Parteien immer behalten, falls sie in der letzten Wahl >0 hatten
    for p in ["CDU", "CSU", "SPD", "Grüne", "FDP", "AfD", "Linke"]:
        if float(LAST_ELECTION.get(p, 0.0)) > 0.0:
            present_parties.add(p)

    # Ausgabepartien (bundesland-agnostisch)
    base_parties = [v for k, v in PARTY_MAP.items() if k in original_cols]
    extra_parties = ["FW", "BSW", "FDP", "Linke"]

    candidates = []
    for p in base_parties + extra_parties:
        if p not in candidates:
            candidates.append(p)

    parties_out = []
    for p in candidates:
        if p not in df.columns:
            df[p] = np.nan
        if p in present_parties:
            parties_out.append(p)

    # ---- Gewichteter Durchschnitt (Balken) ----
    latest_date = df["Datum"].max()  # publication date for notes/stand
    latest_effective = df["effective_date"].max()  # fieldwork end for weighting

    # Zeitfenster: in der heissen Phase alte Umfragen ausblenden:
    window_days = WINDOW_HOT_DAYS if HOT_PHASE else WINDOW_COLD_DAYS
    cutoff_eff = latest_effective - pd.Timedelta(days=int(window_days))
    df_avg = df[df["effective_date"] >= cutoff_eff].copy()

    # Sequenzgewicht: pro Institut nur die neueste Umfrage voll zählen lassen
    if USE_POLLSTER_SEQ_WEIGHT:
        inst_col = institute_col  # Originalspalte aus der Tabelle
        # Sortierung: neueste effektive_date zuerst; Ties stabil auf Basis der Zeile
        df_avg = df_avg.sort_values([inst_col, "effective_date", "Datum"], ascending=[True, False, False]).copy()
        df_avg["_rank_inst"] = df_avg.groupby(inst_col).cumcount() + 1
        df_avg["_w_seq"] = np.power(2.0, 1.0 - df_avg["_rank_inst"].astype(float))
    else:
        df_avg["_w_seq"] = 1.0

    age_days = (latest_effective - df_avg["effective_date"]).dt.days.astype(float)
    w_time = np.power(0.5, age_days / HALF_LIFE_DAYS)

    fallback_n = float(np.nanmedian(df_avg["n"])) if pd.notna(np.nanmedian(df_avg["n"])) else 1000.0
    w_n = np.sqrt(pd.to_numeric(df_avg["n"], errors="coerce").fillna(fallback_n).clip(lower=200.0))

    w = w_time * w_n * pd.to_numeric(df_avg["_w_seq"], errors="coerce").fillna(1.0)

    avg = {}
    for p in parties_out:
        vals = pd.to_numeric(df_avg.get(p), errors="coerce")
        if vals is None:
            avg[p] = None
            continue

        rep_col = f"_reported_{p}"
        cen_col = f"_censored_{p}"
        cens_mask = df_avg[cen_col].fillna(False).astype(bool) if cen_col in df_avg.columns else pd.Series(False, index=df_avg.index)

        # Imputation: zensierte Werte (<U) werden als plausibler Erwartungswert (~2%) behandelt,
        # damit selten ausgewiesene Parteien nicht durch wenige hohe Beobachtungen verzerrt werden.
        vals_filled = vals.copy()
        vals_filled.loc[cens_mask & vals_filled.isna()] = float(U_CENSORED_EXPECTED)

        m = vals_filled.notna()
        if m.sum() == 0:
            avg[p] = None
        else:
            avg[p] = float(np.average(vals_filled[m], weights=w[m]))

    # ---- data.json schreiben (Schema fürs Balkendiagramm) ----
    survey_date = latest_date.strftime("%Y-%m-%d")

    parties_payload = []
    for p in parties_out:
        if avg.get(p) is None:
            continue

        # Erst mit Nachkommastelle rechnen, dann Differenz bilden, erst danach fürs Display runden (kaufmännisch)
        result_raw = round_half_up(float(avg[p]), 1)
        prev_raw = round_half_up(float(LAST_ELECTION.get(p, 0.0)), 1)

        change_raw = result_raw - prev_raw

        # Display: ganze Prozentpunkte (kaufmännisch)
        result_disp = int(round_half_up(result_raw, 0))
        prev_disp = int(round_half_up(prev_raw, 0))
        change_disp = int(round_half_up(change_raw, 0))

        parties_payload.append({
            "id": p,
            "result": result_disp,
            "previousResult": prev_disp,
            "change": change_disp,
            "color": party_colors.get(p, "#000000"),
        })

    # Parteien nach aktuellem Wert sortieren (absteigend)
    parties_payload.sort(key=lambda d: (d.get("result") is None, -(float(d.get("result")) if d.get("result") is not None else 0.0)))

    # Tabellen-Spaltenreihenfolge an Balkendiagramm ausrichten
    bar_order = [d["id"] for d in parties_payload if isinstance(d, dict) and d.get("id")]

    bar_payload = {
        "year": ELECTION_YEAR,
        "previousYear": PREVIOUS_ELECTION_YEAR,
        "surveyDate": survey_date,
        "parties": parties_payload,
    }

    bar_path = os.path.join(state_dir, "data.json")
    with open(bar_path, "w", encoding="utf-8") as f:
        json.dump(bar_payload, f, ensure_ascii=False, indent=1, allow_nan=False)

    print(f"JSON file '{bar_path}' has been created successfully.")

    # ---- Umfragetabelle ----
    table_df = df_table_source.copy()

    if "Datum" in table_df.columns:
        table_df["Datum"] = pd.to_datetime(table_df["Datum"], errors="coerce", format="%d.%m.%Y")

    if "n" not in table_df.columns:
        table_df["method"], table_df["n"] = zip(*table_df[befragte_col].apply(parse_method_code_and_n))
    else:
        missing_n = table_df["n"].isna()
        if missing_n.any():
            parsed_method_n = table_df.loc[missing_n, befragte_col].apply(parse_method_code_and_n)
            table_df.loc[missing_n, "method"] = [mn[0] for mn in parsed_method_n]
            table_df.loc[missing_n, "n"] = [mn[1] for mn in parsed_method_n]

    # Für die Tabelle dieselbe Parteien-Normalisierung wie im Haupt-df herstellen,
    # da df_table_source aus den rohen Wahlrecht-Zeilen gebaut wird.
    for src_col, party in PARTY_MAP.items():
        if src_col in table_df.columns:
            table_df[party] = table_df[src_col].apply(convert_percentage_to_float)
        else:
            table_df[party] = np.nan

    for extra_col in ["FW", "BSW"]:
        if extra_col in table_df.columns:
            table_df[extra_col] = table_df[extra_col].apply(convert_percentage_to_float)
        else:
            table_df[extra_col] = np.nan

    if sonstige_col in table_df.columns:
        for token, party in EMBEDDED_TOKENS.items():
            embedded_col = f"_tbl_embedded_{party}"
            table_df[embedded_col] = table_df[sonstige_col].apply(lambda x, t=token: extract_embedded_party(x, t))
            if party not in table_df.columns:
                table_df[party] = np.nan
            table_df[party] = table_df[party].where(table_df[party].notna(), table_df[embedded_col])

    # --- Institutsnamen normalisieren (wie Bundestag) ---
    institute_rename = {
        "INSA": "Insa",
        "Forschungsgruppe Wahlen": "FG Wahl.",
        "Verian": "Verian",
        "Allensbach": "Allensb.",
        "GMS": "GMS",
        "Infratest dimap": "Infratest",
        "Infratest": "Infratest",
        "Forsa": "Forsa",
    }

    def _norm_inst(x: str) -> str:
        if pd.isna(x):
            return ""
        s = str(x).strip()

        # Normalize whitespace and hyphenation artifacts from HTML line breaks, e.g.
        # "Forschungs-\ngruppe Wahlen" or "Forschungs- gruppe Wahlen".
        s = s.replace("\xa0", " ")
        s = re.sub(r"\s+", " ", s)
        s = re.sub(r"-\s+", "", s)  # remove hyphen + following whitespace
        s = s.strip()

        s_l = s.lower()

        # Match by prefix for common broken labels (e.g. starts with 'forschung')
        if s_l.startswith("forschung"):
            return "FG Wahl."

        # normalize common variants/case
        for k, v in institute_rename.items():
            if s_l == str(k).lower():
                return v
        return s

    table_df["Institut_clean"] = table_df[institute_col].apply(_norm_inst)

    # --- Feldzeitraum aus "Befragte" extrahieren (z.B. 23.2.–26.2.26) ---
    def _extract_zeitraum(befragte, datum) -> str:
        """Return fieldwork period like '23.2.–26.2.26' (no leading zeros, 2-digit year)."""
        if pd.isna(befragte) or pd.isna(datum):
            return ""

        s = str(befragte).replace("\xa0", " ")
        m = re.search(r"(\d{1,2})\.(\d{1,2})\.\s*[–-]\s*(\d{1,2})\.(\d{1,2})\.", s)
        if not m:
            return ""

        d1, m1, d2, m2 = (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
        yy = int(pd.to_datetime(datum).year) % 100

        return f"{d1}.{m1}.–{d2}.{m2}.{yy:02d}"

    table_df["Zeitraum"] = table_df.apply(lambda r: _extract_zeitraum(r.get(befragte_col, ""), r.get("Datum", pd.NaT)), axis=1)
    # Wahlzeilen in der Tabelle speziell behandeln: Label "Wahl", Datum anzeigen, keine Teilnehmerzahl.
    election_marker_mask_tbl = table_df[institute_col].astype(str).str.contains(ELECTION_CUTOFF_PATTERN, na=False)
    table_df["_is_election_row"] = election_marker_mask_tbl
    table_df["_election_marker_date"] = table_df[institute_col].apply(_extract_date_from_marker)

    def _fmt_institut_row(r):
        if bool(r.get("_is_election_row", False)):
            date_txt = ""
            try:
                d = r.get("_election_marker_date")
                if pd.notna(d):
                    d = pd.to_datetime(d)
                    date_txt = f"{int(d.day)}.{int(d.month)}.{int(d.year)}"
                elif pd.notna(r.get("Datum")):
                    d = pd.to_datetime(r.get("Datum"))
                    date_txt = f"{int(d.day)}.{int(d.month)}.{int(d.year)}"
            except Exception:
                date_txt = ""
            return "Wahl<br><span style=\"font-size: x-small; color: #69696c\">" + date_txt + "</span>"

        teiln = ""
        try:
            if pd.notna(r.get("n")):
                teiln = f"{int(r.get('n')):,}".replace(",", " ") + " Teiln."
        except Exception:
            teiln = ""

        return (
            str(r.get("Institut_clean", "")) + "<br>" +
            '<span style="font-size: x-small; color: #69696c">' +
            str(r.get("Zeitraum", "")) + "<br>" +
            teiln +
            "</span>"
        )

    table_df["Institut_fmt"] = table_df.apply(_fmt_institut_row, axis=1)

    # Tabelle nur für Parteien, die auch im aktuellen Balkendiagramm vorkommen
    # (also nur Parteien mit gültigem aktuellem Durchschnitt / bar_order).
    table_party_order = [p for p in bar_order if p in table_df.columns]

    wide_polls_table = table_df[["Institut_fmt"] + table_party_order].copy()
    wide_polls_table.rename(columns={"Institut_fmt": "Institut"}, inplace=True)
    # Tabellenkopf farbig einfärben
    formatted_columns = {
        p: f'<span style="color:{party_colors.get(p, "#000000")}">{p}</span>'
        for p in table_party_order
        if p != "Institut"
    }
    wide_polls_table.rename(columns=formatted_columns, inplace=True)

    def fmt_cell(x, color):
        if pd.isna(x):
            return ""

        # Accept already-numeric values and strings like '5 %' / '5,5 %'
        if isinstance(x, str):
            s0 = x.strip()
            if s0 in {"", "-", "—", "–"}:
                return ""
            s0 = s0.replace("%", "").replace(" ", "").replace("\xa0", "")
            s0 = s0.replace(",", ".")
            # handle censored markers
            if "<" in s0 or "≤" in s0:
                return ""
            try:
                x = float(s0)
            except Exception:
                return ""
        else:
            try:
                x = float(x)
            except Exception:
                return ""

        if float(x).is_integer():
            s = f"{int(round_half_up(x, 0)):,}".replace(",", " ") + "%"
        else:
            s = f"{round_half_up(x, 1):.1f}".replace(".", ",") + "%"
        return f'<span style="color:{color}">{s}</span>'

    for p in table_party_order:
        col = formatted_columns.get(p, p)
        c = party_colors.get(p, "#000000")
        if col in wide_polls_table.columns:
            wide_polls_table[col] = wide_polls_table[col].apply(lambda v, cc=c: fmt_cell(v, cc))

    wide_polls_table.set_index("Institut", inplace=True)
    notes_table = "Stand: " + latest_date.strftime("%-d. %-m. %Y")
    update_chart(id=Q_ID_TABLE, data=wide_polls_table, notes=notes_table)

    # ---- Koalitionen ----
    # Fixes Parteien-Set für das Koalitions-Widget (auch wenn Daten fehlen)
    party_metadata = {
        "CDU": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909830-658639605", "colorCode": party_colors["CDU"]},
        "CSU": {"id": "v9EU9SKJzMqKGfdPT0v48", "colorCode": party_colors["CSU"]},
        "SPD": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909830-820461104", "colorCode": party_colors["SPD"]},
        "Grüne": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909830-681841949", "colorCode": party_colors["Grüne"]},
        "FDP": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909831-568178765", "colorCode": party_colors["FDP"]},
        "Linke": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909831-21531609", "colorCode": party_colors["Linke"]},
        "AfD": {"id": "0d50b45e538faa45f768d3204450d0e7-1732636909831-211145954", "colorCode": party_colors["AfD"]},
        "BSW": {"id": "A6zt3iDyIxG96itQmrhJ3", "colorCode": party_colors["BSW"]},
        "FW": {"id": "0d50b45e538faa45f768d3204450d0e7-1732637074764-908994801", "colorCode": party_colors["FW"]},
    }

    # --- Koalitions-Templates automatisch erzeugen (Reihenfolge aus coalitions_spec) ---
    def write_coalition_templates():
        # Parteien, die Varianten-Dateien auslösen (z.B. FDP: Ampel nur, wenn FDP drin ist)
        switch_parties = [p for p in STATES[state_key].get("variant_parties", []) if p in party_metadata]
        spec = STATES[state_key].get("coalitions_spec", [])
        prune_bases = [set(x) for x in STATES[state_key].get("dedupe_bases", [])]

        name_to_id = {name: meta["id"] for name, meta in party_metadata.items()}

        from itertools import combinations

        # Alle Kombinationen: Partei drin/raus (für Varianten-Dateien)
        scenarios = []
        for r in range(0, len(switch_parties) + 1):
            for comb in combinations(switch_parties, r):
                scenarios.append(set(comb))

        for present_set in scenarios:
            suffix = "_" + "_".join(sorted([p.lower() for p in present_set])) if present_set else ""
            out_path = os.path.join(state_dir, f"coalitions{suffix}.json")

            out = []
            for c in spec:
                parties = c.get("parties", [])
                if not parties:
                    continue

                # Skip coalitions that require a switch party not present in this scenario
                if any((p in switch_parties and p not in present_set) for p in parties):
                    continue

                # Convert party names to ids; skip if any id is missing
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

            # Dedupe nur für definierte Basiskoalitionen (z.B. CDU+AfD unterdrücken, wenn CDU+AfD+FW existiert)
            if prune_bases and out:
                party_id_to_name = {meta["id"]: name for name, meta in party_metadata.items()}

                coal_sets = []
                for d in out:
                    names = set()
                    for obj in d.get("parties", []):
                        pid = obj.get("id") if isinstance(obj, dict) else None
                        if pid in party_id_to_name:
                            names.add(party_id_to_name[pid])
                    coal_sets.append(names)

                drop_idx = set()
                for i, si in enumerate(coal_sets):
                    if si in prune_bases:
                        for j, sj in enumerate(coal_sets):
                            if i == j:
                                continue
                            if si < sj:
                                extra = sj - si
                                # only prune if extras are switch parties present in this scenario
                                if extra and all((e in switch_parties and e in present_set) for e in extra):
                                    drop_idx.add(i)
                                    break

                if drop_idx:
                    out = [d for idx, d in enumerate(out) if idx not in drop_idx]

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)

    write_coalition_templates()

    TOTAL_SEATS = int(STATES[state_key].get("seats", 0))
    if TOTAL_SEATS <= 0:
        raise ValueError(f"Missing or invalid seats for {state_key}. Set STATES['{state_key}']['seats'].")
    MAJORITY = TOTAL_SEATS // 2 + 1

    latest_rolling_averages = pd.DataFrame({
        "Partei": parties_out,
        "average": [avg.get(k) for k in parties_out]
    }).dropna(subset=["average"]).reset_index(drop=True)

    # Party-specific mean CI (approx.) based on recent polls, analogous to Bundestag script
    # Compute per-row 95% CI half-width: 1.96 * sqrt(p*(1-p)/n) in percentage points.
    ci_rows = []
    for p in parties_out:
        # Use the raw poll values (not averaged) for CI estimation
        vals = pd.to_numeric(df.get(p), errors="coerce")
        ns = pd.to_numeric(df.get("n"), errors="coerce")
        dt_eff = pd.to_datetime(df.get("effective_date"), errors="coerce")

        tmp = pd.DataFrame({
            "Partei": p,
            "value": vals,
            "n": ns,
            "effective_date": dt_eff,
        }).dropna(subset=["value", "n", "effective_date"]).copy()

        if len(tmp) == 0:
            continue

        # n safety
        tmp = tmp[tmp["n"] > 0]
        if len(tmp) == 0:
            continue

        pr = (tmp["value"] / 100.0).clip(lower=0.0, upper=1.0)
        se = np.sqrt(pr * (1.0 - pr) / tmp["n"].astype(float))
        tmp["ci"] = 1.96 * se * 100.0
        ci_rows.append(tmp[["Partei", "effective_date", "ci"]])

    if ci_rows:
        ci_df = pd.concat(ci_rows, ignore_index=True)
        ci_df = ci_df.sort_values(["Partei", "effective_date"])

        # Use a time window instead of a fixed number of observations
        window_days = 90 if HOT_PHASE else 365
        max_obs = 10
        cutoff = ci_df["effective_date"].max() - pd.Timedelta(days=window_days)
        ci_df = ci_df[ci_df["effective_date"] >= cutoff]

        # Cap per party to the most recent observations within the window
        ci_recent = ci_df.groupby("Partei", as_index=False).tail(max_obs)

        mean_ci_per_party = (
            ci_recent.groupby("Partei", as_index=False)["ci"].mean()
            .rename(columns={"ci": "mean_ci"})
        )
    else:
        mean_ci_per_party = pd.DataFrame(columns=["Partei", "mean_ci"])

    # Conservative fallback if CI missing
    if len(mean_ci_per_party) == 0:
        mean_ci_per_party = pd.DataFrame({"Partei": parties_out, "mean_ci": [3.0] * len(parties_out)})
    else:
        mean_ci_per_party["mean_ci"] = pd.to_numeric(mean_ci_per_party["mean_ci"], errors="coerce").fillna(3.0)

    party_stats = latest_rolling_averages.merge(mean_ci_per_party, on="Partei", how="left")
    party_stats["mean_ci"] = pd.to_numeric(party_stats["mean_ci"], errors="coerce").fillna(3.0)
    party_stats["wacklig"] = (party_stats["average"] - 5.0).abs() <= party_stats["mean_ci"]

    in_base = party_stats.loc[party_stats["average"] >= 5.0, ["Partei", "average"]].set_index("Partei")["average"]
    in_low = party_stats.loc[(party_stats["average"] >= 5.0) & (~party_stats["wacklig"]), ["Partei", "average"]].set_index("Partei")["average"]
    in_high = party_stats.loc[(party_stats["average"] >= 5.0) | (party_stats["wacklig"]), ["Partei", "average"]].set_index("Partei")["average"]

    def _allocate_seats(avgs: pd.Series, total_seats: int = TOTAL_SEATS):
        """Sainte-Laguë/Schepers via highest-averages (Webster)."""
        seats_by_party = {p: 0 for p in party_metadata.keys()}

        if avgs is None or len(avgs) == 0:
            return seats_by_party

        avgs = pd.to_numeric(avgs, errors="coerce").dropna()
        avgs = avgs[avgs > 0]
        if len(avgs) == 0:
            return seats_by_party

        value_sum = float(avgs.sum())
        votes = (avgs / value_sum) * 100.0

        s = pd.Series(0, index=votes.index, dtype="int64")
        for _ in range(int(total_seats)):
            quot = votes / (2 * s + 1)
            m = quot.max()
            top = quot[quot == m].index
            if len(top) > 1:
                top_votes = votes.loc[top]
                mv = top_votes.max()
                top2 = top_votes[top_votes == mv].index
                winner = sorted(list(top2))[0]
            else:
                winner = top[0]
            s.loc[winner] += 1

        for p, seat_count in s.items():
            seats_by_party[str(p)] = int(seat_count)
        return seats_by_party

    seats_base = _allocate_seats(in_base)
    seats_low = _allocate_seats(in_low)
    seats_high = _allocate_seats(in_high)

    coalitionSeats = []
    for party_name, meta in party_metadata.items():
        coalitionSeats.append({
            "id": meta["id"],
            "color": {"colorCode": meta["colorCode"]},
            "name": party_name,
            "seats": int(seats_base.get(party_name, 0))
        })

    # Passende Koalitionsdatei anhand der Varianten-Parteien im Basisszenario wählen
    switch_parties = [p for p in STATES[state_key].get("variant_parties", []) if p in party_metadata]
    present = [p.lower() for p in switch_parties if int(seats_base.get(p, 0)) > 0]
    suffix = "_" + "_".join(sorted(present)) if present else ""
    coalition_file = os.path.join(state_dir, f"coalitions{suffix}.json")

    if not os.path.exists(coalition_file):
        raise FileNotFoundError(f"Missing coalition template: {coalition_file}")

    with open(coalition_file, "r", encoding="utf-8") as f:
        coalition_set = json.load(f)

    id_to_party = {meta["id"]: party for party, meta in party_metadata.items()}

    for c in coalition_set:
        party_ids = [p.get("id") for p in c.get("parties", []) if isinstance(p, dict)]
        party_names = [id_to_party.get(pid) for pid in party_ids]
        party_names = [p for p in party_names if p is not None]

        base_total = sum(int(seats_base.get(p, 0)) for p in party_names)
        low_total  = sum(int(seats_low.get(p, 0))  for p in party_names)
        high_total = sum(int(seats_high.get(p, 0)) for p in party_names)

        worst_total = min(low_total, high_total)
        best_total = max(low_total, high_total)

        # Stabil: hat bereits im Basisszenario eine Mehrheit und behaelt sie auch im schlechtesten Huerden-Szenario.
        if base_total >= MAJORITY and worst_total >= MAJORITY:
            label = "stabile Mehrheit"
        # Unrealistisch: selbst im guenstigsten Huerden-Szenario keine Mehrheit.
        elif best_total < MAJORITY:
            label = "Mehrheit unrealistisch"
        # Wackelig: Mehrheit haengt von Huerden-Szenarien ab (rein/raus von Parteien nahe 5%).
        else:
            label = "wackelige Mehrheit"

        name = c.get("name", "")
        if isinstance(name, str):
            if "«" in name and "»" in name:
                name_clean = re.sub(r"\s*«.*?»\s*", "", name).strip()
                c["name"] = f"{name_clean} {label}".strip()
            else:
                c["name"] = f"{name} {label}".strip()
        else:
            c["name"] = label

    notes_chart_seats_intro = (
        "Neueste Umfrage. " if len(df_avg) <= 1 else "Gewichteter Durchschnitt der neuesten Umfragen. "
    )
    notes_chart_seats = (
        notes_chart_seats_intro +
        "«Stabile/wackelige/unrealistische» Mehrheit geprüft anhand einer Modellrechnung für Parteien nahe der 5-Prozent-Hürde. "
        "Sitzverteilung gemäss Regelgrösse, ohne Berücksichtigung einer etwaigen Grundmandatsklausel. "
        "Stand: " + latest_date.strftime("%-d. %-m. %Y")
    )

    update_chart(
        id=Q_ID_COALITIONS,
        parties=coalitionSeats,
        possibleCoalitions=coalition_set,
        notes=notes_chart_seats
    )

    # Main-Chart: JSON-Datei als Asset setzen
    assets = [{
        "name": "jsonFiles",
        "assets": [
            {"path": bar_path},
        ]
    }]
    subtitle_main = f"NZZ-Wahltrend und Veränderung gegenüber der Wahl {PREVIOUS_ELECTION_YEAR}"
    if len(df_avg) <= 1:
        notes_main = "Neueste Umfrage. Stand: " + latest_date.strftime("%-d. %-m. %Y")
    else:
        notes_main = "Gewichteter Durchschnitt der neuesten Umfragen. Stand: " + latest_date.strftime("%-d. %-m. %Y")
    update_chart(id=Q_ID_MAIN_CUSTOM, assetGroups=assets, subtitle=subtitle_main, notes=notes_main)

    print(f"Done for {state_key}.")



# Working directory
os.chdir(os.path.dirname(__file__))


# ---- Run for all selected states ----
build_q_config(STATES_TO_RUN, TARGET_ENV)
for _state in STATES_TO_RUN:
    run_state(_state)
