"""FileManifest class."""

import os
import sys
import traceback

from forex_python.converter import CurrencyRates

from spring_manifest import models


class FileManifest:
    """Base class for filing manifests."""

    def __init__(self, manifest):
        """File manifest."""
        self.currency_rates = self.get_currency_rates()
        self.manifest = manifest
        self.manifest.status = manifest.IN_PROGRESS
        self.manifest.errors = ''
        self.manifest.save()
        try:
            self.process_manifest()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            tb = traceback.format_exception(None, e, e.__traceback__)
            self.add_error(
                'An error occured: {}\n{} {} {}\n{}'.format(
                    str(e), exc_type, fname, exc_tb.tb_lineno, tb))

    def process_manifest(self):
        """File manifest."""
        rows = self.get_manifest_rows(self.manifest)
        if self.valid():
            self.save_manifest_file(self.manifest, rows)
        if self.valid():
            self.save_item_advice_file(self.manifest, rows)
        if self.valid():
            self.save_docket_file(self.manifest, rows)
        if self.valid():
            self.send_file(self.manifest)
        if self.valid():
            self.manifest.status = self.manifest.FILED
            self.manifest.save()
            self.cleanup()
        else:
            self.manifest.time_filed = None
            self.manifest.manifest_file = None
            self.manifest.status = self.manifest.FAILED
            self.manifest.save()

    def get_currency_rates(self):
        """Return dict of currency rates."""
        currency_converter = CurrencyRates()
        currency_codes = list(set([
            c.currency_code for c in
            models.CloudCommerceCountryID.objects.all() if c.currency_code
            is not None and c.currency_code != 'GBP']))
        return {
            c: currency_converter.get_rate(c, 'GBP') for c in currency_codes}

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
        self.manifest.errors += '{}\n'.format(message)
        self.manifest.save()

    def get_order_weight(self, order):
        """Return weight of order in KG."""
        weight_grams = sum([
            product.per_item_weight * product.quantity for product in
            order.products])
        weight_kg = weight_grams / 1000
        return weight_kg

    def convert_to_GBP(self, currency, amount):
        """Return amount converted from currency to GBP."""
        if currency is None or currency == 'GBP':
            return round(amount, 2)
        rate = self.currency_rates[currency]
        converted_amount = amount * rate
        return round(converted_amount, 2)

    def send_file(self, manifest):
        """Send manifest file to shipping provider."""
        pass

    def valid(self):
        """Return True if manifest has no errors and is not marked failed."""
        return (
            self.manifest.status != self.manifest.FAILED and
            not self.manifest.errors)

    def cleanup(self):
        """Subclass this method to do things after manifest is filed."""
        pass
