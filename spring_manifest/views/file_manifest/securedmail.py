import csv
import datetime
import io
import os
from collections import OrderedDict

import openpyxl
from ccapi import CCAPI
from django.contrib import messages
from django.core.files import File
from django.core.files.base import ContentFile
from unidecode import unidecode

from spring_manifest import models

from .file_manifest import FileManifest


class FileSecuredMailManifest(FileManifest):
    PROOF_OF_DELIVERY = {'SMIU': '', 'SMIT': 'T'}
    TEMPLATE_FILENAME = 'secure_mail_manifest_template.xlsx'
    MANIFEST_TEMPLATE_PATH = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), TEMPLATE_FILENAME)
    ITEM_COL = 'M'
    WEIGHT_COL = 'N'
    REFERENCE_CELL = 'J3'
    DATE_CELL = 'O3'

    def get_manifest_rows(self, manifest):
        rows = []
        self.country_weights = {
            dest: [] for dest in models.SecuredMailDestination.objects.all()}
        for order in manifest.springorder_set.all():
            try:
                rows += self.get_row_for_order(order)
            except Exception as e:
                self.add_error('Problem with order {}.\n{}'.format(
                    order.order_id, e))
                return
        return rows

    def invalid_country_message(self, order):
        return 'Order {}: Country {} info invalid.'.format(
            order, order.country)

    def send_file(self, manifest):
        pass

    def save_manifest_file(self, manifest, rows):
        wb = openpyxl.load_workbook(filename=self.MANIFEST_TEMPLATE_PATH)
        ws = wb.active
        total_items = 0
        total_weight = 0
        for country, weights in self.country_weights.items():
            country_items = len(weights)
            country_weight = sum(weights)
            total_items += country_items
            total_weight += country_weight
            row = str(country.manifest_row_number)
            ws[self.ITEM_COL + row] = country_items
            ws[self.WEIGHT_COL + row] = country_weight
        ws[self.REFERENCE_CELL] = str(manifest)
        ws[self.DATE_CELL] = datetime.datetime.now().strftime('%Y/%m/%d')
        output = io.BytesIO(openpyxl.writer.excel.save_virtual_workbook(wb))
        manifest.manifest_file.save(
            str(manifest) + '_manifest.xlsx', File(output))

    def save_item_advice_file(self, manifest, rows):
        output = io.StringIO(newline='')
        writer = csv.DictWriter(
            output, rows[0].keys(), delimiter=',', lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(rows)
        manifest.file_manifest()
        manifest_string = unidecode(
            output.getvalue()).encode('utf-8', 'replace')
        manifest.item_advice_file.save(
            str(manifest) + '.csv',
            ContentFile(manifest_string), save=True)
        output.close()

    def get_order_address(self, order):
        address = self.get_delivery_address(order)
        address.clean_address = self.clean_address(order, address)
        return address

    def get_order_product(self, item, cc_order):
        for product in cc_order.products:
            if int(product.product_id) == item.item_id:
                return product
        self.add_error('Product {} not found for order {}'.format(
            item.sku, cc_order.order_id))

    def get_delivery_address(self, order):
        try:
            address = CCAPI.get_order_addresses(
                order.order_id, order.customer_id).delivery_address
        except Exception:
            self.add_error('Error getting addresses for order {}'.format(
                order.order_id))
        else:
            return address

    def get_row_for_order(self, order):
        cc_order = order.get_order_data()
        address = self.get_order_address(cc_order)
        country = order.country
        if not country.is_valid_destination():
            self.add_error(
                'Invalid destination country {} for order {}.'.format(
                    country.name, order.order_id))
        price = self.get_order_value(cc_order, country.currency_code)
        rows = []
        packages = order.springpackage_set.all()
        for package in packages:
            items = [i for i in package.springitem_set.all() if i.quantity > 0]
            description = []
            price = 0
            quantity = 0
            weight = 0
            for item in items:
                product = self.get_order_product(item, cc_order)
                description.append(product.product_name)
                price += self.convert_to_GBP(
                    country.currency_code, product.price)
                quantity += item.quantity
                weight += self.get_product_weight(product)
            self.country_weights[
                country.secured_mail_destination].append(
                    round(weight / 1000, 2))
            data = OrderedDict([
                ('RecipientName', address.delivery_name),
                ('Addr1', address.clean_address[0]),
                ('Addr2', address.clean_address[1]),
                ('Addr3', address.clean_address[2]),
                ('Town', address.town_city),
                ('Country', ''),
                ('Postcode', address.post_code or ' '),
                ('Item Description', ', '.join(description)),
                ('Item Quantity', quantity),
                ('Item Value', price),
                ('Weight', int(weight)),
                ('Format', 'P'),
                ('Client Item Reference', str(package)),
                ('CountryCode', country.iso_code),
                ('Proof of Delivery', self.PROOF_OF_DELIVERY[order.service])])
            rows.append(data)
        return rows

    def clean_address(self, order, address):
        original_address = address.address
        clean_address = [' '.join(a.split()) for a in original_address]
        while len(clean_address) < 3:
            clean_address.append('')
        return clean_address

    def get_order_value(self, order, currency_code=None):
        price = 0
        for product in order.products:
            price += float(product.price) * product.quantity
        if currency_code is None:
            return int(price)
        return int(self.convert_to_GBP(currency_code, price))

    def get_date_string(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def get_product_weight(self, product):
        return product.per_item_weight * product.quantity

    def add_success_messages(self, manifest):
        orders = manifest.springorder_set.all()
        package_count = sum(o.springpackage_set.count() for o in orders)
        order_count = len(orders)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Manifest file created with {} packages for {} orders'.format(
                package_count, order_count))
