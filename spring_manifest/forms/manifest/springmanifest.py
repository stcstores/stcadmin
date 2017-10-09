import csv
import datetime
import ftplib
import os

import xlsxwriter
from ccapi import CCAPI
from django.core.exceptions import ValidationError
from spring_manifest import models
from stcadmin import settings

from .errors import AddressError
from .locationcodes import get_iso_country_code


class SpringManifest(settings.SpringManifestSettings):
    login_url = settings.LOGIN_URL

    def __init__(self):
        self.errors = []
        self.manifested_orders = []
        self.previously_manifested = models.ManifestedOrder.order_ids()
        self.orders = self.get_orders()
        self.manifest = self.get_manifest(self.orders)

    @property
    def save_name(self):
        return 'SpringManifest_{}_{}'.format(
            self.name, self.get_date_string())

    def save_xlsx(self):
        filename = '{}.xlsx'.format(self.save_name)
        filepath = os.path.join(self.save_path, filename)
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet()
        for row_number, row in enumerate(self.get_file_rows()):
            for col_number, cell in enumerate(row):
                worksheet.write(row_number, col_number, cell)
        workbook.close()
        return filename

    def save_csv(self):
        filename = '{}.csv'.format(self.save_name)
        filepath = os.path.join(self.save_path, filename)
        with open(filepath, 'w', encoding='utf8') as save_file:
            writer = csv.writer(save_file, lineterminator='\n')
            writer.writerows(self.get_file_rows())
        return filename

    def is_valid(self):
        if len(self.errors) > 0:
            return False
        if len(self.missing_countrys) > 0:
            return False

    def get_date_string(self):
        return datetime.datetime.now().strftime('%Y-%m-%d')

    def file_manifest(self):
        raise NotImplementedError

    def get_orders(self):
        raise NotImplementedError

    def get_country(self, order, address):
        try:
            country = models.CloudCommerceCountryID.objects.get(
                cc_id=order.delivery_country_code)
        except models.CloudCommerceCountryID.DoesNotExist:
            self.add_missing_country(order, address)
            return None
        if not country.valid_spring_destination:
            self.add_error(
                'Destination Country invalid for order {}'.format(
                    order.order_id))
            return None
        if country.iso_code == '' or country.zone is None:
            return None
        return country

    def add_missing_country(self, order, address):
        iso_code = get_iso_country_code(order.delivery_country_code, address)
        country = models.CloudCommerceCountryID(
            cc_id=order.delivery_country_code, name=address.country)
        if iso_code is not None:
            country.iso_code = iso_code
        country.save()

    def request_orders(self, **kwargs):
        try:
            orders = CCAPI.get_orders_for_dispatch(**kwargs)
        except Exception:
            raise ValidationError('Error retriving orders.')
        else:
            return [
                o for o in orders if str(o.order_id) not in
                self.previously_manifested]

    def get_ftp(self):
        ftp = ftplib.FTP()
        try:
            ftp.connect(self.ftp_host, self.ftp_port)
        except Exception:
            self.add_error('Error connecting to FTP Server')
            return None
        try:
            ftp.login(self.ftp_user, self.ftp_pw)
        except Exception:
            self.add_error('Error loggin into FTP Server')
            return None
        return ftp

    def get_manifest(self, orders):
        self.rows = self.get_spreadsheet_rows(orders)

    def get_file_rows(self):
        return [self.write_header] + self.rows

    def add_error(self, message, field=None):
        self.errors.append(ValidationError(message))

    def get_spreadsheet_rows(self, orders):
        raise NotImplementedError

    def get_order_value(self, order):
        price = 0
        for product in order.products:
            price += float(product.price) * product.quantity
        return price

    def get_delivery_address(self, order):
        try:
            address = CCAPI.get_order_addresses(
                order.order_id, order.customer_id).delivery_address
        except Exception:
            self.add_error('Error getting addresses for order {}'.format(
                order.order_id))
        else:
            return address

    def clean_address_line(self, address):
        if len(address) <= 40:
            return [address]
        split_index = address[:40].rfind(' ')
        return [address[:split_index], address[split_index + 1:]]

    def get_phone_number(self, phone_number):
        if len(phone_number) < 5:
            return self.default_phone_number
        for char in str(phone_number):
            if not char.isdigit() or char in ('-', ' '):
                return self.default_phone_number
        return phone_number

    def clean_address(self, address):
        original_address = address.address
        stripped_address = [' '.join(a.split()) for a in original_address]
        clean_address = []
        for address_line in stripped_address:
            clean_address += self.clean_address_line(address_line)
        if len(clean_address) > 3 or any(
                a for a in clean_address if len(a) > 40):
            raise AddressError
        while len(clean_address) < 3:
            clean_address.append('')
        return clean_address

    def save_orders(self):
        for manifested_order in self.manifested_orders:
            manifested_order.save()
