import datetime
import io
from collections import OrderedDict

import xlsxwriter
from django.contrib import messages
from django.core.files import File
from stcadmin import settings

from .file_manifest import FileManifest


class FileUntrackedManifest(FileManifest):

    def get_manifest_rows(self, manifest):
        zones = {}
        for order in manifest.springorder_set.all():
            if not order.country.is_valid_destination():
                self.add_error(self.invalid_country_message(order))
                return None
            zone = order.country.zone
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(order)
        rows = [
            self.get_row_for_zone(zones, zone, orders) for zone, orders in
            zones.items()]
        return rows

    def invalid_country_message(self, order):
        return 'Order {}: Country {} info invalid.'.format(
            order, order.country)

    def send_file(self, manifest):
        pass

    @staticmethod
    def save_manifest_file(manifest, rows):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        for cell_number, col_header in enumerate(rows[0].keys()):
            worksheet.write(0, cell_number, col_header)
        for row_number, row in enumerate(rows, start=1):
            for col_number, cell in enumerate(row.values()):
                worksheet.write(row_number, col_number, cell)
        workbook.close()
        manifest.file_manifest()
        manifest.manifest_file.save(str(manifest) + '.xlsx', File(output))

    def get_row_for_zone(self, zones, zone, orders):
        customer_number = settings.SpringManifestSettings.customer_number
        customer_reference = 'STC_STORES_{}'.format(self.get_date_string())
        package_count = 0
        weight = 0
        for order in orders:
            cc_order = order.get_order_data()
            weight += self.get_order_weight(cc_order)
            package_count += order.springpackage_set.count()
            weight += 0.025 * package_count
        data = OrderedDict([
            ('CustomerNumber*', customer_number),
            ('Customer Reference 1', customer_reference),
            ('Customer Reference 2', ''),
            ('Special Requirements', ''),
            ('Quote Reference', ''),
            ('Count items*', 'N'),
            ('Pre-franked*', 'N'),
            ('Product Code*', '1MI'),
            ('Nr satchels', '0'),
            ('Nr bags', len(zones)),
            ('Nr boxes', '0'),
            ('Nr pallets', '0'),
            ('Destination code*', zone.code),
            ('Format code', zone.format_code or ''),
            ('Weightbreak from', ''),
            ('Weightbreak to', ''),
            ('Nr items*', str(package_count)),
            ('Weight (kg)*', str(round(weight, 2))),
        ])
        return data

    def get_date_string(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def add_success_messages(self, manifest):
        orders = manifest.springorder_set.all()
        package_count = sum(o.springpackage_set.count() for o in orders)
        order_count = len(orders)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Manifest file created with {} packages for {} orders'.format(
                package_count, order_count))
