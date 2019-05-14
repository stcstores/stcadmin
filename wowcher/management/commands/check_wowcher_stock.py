"""Get current stock levels for wowcher products and send alert emails."""

import datetime
import logging

from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from stcadmin import settings
from wowcher.wowcher_management import WowcherManager

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Get Wowcher orders command."""

    help = "Get current stock levels for wowcher products and send alert emails."

    def handle(self, *args, **options):
        """Get current stock levels for wowcher products and send alert emails."""
        try:
            alerts = WowcherManager.check_stock_levels()
            if len(alerts) > 0:
                message = self.create_message(alerts)
                send_mail(
                    f"Wowcher Stock Alerts {datetime.datetime.now().date()}.",
                    message,
                    settings.EMAIL_HOST_USER,
                    settings.WOWCHER_STOCK_ALERT_EMAIL,
                    fail_silently=False,
                )
        except Exception as e:
            logger.exception("Error getting stock levels for Wowcher orders.")
            raise e

    def create_message(self, alerts):
        """Return the message body for the alert email."""
        lines = [self.message_line(alert) for alert in alerts]
        return "\n".join(lines)

    def message_line(self, alert):
        """Return a line of text describing a stock alert."""
        if alert.stock_level > 0:
            return f"{alert.item.deal.name} - {alert.item.CC_SKU} has {alert.stock_level} left."
        else:
            return f"{alert.item.deal.name} - {alert.item.CC_SKU} is out of stock."
