"""FileManifest class."""

import logging
import sys

from forex_python.converter import CurrencyRates
from spring_manifest import models
from django.conf import settings

logger = logging.getLogger("file_manifest")


class FileManifest:
    """Base class for filing manifests."""

    def __init__(self, manifest):
        """File manifest."""
        self.currency_rates = self.get_currency_rates()
        self.manifest = manifest
        try:
            models.close_manifest(self.manifest)
            if self.manifest.closed is False:
                raise Exception
        except Exception as e:
            logger.error(
                "Manifest Error: %s", " ".join(sys.argv), exc_info=sys.exc_info()
            )
            self.manifest.errors = "Manifest did not close."
            raise e
        self.manifest.status = manifest.IN_PROGRESS
        self.manifest.errors = ""
        self.manifest.save()
        try:
            self.process_manifest()
        except Exception as e:
            self.add_error("An error occured.")
            logger.error(
                "Manifest Error: %s", " ".join(sys.argv), exc_info=sys.exc_info()
            )
            if settings.DEBUG:
                raise e

    def get_currency_rates(self):
        """Return dict of currency rates."""
        currency_converter = CurrencyRates()
        currency_codes = list(
            set(
                [
                    c.currency_code
                    for c in models.CloudCommerceCountryID.objects.all()
                    if c.currency_code is not None and c.currency_code != "GBP"
                ]
            )
        )
        return {c: currency_converter.get_rate(c, "GBP") for c in currency_codes}

    def file_manifest(self, manifest):
        """File manifest."""
        raise NotImplementedError

    def save_manifest_file(self, manifest, rows):
        """Save manifest file to database."""
        raise NotImplementedError

    def save_docket_file(self, *args, **kwargs):
        """Save docket file to database."""
        pass

    def save_item_advice_file(self, *args, **kwargs):
        """Save item advice file to database."""
        pass

    def add_error(self, message):
        """Add error message to manifest."""
        self.manifest.status = self.manifest.FAILED
        self.manifest.errors += "{}\n".format(message)
        self.manifest.save()

    def get_order_weight(self, order):
        """Return weight of order in KG."""
        weight_grams = sum(
            [product.per_item_weight * product.quantity for product in order.products]
        )
        weight_kg = weight_grams / 1000
        return weight_kg

    def convert_to_GBP(self, currency, amount):
        """Return amount converted from currency to GBP."""
        if currency is None or currency == "GBP":
            return round(amount, 2)
        rate = self.currency_rates[currency]
        converted_amount = amount * rate
        return round(converted_amount, 2)

    def send_file(self, manifest):
        """Send manifest file to shipping provider."""
        pass

    def valid(self):
        """Return True if manifest has no errors and is not marked failed."""
        return self.manifest.status != self.manifest.FAILED and not self.manifest.errors

    def cleanup(self):
        """Subclass this method to do things after manifest is filed."""
        pass
