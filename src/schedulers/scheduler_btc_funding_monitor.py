import time
import schedule

from src.OI_monitors.btc_funding_monitor import alert_on_btc_funding_rate_change


def run_alert_on_btc_funding_change():
    alert_on_btc_funding_rate_change()


# Scheduling like this to circumvent rate limits
schedule.every().hour.at(":09").do(run_alert_on_btc_funding_change)
schedule.every().hour.at(":21").do(run_alert_on_btc_funding_change)
schedule.every().hour.at(":33").do(run_alert_on_btc_funding_change)
schedule.every().hour.at(":45").do(run_alert_on_btc_funding_change)
schedule.every().hour.at(":57").do(run_alert_on_btc_funding_change)

#for testing
# schedule.every().minute.do(run_alert_on_btc_funding_change)


try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("Scheduler stopped by user")
