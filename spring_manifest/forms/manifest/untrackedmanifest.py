from spring_manifest import models

from .springmanifest import SpringManifest


class UnTrackedManifest(SpringManifest):

    name = 'UnTracked'

    spreadsheet_header = [
        'CustomerNumber', 'Customer Reference 1', 'Customer Reference 2',
        'PO Number', 'Quote Reference', 'Count items', 'Pre-franked',
        'Product Code', 'Nr satchels', 'Nr bags', 'Nr boxes', 'Nr pallets',
        'Destination code', 'Format code', 'Weightbreak from',
        'Weightbreak to', 'Nr items', 'Weight']

    write_header = [
        'CustomerNumber*', 'Customer Reference 1', 'Customer Reference 2',
        'PO Number', 'Quote Reference', 'Count items*', 'Pre-franked*',
        'Product Code*', 'Nr satchels', 'Nr bags', 'Nr boxes', 'Nr pallets',
        'Destination code*', 'Format code', 'Weightbreak from',
        'Weightbreak to', 'Nr items*', 'Weight (kg)*']

    def __init__(self, *args, **kwargs):
        self.download = None
        self.zones = models.DestinationZone.objects.all()
        self.zone_orders = {zone: [] for zone in self.zones}
        super().__init__(*args, **kwargs)

    def get_orders(self):
        return self.request_orders(courier_rule_id=9723)

    def save_manifest(self, manifest):
        return self.save_xlsx()

    def file_manifest(self):
        if len(self.rows) > 0:
            download_filename = self.save_manifest(self.manifest)
            self.download = self.url_path(download_filename)
            self.save_orders()

    def get_spreadsheet_rows(self, orders):
        for order in orders:
            address = self.get_delivery_address(order)
            country = self.get_country(order, address)
            if country is None:
                continue
            self.zone_orders[country.zone].append(order)
            manifested_order = models.ManifestedOrder(
                order_id=order.order_id, country=country,
                service_code='PAK')
            self.manifested_orders.append(manifested_order)
        return [
            self.get_row_for_zone(zone, orders) for zone, orders in
            self.zone_orders.items() if len(orders) > 0]

    def get_row_for_zone(self, zone, orders):
        products = []
        for order in orders:
            products += order.products
        weight = sum([product.per_item_weight for product in products]) / 1000
        data = {
            'CustomerNumber': self.customer_number,
            'Customer Reference 1': 'STC_STORES_{}_{}'.format(
                self.get_date_string(), zone.code),
            'Customer Reference 2': '',
            'PO Number': '',
            'Quote Reference': '',
            'Count items': 'N',
            'Pre-franked': 'N',
            'Product Code': '1MI',
            'Nr satchels': '1',
            'Nr bags': '1',
            'Nr boxes': '1',
            'Nr pallets': '1',
            'Destination code': zone.code,
            'Format code': '',
            'Weightbreak from': '',
            'Weightbreak to': '',
            'Nr items': str(len(orders)),
            'Weight': str(weight),
        }
        return [data[key] for key in self.spreadsheet_header]
