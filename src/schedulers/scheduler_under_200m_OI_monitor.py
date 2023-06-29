import time
import schedule

from datetime import datetime

from src.OI_monitors.under_200m_tokens_OI_monitor import alert_on_OI_mcap_ratio, update_token_info, initiate_token_list


def run_initiate_token_list():
    initiate_token_list()


def run_update_token_info():
    update_token_info()


def run_alert_on_OI_mcap_ratio():
    alert_on_OI_mcap_ratio(90, 25, 25, 70)


schedule.every().day.at("13:05").do(run_initiate_token_list)
schedule.every().hour.at(":10").do(run_update_token_info)
schedule.every().hour.at(":15").do(run_alert_on_OI_mcap_ratio)

# Schedule the script to run immediately
# schedule.every().minute.do(run_alert_on_OI_mcap_ratio)

try:
    print(f"Under 200m tokens OI monitor starting at {datetime.now()}")
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Scheduler stopped by user")
