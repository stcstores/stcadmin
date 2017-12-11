from django.contrib import messages
from forex_python.converter import CurrencyRates


class FileManifest:

    def __init__(self, manifest, request=None):
        self.currency_converter = CurrencyRates()
        self.valid = True
        self.request = request
        self.manifest = manifest
        rows = self.get_manifest_rows(self.manifest)
        if self.valid:
            self.save_manifest_file(self.manifest, rows)
        if self.valid:
            self.send_file(manifest)
        if self.valid:
            if self.request:
                self.add_success_messages(self.manifest)
        else:
            self.manifest.time_filed = None
            self.manifest.manifest_file = None
            self.manifest.save()

    def file_manifest(self, manifest):
        raise NotImplementedError

    def save_manifest_file(self, manifest, rows):
        raise NotImplementedError

    def add_error(self, message):
        self.valid = False
        if self.request:
            messages.add_message(self.request, messages.ERROR, message)
        print(message)

    def get_order_weight(self, order):
        weight_grams = sum([
            product.per_item_weight * product.quantity for product in
            order.products])
        weight_kg = weight_grams / 1000
        return weight_kg

    def convert_to_GBP(self, currency, amount):
        if currency is None or currency == 'GBP':
            return round(amount, 2)
        converted_amount = self.currency_converter.convert(
            currency, 'GBP', amount)
        return round(converted_amount, 2)


    def send_file(self, manifest):
        raise NotImplementedError
