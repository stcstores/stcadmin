from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from spring_manifest import models
from stcadmin import settings
import csv
from collections import OrderedDict
import datetime
import io
import xlsxwriter
from django.core.files import File

from . views import SpringUserMixin


class FileManifest(SpringUserMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(
            models.SpringManifest, pk=manifest_id)
        if manifest.manifest_file:
            messages.add_message(
                self.request, messages.ERROR, 'Manifest already filed.')
        else:
            self.file_manifest(manifest)
        return reverse_lazy(
            'spring_manifest:manifest', kwargs={'manifest_id': manifest.id})

    def file_manifest(self, manifest):
        models.update_spring_orders()
        if manifest.manifest_type == manifest.TRACKED:
            self.file_tracked_manifest(manifest)
        elif manifest.manifest_type == manifest.UNTRACKED:
            self.file_untracked_manifest(manifest)

    def file_tracked_manifest(self, manifest):
        # TODO everything
        manifest.file_manifest()

    def file_untracked_manifest(self, manifest):
        self.zones = {}
        for order in manifest.springorder_set.all():
            zone = order.country.zone
            if zone not in self.zones:
                self.zones[zone] = []
            self.zones[zone].append(order)
        rows = [
            self.get_row_for_zone(zone, orders) for zone, orders in
            self.zones.items()]
        output = self.save_xlsx(manifest, rows)
        manifest.file_manifest()
        manifest.manifest_file.save(str(manifest) + '.xlsx', File(output))

    def save_xlsx(self, manifest, rows):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        for cell_number, col_header in enumerate(rows[0].keys()):
            worksheet.write(0, cell_number, col_header)
        for row_number, row in enumerate(rows, start=1):
            for col_number, cell in enumerate(row.values()):
                worksheet.write(row_number, col_number, cell)
        workbook.close()
        return output

    def save_csv(self, manifest, rows):
        output = io.StringIO(newline='')
        writer = csv.DictWriter(
            output, rows[0].keys(), delimiter=',', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
        return output

    def get_row_for_zone(self, zone, orders):
        customer_number = settings.SpringManifestSettings.customer_number
        products = []
        for order in orders:
            cc_order = order.get_order_data()
            products += cc_order.products
        weight_g = sum([
            product.per_item_weight * product.quantity for product in
            products])
        weight_kg = weight_g / 1000
        data = OrderedDict([
            ('CustomerNumber*', customer_number),
            ('Customer Reference 1', 'STC_STORES_{}_{}'.format(
                self.get_date_string(), zone.code)),
            ('Customer Reference 2', ''),
            ('PO Number', ''),
            ('Quote Reference', ''),
            ('Count items*', 'N'),
            ('Pre-franked*', 'N'),
            ('Product Code*', '1MI'),
            ('Nr satchels', '0'),
            ('Nr bags', len(self.zones)),
            ('Nr boxes', '0'),
            ('Nr pallets', '0'),
            ('Destination code*', zone.code),
            ('Format code', zone.format_code or ''),
            ('Weightbreak from', ''),
            ('Weightbreak to', ''),
            ('Nr items*', str(sum(order.package_count for order in orders))),
            ('Weight (kg)*', str(weight_kg)),
        ])
        return data

    def get_date_string(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')
