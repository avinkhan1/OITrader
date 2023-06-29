import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

resolved_header = {
    "accept": "application/json",
    "coinglassSecret": f"{os.environ.get('COIN_GLASS_SECRET')}"
}


def get_funding_rate_data():
    url = "https://open-api.coinglass.com/public/v2/funding"
    headers = resolved_header

    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)
