import csv
import datetime
import io
from collections import OrderedDict

import xlsxwriter
from django.contrib import messages
from django.core.files import File
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView
from spring_manifest import models
from stcadmin import settings

from .views import SpringUserMixin


class FileManifestView(SpringUserMixin, RedirectView):

    def get_manifest(self):
        manifest_id = self.kwargs['manifest_id']
        manifest = get_object_or_404(
            models.SpringManifest, pk=manifest_id)
        if manifest.manifest_file:
            messages.add_message(
                self.request, messages.ERROR, 'Manifest already filed.')
            return None
        return manifest

    def process_manifest(self):
        manifest = self.get_manifest()
        if manifest is not None:
            if manifest.manifest_type == manifest.UNTRACKED:
                FileUntrackedManifest(self.request, manifest)
            elif manifest.manifest_type == manifest.UNTRACKED:
                FileTrackedManifest(self.request, manifest)
            else:
                raise Exception(
                    'Unknown manifest type {} for manifest {}'.format(
                        manifest.manifest_type, manifest.id))

    def get_redirect_url(self, *args, **kwargs):
        self.process_manifest()
        return reverse_lazy(
                'spring_manifest:manifest',
                kwargs={'manifest_id': self.kwargs['manifest_id']})


class FileManifest:

    def __init__(self, request, manifest):
        self.request = request
        rows = self.get_manifest_rows(manifest)
        self.save_manifest_file(manifest, rows)
        self.add_messages(manifest)

    def file_manifest(self, manifest):
        raise NotImplementedError

    def save_manifest_file(self, manifest, rows):
        raise NotImplementedError

    def get_order_weight(self, order):
        weight_grams = sum([
            product.per_item_weight * product.quantity for product in
            order.products])
        weight_kg = weight_grams / 1000
        return weight_kg


class FileUntrackedManifest(FileManifest):

    def get_manifest_rows(self, manifest):
        zones = {}
        for order in manifest.springorder_set.all():
            zone = order.country.zone
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(order)
        rows = [
            self.get_row_for_zone(zones, zone, orders) for zone, orders in
            zones.items()]
        return rows

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
        products = []
        weight = 0
        item_count = 0
        for order in orders:
            cc_order = order.get_order_data()
            products += cc_order.products
            weight += self.get_order_weight(cc_order)
            item_count += order.package_count
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
            ('Nr bags', len(zones)),
            ('Nr boxes', '0'),
            ('Nr pallets', '0'),
            ('Destination code*', zone.code),
            ('Format code', zone.format_code or ''),
            ('Weightbreak from', ''),
            ('Weightbreak to', ''),
            ('Nr items*', str(item_count)),
            ('Weight (kg)*', str(weight)),
        ])
        return data

    def get_date_string(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def add_messages(self, manifest):
        orders = manifest.springorder_set.all()
        package_count = sum(o.package_count for o in orders)
        order_count = len(orders)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Manifest file created with {} packages for {} orders'.format(
                package_count, order_count))


class FileTrackedManifest(FileManifest):
    # TODO everything

    def save_manifest_file(self, manifest, rows):
        output = io.StringIO(newline='')
        writer = csv.DictWriter(
            output, rows[0].keys(), delimiter=',', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
        output.close()
        manifest.file_manifest()
        manifest.manifest_file.save(str(manifest) + '.csv', File(output))

    def add_messages(self, manifest):
        orders = manifest.springorder_set.all()
        package_count = sum(o.package_count for o in orders)
        order_count = len(orders)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Manifest filed with {} packages for {} orders'.format(
                package_count, order_count))
        services = {}
        for order in orders:
            if order.service not in services:
                services[order.service] = []
            services[order.service].append(order)
        for service, s_orders in services.items():
            package_count = sum(o.package_count for o in s_orders)
            order_count = len(s_orders)
            messages.add_message(
                self.request, messages.SUCCESS,
                '{} packages for {} orders with service code {}'.format(
                    package_count, order_count, service))
