"""
Update the currency exchange rates for the price calculator.

Command: python management.py update_exchange_rates
"""

import logging

import requests
from django.core.management.base import BaseCommand

from price_calculator.models import DestinationCountry

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Update price calculator currency exchange rates."""

    help = "Update price calculator currency exchange rates."

    def handle(self, *args, **kwargs):
        """Update price calculator currency exchange rates."""
        for country in DestinationCountry.objects.exclude(currency_code="GBP"):
            try:
                self.update_country(country)
            except Exception:
                pass

    def update_country(self, country):
        """Update the exchange rate for country."""
        try:
            new_rate = self.current_rate(country)
        except Exception as e:
            logger.exception(f"Error updating the exchange rate for {country}")
            raise e
        else:
            country.exchange_rate = new_rate
            country.save()

    def exchange_rates(self, country):
        """Return the current exchange rates for the country."""
        URL = f"https://api.exchangerate-api.com/v4/latest/{country.currency_code}"
        response = requests.get(URL)
        response.raise_for_status()
        return response.json()["rates"]

    def current_rate(self, country):
        """Return current currency conversion rate to GBP."""
        if country.currency_code == "GBP":
            return 1
        rates = self.exchange_rates(country)
        return rates["GBP"]
