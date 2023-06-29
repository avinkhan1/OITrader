import os
import ast
import json

from dotenv import load_dotenv

from src.utilities.coinglass_helpers import get_funding_rate_data
from src.services.external_services import sending_BTC_funding_alert_to_discord

load_dotenv()

BTC_FUNDING_DATA_JSON = '../../btc_funding_data.json'
script_dir = os.path.dirname(os.path.abspath(__file__))
btc_funding_data_path = os.path.join(script_dir, BTC_FUNDING_DATA_JSON)

resolved_header = {
    "accept": "application/json",
    "coinglassSecret": f"{os.environ.get('COIN_GLASS_SECRET')}"
}

EXCHANGES = ['Binance', 'OKX', 'dYdX']


def range_with_floats(start, stop, step):
    while stop > start:
        yield start
        start += step

def update_btc_funding_data():
    funding_json = get_funding_rate_data()

    btc_funding_data = {}

    for item in funding_json['data']:
        if item['symbol'] == 'BTC':
            for component in item['uMarginList']:
                if component['exchangeName'] in EXCHANGES:
                    btc_funding_data[component['exchangeName']] = component['rate']

    return btc_funding_data


def get_list_of_alert_thresholds(start_increment_index, increment):
    funding_rate_alert_thresholds = []
    for i in range_with_floats(start_increment_index, (abs(start_increment_index) + increment), increment):
        funding_rate_alert_thresholds.append(i)
    middle_list_index = len(funding_rate_alert_thresholds)//2
    funding_rate_alert_thresholds.pop(middle_list_index)
    return funding_rate_alert_thresholds


def check_if_funding_change_requires_alert(exchange, funding_rate, last_funding_rate):
    exchange_values_literal = ast.literal_eval(os.environ.get(exchange.upper()))
    float_list = [float(element) for element in exchange_values_literal]
    lowest_funding_threshold = float_list[0]
    funding_increment = float_list[1]
    funding_rate_alert_thresholds = get_list_of_alert_thresholds(lowest_funding_threshold, funding_increment)

    message = None

    if funding_rate is None or last_funding_rate is None:
        return False, message

    direction = "increasing" if funding_rate > last_funding_rate else "decreasing"

    crossed_thresholds = []
    for threshold in funding_rate_alert_thresholds:
        if direction == "increasing":
            if last_funding_rate < threshold <= funding_rate:
                crossed_thresholds.append(threshold)
        else:
            if last_funding_rate > threshold >= funding_rate:
                crossed_thresholds.append(threshold)

    if crossed_thresholds:
        if direction == "increasing":
            message = f"{exchange} funding rate is {direction} from {last_funding_rate} to {funding_rate} and just crossed {max(crossed_thresholds)}"
            return True, message
        else:
            message = f"{exchange} funding rate is {direction} from {last_funding_rate} to {funding_rate} and just crossed {min(crossed_thresholds)}"
            return True, message

    return False, message


def alert_on_btc_funding_rate_change():
    try:
        with open(btc_funding_data_path, 'r') as f:
            last_funding_data = json.load(f)
    except FileNotFoundError:
        last_funding_data = {}

    new_funding_data = update_btc_funding_data()

    for exchange, funding_rate in new_funding_data.items():
        last_funding_rate = last_funding_data.get(exchange, None)
        alert_required, alert_message = check_if_funding_change_requires_alert(exchange, funding_rate, last_funding_rate)
        if alert_required:
            sending_BTC_funding_alert_to_discord(alert_message)
            # print(f"{alert_message}")

    with open(btc_funding_data_path, 'w') as file:
        json.dump(new_funding_data, file)

    return


# alert_on_btc_funding_rate_change()
