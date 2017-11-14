from django.contrib import messages


class FileManifest:

    def __init__(self, request, manifest):
        self.valid = True
        self.request = request
        self.manifest = manifest
        rows = self.get_manifest_rows(self.manifest)
        if self.valid:
            self.save_manifest_file(self.manifest, rows)
        if self.valid:
            self.send_file(manifest)
        if self.valid:
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
        messages.add_message(self.request, messages.ERROR, message)

    def get_order_weight(self, order):
        weight_grams = sum([
            product.per_item_weight * product.quantity for product in
            order.products])
        weight_kg = weight_grams / 1000
        return weight_kg

    def send_file(self, manifest):
        raise NotImplementedError
