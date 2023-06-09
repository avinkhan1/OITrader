# OI Trader
OI Trader is a Python application that monitors the Open Interest (OI) to Market Cap (MCap) ratio of cryptocurrencies. It fetches data from the Coinglass and CoinGecko APIs, and sends alerts to a Discord channel when the OI/MCap ratio crosses certain thresholds.

## Features
Fetches a list of cryptocurrencies from Coinglass and CoinGecko APIs.
Calculates the OI/MCap ratio for each cryptocurrency.
Sends alerts to a Discord channel when the OI/MCap ratio crosses certain thresholds.
Uses a scheduler to update the data and check the ratios at regular intervals.

## How it Works
The application consists of three main parts:

initiate_token_list(): This function fetches the initial list of cryptocurrencies from Coinglass that have a market cap under 200 million USD or some predefined level. It uses the CoinGecko API to get the market cap data. The list of cryptocurrencies is saved in a JSON file.

update_token_info(): This function is scheduled to run every hour. It updates the OI data for each cryptocurrency in the list by calling the Coinglass API. It also calculates the OI/MCap ratio and updates the JSON file.

alert_on_OI_mcap_ratio(): This function is also scheduled to run every hour. It checks the OI/MCap ratio for each cryptocurrency and sends an alert to a Discord channel if the ratio crosses a predefined threshold. It uses the sending_OI_alert_to_discord() function from the external_services.py script to send the alerts.

## Setup
1. Clone the repository.

2. Install the required Python packages:
```pip install -r requirements.txt```

3. Set up the environment variables:

- COIN_GLASS_SECRET: Your Coinglass API secret.
- OITRADER_DISCORD_ID: Your Discord webhook ID.
- OITRADER_DISCORD_KEY: Your Discord webhook key.

You can set these variables in a .env file in the root directory of the project.

4. Run the main.py script to start the application:
```python main.py```


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