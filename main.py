import json
import os
import time
import requests

from enum import Enum
from dotenv import load_dotenv

from external_services import sending_OI_alert_to_discord

load_dotenv()


class Exchange(Enum):
    BINANCE = 'Binance'
    DYDX = 'dYdX'
    OKX = 'OKX'
    Huobi = 'Huobi'
    Bybit = 'Bybit'
    # Add more exchanges here as needed


def get_funding_rate_data(exchanges_to_match: list=None):
    url = "https://open-api.coinglass.com/public/v2/funding"
    headers = {
        'coinglassSecret': 'add3319b441046bd9f49210d96960407'
    }

    response = requests.request("GET", url, headers=headers)
    json_response = json.loads(response.text)

    # Extract the symbols
    symbols = []
    if exchanges_to_match:
        for item in json_response['data']:
            exchanges = [component['exchangeName'] for component in item['uMarginList'] if component['status'] == 1]
            if any(exchange in exchanges_to_match for exchange in exchanges):
                symbols.append(item['symbol'])
    else:
        symbols = [item['symbol'] for item in json_response['data']]#if item['uMarginList'][]]

    return symbols


def get_coingecko_data(threshold_mcap, top_tokens_to_evaluate):
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={top_tokens_to_evaluate}&page=1&sparkline=false&locale=en"
    response = requests.get(url)
    json_response = json.loads(response.text)

    # Filter out the symbols with a market cap of over 200M
    # filtered_symbols = [(item['symbol']).upper() for item in json_response if item['market_cap'] >= threshold_mcap]
    filtered_symbols_and_macp = [{'symbol': (item['symbol']).upper(), 'market_cap': item['market_cap']} for item in json_response if item['market_cap'] < threshold_mcap]

    return filtered_symbols_and_macp


def curate_tokenlist_under_threshold_mcap(threshold_mcap, top_tokens_to_evaluate, exchanges:list=None):
    coinglass_symbols = get_funding_rate_data(exchanges)
    coingecko_symbols = get_coingecko_data(threshold_mcap, top_tokens_to_evaluate)

    # Remove all the symbols that match symbols from CoinGecko with a market cap of over 200M
    # final_symbols = [symbol for symbol in coinglass_symbols if symbol not in coingecko_symbols]

    # Get all the symbols that are common to both lists
    final_symbols = [symbol for symbol in coinglass_symbols if symbol in [item['symbol'] for item in coingecko_symbols]]

    # Get the market cap for the final symbols
    final_symbols_with_market_cap = [item for item in coingecko_symbols if item['symbol'] in final_symbols]

    return final_symbols_with_market_cap


def get_open_interest(symbol):
    url = f"https://open-api.coinglass.com/public/v2/open_interest?symbol={symbol}"
    headers = {
        "accept": "application/json",
        "coinglassSecret": f"{os.environ.get('COIN_GLASS_SECRET')}"
    }

    response = requests.get(url, headers=headers)
    response_json = json.loads(response.text)
    open_interest = response_json['data'][0]['openInterest']
    return open_interest


def populate_oi_for_tokens():
    with open('token_data.json', 'r') as f:
        token_data = json.load(f)

    for i, item in enumerate(token_data):
        symbol = item['symbol']
        open_interest_data = get_open_interest(symbol)
        item['open_interest'] = open_interest_data
        item['last_update_time'] = time.ctime()
        item['oi_mcap_ratio'] = item['open_interest']/item['market_cap']

        with open('token_data.json', 'w') as f:
            json.dump(token_data, f)

        # If we've made 25 requests, sleep for 60 seconds
        if (i + 1) % 25 == 0:
            time.sleep(60)

    return token_data


def initiate_token_list():
    token_data = curate_tokenlist_under_threshold_mcap(200000000, 1000, [Exchange.BINANCE.value, Exchange.Bybit.value, Exchange.OKX.value])
    # Save the token data to a JSON file
    with open('token_data.json', 'w') as f:
        json.dump(token_data, f)


def update_token_info():
    populate_oi_for_tokens()


def alert_on_OI_mcap_ratio(threshold):
    with open('token_data.json', 'r') as f:
        token_data = json.load(f)

    for item in token_data:
        # skips loop if oi_mcap_ratio data is not available, useful if this function is running right after initiate_token_list and before update_token_info
        if not 'oi_mcap_ratio' in item:
            continue

        if item['oi_mcap_ratio'] >= threshold:
            if not 'threshold_alert' in item:
                item['threshold_alert'] = True
            if not item.get('threshold_alert', False):
                message = f'OI market cap ratio for {item["symbol"]} is up at {item["oi_mcap_ratio"]} which is over the threshold {threshold}'
                sending_OI_alert_to_discord(message)
                print(message)
            item['threshold_alert'] = True
            item['half_threshold_alert'] = False
        elif item['oi_mcap_ratio'] < threshold:
            item['threshold_alert'] = False

        if item['oi_mcap_ratio'] < threshold/2:
            if not 'half_threshold_alert' in item:
                item['half_threshold_alert'] = True
            if not item.get('half_threshold_alert', False):
                message = f'OI market cap ratio for {item["symbol"]} has dropped to {item["oi_mcap_ratio"]} which is under half of the threshold {threshold}'
                sending_OI_alert_to_discord(message)
                print(message)
            item['threshold_alert'] = False
            item['half_threshold_alert'] = True
        elif item['oi_mcap_ratio'] >= threshold/2:
            item['half_threshold_alert'] = False

    # Write the updated data back to the file
    with open('token_data.json', 'w') as f:
        json.dump(token_data, f)
