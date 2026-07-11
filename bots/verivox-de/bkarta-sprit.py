import os
import subprocess

import pandas as pd


DIESEL_SOURCE_ID = "1LsG8"
SUPER_SOURCE_ID = "QYUiG"

DIESEL_OUTPUT = "./data/node_diesel.csv"
SUPER_OUTPUT = "./data/node_super.csv"

DATE_COL = "meldedatum"
LOW_COL = "Durchschnitt unterstes Dezil"
HIGH_COL = "Durchschnitt oberstes Dezil"
MEAN_COL = "Mittlerer Preis"

NEW_Q_START_DATE = pd.Timestamp("2026-01-01")


def download_datawrapper_csv(source_id: str, output_path: str) -> None:
    """Download a Datawrapper dataset through dataunwrapper.js."""
    result = subprocess.run(
        ["node", "dataunwrapper.js", source_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    if result.returncode != 0:
        error = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Download der Datawrapper-Daten {source_id} fehlgeschlagen:\n{error}"
        )

    if not result.stdout:
        raise RuntimeError(
            f"Datawrapper-Datensatz {source_id} lieferte keine Daten."
        )

    with open(output_path, "wb") as file:
        file.write(result.stdout)


def prepare_fuel_data(file_path: str) -> pd.DataFrame:
    """Read and prepare the new Datawrapper fuel-price structure."""
    df = pd.read_csv(file_path)

    required_columns = [DATE_COL, LOW_COL, HIGH_COL, MEAN_COL]
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"In {file_path} fehlen folgende Spalten: "
            f"{', '.join(missing_columns)}"
        )

    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")

    for column in [LOW_COL, HIGH_COL, MEAN_COL]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=[DATE_COL, LOW_COL, HIGH_COL, MEAN_COL]
    )

    # Bei mehreren Einträgen für denselben Tag den letzten behalten.
    df = df.sort_values(DATE_COL)
    df = df.drop_duplicates(subset=DATE_COL, keep="last")
    df = df.set_index(DATE_COL)

    # Reihenfolge für das Q-Chart:
    # unterstes Dezil, oberstes Dezil, bundesweiter Mittelwert
    df = df[[LOW_COL, HIGH_COL, MEAN_COL]].copy()

    df = df.rename(
        columns={
            LOW_COL: "",
            HIGH_COL: "Höchster/tiefster Preis¹",
            MEAN_COL: "Bundesschnitt",
        }
    )

    return df


def format_price(price: float) -> str:
    """Format a price with two decimal places and German decimal comma."""
    return f"{price:.2f}".replace(".", ",")


if __name__ == "__main__":
    from helpers import update_chart

    # Set working directory to the script directory.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    os.makedirs("data", exist_ok=True)

    # Download current Datawrapper datasets.
    download_datawrapper_csv(DIESEL_SOURCE_ID, DIESEL_OUTPUT)
    download_datawrapper_csv(SUPER_SOURCE_ID, SUPER_OUTPUT)

    # Read and clean data.
    df_diesel = prepare_fuel_data(DIESEL_OUTPUT)
    df_super = prepare_fuel_data(SUPER_OUTPUT)

    # Use the most recent available date for the chart notes.
    latest_date = max(df_diesel.index.max(), df_super.index.max())
    timestamp_str = latest_date.strftime("%-d. %-m. %Y")

    notes_chart = (
        "¹ Durchschnitt oberstes und unterstes Dezil von rund "
        "15&nbsp;000 Tankstellen."
        f"<br>Stand: {timestamp_str}"
    )

    # Current prices for chart titles.
    price_d = format_price(df_diesel["Bundesschnitt"].iloc[-1])
    price_s = format_price(df_super["Bundesschnitt"].iloc[-1])

    title_chart_d = f"Diesel kostet im Schnitt {price_d} Euro je Liter"
    title_chart_s = f"Benzin kostet im Schnitt {price_s} Euro je Liter"

    # Existing Q charts.
    update_chart(
        id="458d885de84d6eb558874e221f294a93",
        data=df_diesel,
        title=title_chart_d,
        notes=notes_chart,
    )

    update_chart(
        id="458d885de84d6eb558874e221f2c09c0",
        data=df_super,
        title=title_chart_s,
        notes=notes_chart,
    )

    # New Q charts: show prices from 1 January 2026 onward.
    df_diesel_new_q = df_diesel.loc[df_diesel.index >= NEW_Q_START_DATE]
    df_super_new_q = df_super.loc[df_super.index >= NEW_Q_START_DATE]

    update_chart(
        id="c250129ff15f53bb0dc11bd295c817fe",
        data=df_diesel_new_q,
        title=title_chart_d,
        notes=notes_chart,
    )

    update_chart(
        id="11ce8401d5796bfe560bead197ce0d7e",
        data=df_super_new_q,
        title=title_chart_s,
        notes=notes_chart,
    )