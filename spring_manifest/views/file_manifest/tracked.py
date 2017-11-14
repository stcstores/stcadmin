import os
import csv
import ftplib
import io
from collections import OrderedDict

from ccapi import CCAPI
from django.contrib import messages
from django.core.files.base import ContentFile
from stcadmin import settings
from unidecode import unidecode

from .file_manifest import FileManifest
from .state_code import StateCode


class FileTrackedManifest(FileManifest):

    def send_file(self, manifest):
        if self.valid:
            self.ftp_manifest(manifest)

    def get_manifest_rows(self, manifest):
        rows = []
        for order in manifest.springorder_set.all():
            try:
                rows += self.get_rows_for_order(order)
            except Exception as e:
                self.add_error('Problem with order {}.\n{}'.format(
                    order.order_id, e))
                return
        return rows

    def save_manifest_file(self, manifest, rows):
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

    def add_success_messages(self, manifest):
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
        messages.add_message(
            self.request, messages.SUCCESS,
            'Manifest file uploaded to {}.'.format(
                settings.SpringManifestSettings.ftp_host))

    def get_rows_for_order(self, order):
        cc_order = order.get_order_data()
        shipper_id = settings.SpringManifestSettings.shipper_id
        address = self.get_order_address(cc_order)
        country = order.country
        if not country.is_valid_destination():
            self.add_error(
                'Invalid destination country {} for order {}.'.format(
                    country.name, order.order_id))
        price = self.get_order_value(cc_order)
        rows = []
        for product in cc_order.products:
            data = OrderedDict([
                ('Version #', '3.0'),
                ('Shipper ID', shipper_id),
                ('Package ID', order.order_id),
                ('Weight', round(self.get_order_weight(cc_order), 3)),
                ('Ship From Attn', ''),
                ('Ship From Name', ''),
                ('Ship From Address 1', ''),
                ('Ship From Address 2', ''),
                ('Ship From City', ''),
                ('Ship From State', ''),
                ('Ship From Zip5', ''),
                ('Ship From Country Code', ''),
                ('Ship To Attn', address.delivery_name),
                ('Ship To Name', address.delivery_name),
                ('Ship To Address 1', address.clean_address[0]),
                ('Ship To Address 2', address.clean_address[1]),
                ('Ship To Address 3', address.clean_address[2]),
                ('Ship To City', address.town_city),
                ('Ship To State', StateCode(
                    address.county_region) or order.country.iso_code),
                ('Ship To Postal Code', address.post_code or ' '),
                ('Ship To Country Code', country.iso_code),
                ('Recipient Phone Nbr', self.get_phone_number(address.tel_no)),
                ('Recipient Email', ''),
                ('Shipment Reference1', ''),
                ('Shipment Reference2', ''),
                ('Packaging Type', 105),
                ('Declared Value', price),
                ('Service Code', str(order.service)),
                ('Length', ''),
                ('Width', ''),
                ('Height', ''),
                ('Line Item Quantity', product.quantity),
                ('Line Item Code', product.sku),
                ('Line Item Description', product.product_name),
                ('Line Item  Quantity Unit', 'PCE'),
                ('Unit Price', product.price),
                ('Item Weight', self.get_product_weight(product)),
                ('Weight Unit', 'KG'),
                ('Price', product.price * product.quantity),
                ('HS Code', ''),
                ('Country Of Manufacture', 'CN'),
                ('Currency Code', 'GBP')])
            rows.append(data)
        return rows

    def get_product_weight(self, product):
        weight_g = product.per_item_weight * product.quantity
        weight_kg = weight_g / 1000
        return round(weight_kg, 3)

    def get_phone_number(self, phone_number):
        if len(phone_number) < 5:
            return settings.SpringManifestSettings.default_phone_number
        for char in str(phone_number):
            if not char.isdigit() or char in ('-', ' '):
                return settings.SpringManifestSettings.default_phone_number
        return phone_number

    def get_order_address(self, order):
        address = self.get_delivery_address(order)
        address.clean_address = self.clean_address(order, address)
        return address

    def get_delivery_address(self, order):
        try:
            address = CCAPI.get_order_addresses(
                order.order_id, order.customer_id).delivery_address
        except Exception:
            self.add_error('Error getting addresses for order {}'.format(
                order.order_id))
        else:
            return address

    def clean_address(self, order, address):
        original_address = address.address
        stripped_address = [' '.join(a.split()) for a in original_address]
        clean_address = []
        for address_line in stripped_address:
            clean_address += self.clean_address_line(address_line)
        if len(clean_address) > 3 or any(
                a for a in clean_address if len(a) > 40):
            self.add_error(
                'Address too long for order {}'.format(order.order_id))
            return ['', '', '']
        while len(clean_address) < 3:
            clean_address.append('')
        return clean_address

    def clean_address_line(self, address):
        if len(address) <= 40:
            return [address]
        split_index = address[:40].rfind(' ')
        return [address[:split_index], address[split_index + 1:]]

    def get_order_value(self, order):
        price = 0
        for product in order.products:
            price += float(product.price) * product.quantity
        return price

    def get_ftp(self):
        ftp = ftplib.FTP()
        try:
            ftp.connect(
                settings.SpringManifestSettings.ftp_host,
                settings.SpringManifestSettings.ftp_port)
        except Exception:
            self.add_error('Error connecting to FTP Server')
            return None
        try:
            ftp.login(
                settings.SpringManifestSettings.ftp_user,
                settings.SpringManifestSettings.ftp_pw)
        except Exception:
            self.add_error('Error loggin into FTP Server')
            return None
        ftp.set_pasv(False)
        return ftp

    def ftp_manifest(self, manifest):
        ftp = self.get_ftp()
        if not self.valid:
            return
        try:
            ftp.cwd(settings.SpringManifestSettings.ftp_dir)
        except Exception as e:
            self.add_error('Error getting FTP Directory')
            return
        try:
            manifest.manifest_file.open()
            ftp.storbinary(
                'STOR {}'.format(
                    os.path.basename(manifest.manifest_file.name)),
                manifest.manifest_file)
            manifest.manifest_file.close()
        except Exception as e:
            raise e
            self.add_error('Error saving file to FTP Server')
