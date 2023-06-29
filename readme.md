# OI Trader
OI Trader is a Python application that monitors the Open Interest (OI) to Market Cap (MCap) ratio of cryptocurrencies. It fetches data from the Coinglass and CoinGecko APIs, and sends alerts to a Discord channel when the OI/MCap ratio crosses certain thresholds.

## Features

1. **Token List Monitoring**: Monitors a list of tokens and their open interest to market cap ratio. Sends alerts when the ratio crosses certain thresholds.

2. **BTC Funding Rate Monitoring**: Monitors the funding rates of BTC across multiple exchanges (Binance, OKX, dYdX) and sends alerts when there is a significant change in the funding rate.

## How it Works

### Token List Monitoring

1. `initiate_token_list()`: Fetches the initial list of cryptocurrencies from Coinglass that have a market cap under 200 million USD or some predefined level. It uses the CoinGecko API to get the market cap data. The list of cryptocurrencies is saved in a JSON file.

2. `update_token_info()`: Scheduled to run every hour. Updates the OI data for each cryptocurrency in the list by calling the Coinglass API. It also calculates the OI/MCap ratio and updates the JSON file.

3. `alert_on_OI_mcap_ratio()`: Scheduled to run every hour. Checks the OI/MCap ratio for each cryptocurrency and sends an alert to a Discord channel if the ratio crosses a predefined threshold. It uses the `sending_OI_alert_to_discord()` function from the `external_services.py` script to send the alerts.

### BTC Funding Rate Monitoring

1. `update_btc_funding_data()`: Fetches the funding rates of BTC across Binance, OKX, and dYdX from the Coinglass API.

2. `alert_on_btc_funding_rate_change()`: Scheduled to run every hour at specific minutes. Checks the funding rates of BTC across multiple exchanges and sends alerts to a separate Discord subchannel if there is a significant change. The thresholds for alerting can be configured through environment variables.


## Setup
1. Clone the repository.

2. Install the required Python packages:
```pip install -r requirements.txt```

3. Set up the environment variables:

 - `COIN_GLASS_SECRET`: Your Coinglass API secret.
 - `OITRADER_DISCORD_ID`: Your Discord ID for sending alerts for Token List Monitoring.
 - `OITRADER_DISCORD_KEY`: Your Discord Key for sending alerts for Token List Monitoring.
 - `BTC_FUNDING_DISCORD_ID`: Your Discord ID for sending alerts for BTC Funding Rate Monitoring.
 - `BTC_FUNDING_DISCORD_KEY`: Your Discord Key for sending alerts for BTC Funding Rate Monitoring.
 - `BINANCE`: Binance funding rate thresholds (e.g. `[-0.15, 0.01]`).
 - `OKX`: OKX funding rate thresholds.
 - `DYDX`: dYdX funding rate thresholds.

You can set these variables in a .env file in the root directory of the project.


## JSON Data
The application stores the data for each cryptocurrency in a JSON file. Here is an example of the data:

```[
  {
    "symbol": "IOTX",
    "market_cap": 199692681,
    "open_interest": 9001465.9384,
    "last_update_time": "Fri Jun  9 13:10:01 2023",
    "oi_mcap_ratio": 0.04507659416120514,
    "threshold_alert": false,
    "half_threshold_alert": true
  },
  ...
]
```

Each object in the array represents a cryptocurrency. The properties are as follows:

- symbol: The symbol of the cryptocurrency.
- market_cap: The market cap of the cryptocurrency in USD.
- open_interest: The open interest of the cryptocurrency.
- last_update_time: The last time the data was updated.
- oi_mcap_ratio: The OI/MCap ratio.
- threshold_alert: A boolean indicating whether an alert has been sent for the OI/MCap ratio crossing the threshold.
- half_threshold_alert: A boolean indicating whether an alert has been sent for the OI/MCap ratio dropping below half the threshold.

For BTC Funding Rate Monitoring, the data is stored in a separate JSON file (btc_funding_data.json). Here is an example of the data:

json
Copy code
{
  "Binance": 0.004374,
  "OKX": 0.01314405142205,
  "dYdX": 0.01011688
}
This JSON file contains the latest funding rates for BTC across the monitored exchanges.


## Discord Alerts
Alerts are sent to Discord channels through webhooks. There are separate subchannels for Token List Monitoring and BTC Funding Rate Monitoring. Ensure that the Discord IDs and Keys are correctly set in the .env file.

## Scheduling
The scheduler script (scheduler.py) automates the monitoring process. It runs the Token List Monitoring functions and the BTC Funding Rate Monitoring function at regular intervals.

The BTC Funding Rate Monitoring function is scheduled to run every hour at the 9th, 21st, 33rd, 45th, and 57th minute.
