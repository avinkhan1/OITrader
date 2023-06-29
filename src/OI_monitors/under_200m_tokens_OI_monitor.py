import json
import os
import time
import requests

from dotenv import load_dotenv

from src.Enum.exchanges import Exchange
from src.utilities.coinglass_helpers import get_funding_rate_data
from src.services.external_services import sending_OI_alert_to_discord

load_dotenv()

TOKEN_OI_JSON = '../../token_data.json'
script_dir = os.path.dirname(os.path.abspath(__file__))
token_data_path = os.path.join(script_dir, TOKEN_OI_JSON)

resolved_header = {
    "accept": "application/json",
    "coinglassSecret": f"{os.environ.get('COIN_GLASS_SECRET')}"
}


def get_coingecko_data(threshold_mcap, top_tokens_to_evaluate):
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={top_tokens_to_evaluate}&page=1&sparkline=false&locale=en"
    response = requests.get(url)
    json_response = json.loads(response.text)

    # Filter out the symbols with a market cap of over 200M
    # filtered_symbols = [(item['symbol']).upper() for item in json_response if item['market_cap'] >= threshold_mcap]
    filtered_symbols_and_macp = [{'symbol': (item['symbol']).upper(), 'market_cap': item['market_cap']} for item in
                                 json_response if item['market_cap'] < threshold_mcap]

    return filtered_symbols_and_macp


def curate_tokenlist_under_threshold_mcap(threshold_mcap, top_tokens_to_evaluate, exchanges_to_match: list = None):
    coin_glass_funding_json = get_funding_rate_data()

    # Extract the symbols
    coin_glass_symbols = []
    if exchanges_to_match:
        for item in coin_glass_funding_json['data']:
            exchanges = [component['exchangeName'] for component in item['uMarginList'] if component['status'] == 1]
            if any(exchange in exchanges_to_match for exchange in exchanges):
                coin_glass_symbols.append(item['symbol'])
    else:
        coin_glass_symbols = [item['symbol'] for item in coin_glass_funding_json['data']]  # if item['uMarginList'][]]

    coingecko_symbols = get_coingecko_data(threshold_mcap, top_tokens_to_evaluate)

    # Get all the symbols that are common to both lists
    final_symbols = [symbol for symbol in coin_glass_symbols if symbol in [item['symbol'] for item in coingecko_symbols]]

    # Get the market cap for the final symbols
    final_symbols_with_market_cap = [item for item in coingecko_symbols if item['symbol'] in final_symbols]

    return final_symbols_with_market_cap


def get_open_interest(symbol):
    url = f"https://open-api.coinglass.com/public/v2/open_interest?symbol={symbol}"
    headers = resolved_header
    response = requests.get(url, headers=headers)
    response_json = json.loads(response.text)
    open_interest = response_json['data'][0]['openInterest']
    return open_interest


def populate_oi_for_tokens():
    with open(token_data_path, 'r') as f:
        token_data = json.load(f)

    for i, item in enumerate(token_data):
        symbol = item['symbol']
        open_interest_data = get_open_interest(symbol)
        item['open_interest'] = open_interest_data
        item['last_update_time'] = time.ctime()
        item['oi_mcap_ratio'] = item['open_interest'] / item['market_cap']

        with open(token_data_path, 'w') as f:
            json.dump(token_data, f)

        # If we've made 25 requests, sleep for 60 seconds
        if (i + 1) % 25 == 0:
            time.sleep(60)

    return token_data


def initiate_token_list():
    token_data = curate_tokenlist_under_threshold_mcap(200000000, 1000, [Exchange.BINANCE.value, Exchange.Bybit.value,
                                                                         Exchange.OKX.value])
    # Save the token data to a JSON file
    with open(token_data_path, 'w') as f:
        json.dump(token_data, f)


def update_token_info():
    populate_oi_for_tokens()


def alert_on_OI_mcap_ratio(initial_threshold_percentage, increment_percentage, decrement_percentage, minimum_threshold_percentage):
    try:
        with open(token_data_path, 'r') as f:
            token_data = json.load(f)
    except FileNotFoundError as e:
        print(f'Creating new json file for token data because could not find {token_data_path} file: {e}')
        initiate_token_list()
        update_token_info()

    initial_threshold = initial_threshold_percentage / 100.0
    increment_factor = 1 + (increment_percentage / 100.0)
    decrement_factor = 1 - (decrement_percentage / 100.0)
    minimum_threshold = minimum_threshold_percentage / 100.0

    for item in token_data:
        if not 'oi_mcap_ratio' in item:
            continue

        last_threshold = item.get('last_threshold', initial_threshold)

        if item['oi_mcap_ratio'] >= last_threshold * increment_factor:
            message = f'OI market cap ratio for {item["symbol"]} is up at {item["oi_mcap_ratio"]} which is over {increment_percentage} of the last alert threshold {last_threshold * 100}'
            sending_OI_alert_to_discord(message)
            print(message)
            item['last_threshold'] = item['oi_mcap_ratio']

        elif item['oi_mcap_ratio'] <= last_threshold * decrement_factor and item['oi_mcap_ratio'] >= minimum_threshold:
            message = f'OI market cap ratio for {item["symbol"]} has dropped to {item["oi_mcap_ratio"]} which is under {decrement_percentage} of the last alert threshold {last_threshold * 100}'
            sending_OI_alert_to_discord(message)
            print(message)
            item['last_threshold'] = item['oi_mcap_ratio']

    with open(token_data_path, 'w') as f:
        json.dump(token_data, f)


