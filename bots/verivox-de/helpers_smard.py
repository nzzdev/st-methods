import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
import time
import pandas as pd
from io import StringIO
from user_agent import generate_user_agent

# retry if error
logging.basicConfig(level=logging.INFO)
s = requests.Session()
retries = Retry(total=10, backoff_factor=1,
                status_forcelist=[502, 503, 504])
s.mount('https://', HTTPAdapter(max_retries=retries))


# get unix timestamp in milliseconds
timestamp = int(time.time()) * 1000


def requestSmardData(  # request smard data with default values
    modulIDs=[8004169],
    timestamp_from_in_milliseconds=(int(time.time()) * 1000) - (3*3600)*1000,
    timestamp_to_in_milliseconds=(int(time.time()) * 1000),
    region="DE",
    language="de",
    type="discrete"
):

    # http request content
    headers = generate_user_agent()
    url = "https://www.smard.de/nip-download-manager/nip/download/market-data"
    body = json.dumps({
        "request_form": [
            {
                "format": "CSV",
                "moduleIds": modulIDs,
                "region": region,
                "timestamp_from": timestamp_from_in_milliseconds,
                "timestamp_to": timestamp_to_in_milliseconds,
                "type": type,
                "language": language
            }]})

    # http response
    data = s.post(url, body, headers={'user-agent': headers})

    # create pandas dataframe out of response string (csv)
    df = pd.read_csv(StringIO(data.text), sep=';')

    # convert rows with numbers to float (with wrong decimal)
    cols = df.filter(regex='.*\[MWh]$').columns
    df[cols] = df[cols].replace('-', '')

    return df
