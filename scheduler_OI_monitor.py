import time
import datetime
import schedule

from main import alert_on_OI_mcap_ratio, update_token_info, initiate_token_list


def run_initiate_token_list():
    initiate_token_list()


def run_update_token_info():
    update_token_info()


def run_alert_on_OI_mcap_ratio():
    alert_on_OI_mcap_ratio(0.25)


# schedule the script to run at noon everyday
schedule.every().day.at("13:05").do(run_initiate_token_list)

# Schedule the script to run at 1:01 PM and 4:01 PM on weekdays
schedule.every().hour.at(":10").do(run_update_token_info)
schedule.every().hour.at(":15").do(run_alert_on_OI_mcap_ratio)




# Schedule the script to run immediately
# Uncomment the following line when testing
# schedule.every().minute.do(run_net_liquidity_script_immediately)

while True:
    schedule.run_pending()
    time.sleep(1)
