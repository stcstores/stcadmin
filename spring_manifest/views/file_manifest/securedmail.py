import csv
import datetime
import io
from collections import OrderedDict

from ccapi import CCAPI
from django.contrib import messages
from django.core.files.base import ContentFile
from unidecode import unidecode

from .file_manifest import FileManifest


class FileSecuredMailManifest(FileManifest):
    PROOF_OF_DELIVERY = {'SMIU': '', 'SMIT': 'T'}

    def get_manifest_rows(self, manifest):
        rows = []
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

    @staticmethod
    def save_manifest_file(manifest, rows):
        output = io.StringIO(newline='')
        writer = csv.DictWriter(
            output, rows[0].keys(), delimiter=',', lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(rows)
        manifest.file_manifest()
        manifest_string = unidecode(
            output.getvalue()).encode('utf-8', 'replace')
        manifest.manifest_file.save(
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
                ('Weight', weight),
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
        return int(product.per_item_weight * product.quantity)

    def add_success_messages(self, manifest):
        orders = manifest.springorder_set.all()
        package_count = sum(o.springpackage_set.count() for o in orders)
        order_count = len(orders)
        messages.add_message(
            self.request, messages.SUCCESS,
            'Manifest file created with {} packages for {} orders'.format(
                package_count, order_count))
