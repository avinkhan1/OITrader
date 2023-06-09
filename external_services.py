import os
import logging

from dotenv import load_dotenv
from discord import SyncWebhook

logger = logging.getLogger()
load_dotenv()


def sending_OI_alert_to_discord(alert_content):
    try:
        webhook = SyncWebhook.partial(os.environ.get("OITRADER_DISCORD_ID"), os.environ.get('OITRADER_DISCORD_KEY'))
        webhook.send(alert_content)
    except Exception as error:
        logger.error("Exception returned when sending a message to discord from alt OI monitoring service:", error)
        return {'message': "Failed to contact backend service"}
