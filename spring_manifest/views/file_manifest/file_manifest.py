from forex_python.converter import CurrencyRates
from spring_manifest import models


class FileManifest:

    def __init__(self, manifest):
        self.currency_rates = self.get_currency_rates()
        self.manifest = manifest
        manifest.status = manifest.IN_PROGRESS
        manifest.errors = ''
        manifest.save()
        rows = self.get_manifest_rows(self.manifest)
        if self.valid():
            self.save_manifest_file(self.manifest, rows)
        if self.valid():
            self.send_file(manifest)
        if self.valid():
            self.manifest.status = self.manifest.FILED
            self.manifest.save()
        else:
            self.manifest.time_filed = None
            self.manifest.manifest_file = None
            self.manifest.status = self.manifest.FAILED
            self.manifest.save()

    def get_currency_rates(self):
        currency_converter = CurrencyRates()
        currency_codes = list(set([
            c.currency_code for c in
            models.CloudCommerceCountryID.objects.all() if c.currency_code
            is not None and c.currency_code != 'GBP']))
        return {
            c: currency_converter.get_rate(c, 'GBP') for c in currency_codes}

    def file_manifest(self, manifest):
        raise NotImplementedError

    def save_manifest_file(self, manifest, rows):
        raise NotImplementedError

    def add_error(self, message):
        self.manifest.status = self.manifest.FAILED
        self.manifest.errors += '{}\n'.format(message)
        self.manifest.save()

    def get_order_weight(self, order):
        weight_grams = sum([
            product.per_item_weight * product.quantity for product in
            order.products])
        weight_kg = weight_grams / 1000
        return weight_kg

    def convert_to_GBP(self, currency, amount):
        if currency is None or currency == 'GBP':
            return round(amount, 2)
        rate = self.currency_rates[currency]
        converted_amount = amount * rate
        return round(converted_amount, 2)

    def send_file(self, manifest):
        raise NotImplementedError

    def valid(self):
        return (
            self.manifest.status != self.manifest.FAILED and
            not self.manifest.errors)
