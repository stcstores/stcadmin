import csv
import ftplib
import io
import os

import pycountry
from ccapi import CCAPI
from cloud_commerce.forms import SpringManifestForm
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from stcadmin import settings

from .views import CloudCommerceUserMixin


class SpringManifestSuccessView(CloudCommerceUserMixin, TemplateView):
    template_name = 'cloud_commerce/spring_manifest_success.html'


class SpringManifestView(
        CloudCommerceUserMixin, settings.SpringManifestSettings, FormView):
    login_url = settings.LOGIN_URL
    template_name = 'cloud_commerce/spring_manifest.html'
    form_class = SpringManifestForm
    success_url = reverse_lazy('cloud_commerce:spring_manifest_success')

    spreadsheet_header = [
        "Version #", "Shipper ID", "Package ID", "Weight", "Ship From Attn",
        "Ship From Name", "Ship From Address 1", "Ship From Address 2",
        "Ship From City", "Ship From State", "Ship From Zip5",
        "Ship From Country Code", "Ship To Attn", "Ship To Name",
        "Ship To Address 1", "Ship To Address 2", "Ship To Address 3",
        "Ship To City", "Ship To State", "Ship To Postal Code",
        "Ship To Country Code", "Recipient Phone Nbr", "Recipient Email",
        "Shipment Reference1", "Shipment Reference2", "Packaging Type",
        "Declared Value", "Service Code", "Length", "Width", "Height",
        "Line Item Quantity", "Line Item Code", "Line Item Description",
        "Line Item  Quantity Unit", "Unit Price", "Item Weight", "Weight Unit",
        "Price", "HS Code", "Country Of Manufacture", "Currency Code"]

    write_header = [
        "Version #", "Shipper ID", "Package ID", "Weight", "Ship From Attn",
        "Ship From Name", "Ship From Address 1", "Ship From Address 2",
        "Ship From City", "Ship From State", "Ship From Zip5",
        "Ship From Country Code", "Ship To Attn", "Ship To Name",
        "Ship To Address 1", "Ship To Address 2", "Ship To Address 3",
        "Ship To City", "Ship To State", "Ship To Postal Code",
        "Ship To Country Code", "Recipient Phone Nbr", "Recipient Email",
        "Shipment Reference1", "Shipment Reference2", "Packaging Type",
        "Declared Value", "Service Code", "Length", "Width", "Height",
        "Line Item Quantity", "Line Item Code", "Line Item Description",
        "Line Item  Quantity Unit", "Unit Price", "Weight", "Weight Unit",
        "Price", "HS Code", "Country Of Manufacture", "Currency Code"]

    country_codes = {
        '1': 'GB',
        '2': 'FR',
        '3': 'DE',
        '4': 'ES',
        '7': 'IT',
        '25': 'AU',
        '55': 'CA',
        '112': 'HU',
        '118': 'IE',
        '120': 'IS',
        '134': 'LV',
        '141': 'LU',
        '153': 'MX',
        '176': 'NO',
        '247': 'US',
    }

    state_codes = {
        'alaska': 'AK',
        'alabama': 'AL',
        'arkensas': 'AR',
        'american samoa': 'AS',
        'arizona': 'AZ',
        'california': 'CA',
        'colorado': 'CO',
        'conneticut': 'CT',
        'district of columbia': 'DC',
        'columbia': 'DC',
        'washington dc': 'DC',
        'dc': 'DC',
        'delaware': 'DE',
        'federated states of micronesia': 'FM',
        'miconesia': 'FM',
        'florida': 'FL',
        'georgia': 'GA',
        'guam': 'GU',
        'hawaii': 'HI',
        'iowa': 'IA',
        'idaho': 'ID',
        'illinois': 'IN',
        'kansas': 'KS',
        'kentucky': 'KY',
        'louisianna': 'LA',
        'massachusetts': 'MA',
        'maryland': 'MD',
        'maine': 'ME',
        'marshall islands': 'MH',
        'michigan': 'MI',
        'minnesota': 'MN',
        'missouri': 'MO',
        'northern amriana islands': 'MP',
        'mississippi': 'MS',
        'montana': 'MT',
        'north carolina': 'NC',
        'north dakota': 'ND',
        'nebraska': 'NE',
        'new hampshire': 'NH',
        'new jersey': 'NJ',
        'new mexcio': 'NM',
        'nevada': 'NV',
        'new york': 'NY',
        'ohio': 'OH',
        'oklahoma': 'OK',
        'oregon': 'OR',
        'pennsylvania': 'PA',
        'puerto rico': 'PR',
        'palau': 'PW',
        'rhode island': 'RI',
        'south carolina': 'SC',
        'south dakota': 'SD',
        'tennessee': 'TN',
        'texas': 'TX',
        'utah': 'UT',
        'virginia': 'VA',
        'virgin islands': 'VI',
        'vermont': 'VT',
        'washington': 'WA',
        'wisonsin': 'WI',
        'west virginia': 'WV',
        'wyoming': 'WY',
        'alberta': 'AB',
        'british colombia': 'BC',
        'british columbia': 'BC',
        'manitoba': 'MB',
        'new brunswick': 'NB',
        'newfoundland': 'NF',
        'nova scotia': 'NS',
        'northwest territories': 'NT',
        'ontario': 'ON',
        'prince edward island': 'PE',
        'quebec': 'QC',
        'saskatchewan': 'SK',
        'yukon': 'YT',
        'new south wales': 'NSW',
        'australian capital territory': 'ACT',
        'victoria': 'VIC',
        'queensland': 'QLD',
        'south australia': 'SA',
        'western australia': 'WA',
        'tasmania': 'TAS',
        'northern territory': 'NT',
    }

    def post(self, *args, **kwargs):
        self.form = self.get_form()
        self.manifest()
        if self.form.is_valid():
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    def get_phone_number(self, phone_number):
        if len(phone_number) < 5:
            return self.default_phone_number
        for char in str(phone_number):
            if not char.isdigit() or char in ('-', ' '):
                return self.default_phone_number
        return phone_number

    def manifest(self):
        orders = self.get_orders()
        manifest = self.get_manifest(orders)
        if self.form.is_valid():
            self.ftp_manifest(manifest)
            self.save_manifest(manifest)

    def ftp_manifest(self, manifest):
        manifest_string = manifest.getvalue().encode('utf8')
        manifest_file = io.BytesIO(manifest_string)
        ftp = self.get_ftp()
        if ftp is not None:
            try:
                ftp.cwd(self.ftp_dir)
            except Exception:
                self.add_error('Error getting FTP Directory')
                return
            try:
                ftp.storbinary(
                    'STOR {}'.format(self.ftp_filename), manifest_file)
            except Exception:
                self.add_error('Error saving file to FTP Server')

    def save_manifest(self, manifest):
        filepath = os.path.join(self.save_path, self.save_name)
        try:
            with open(filepath, 'w', encoding='utf8') as f:
                f.write(manifest.read())
        except Exception:
            self.add_error('Error saving local file')

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
        rows = self.get_spreadsheet_rows(orders)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(self.write_header)
        [writer.writerow(row) for row in rows]
        return output

    def add_error(self, message, field=None):
        self.form.add_error(field, message)

    def get_orders(self):
        manifest_type = self.form.data['manifest_type']
        if manifest_type == 'standard':
            self.package_code = 'PAK'
            kwargs = {}
        elif manifest_type == 'tracked':
            self.package_code = 'PAT'
            kwargs = {}
        elif manifest_type == 'parcel':
            self.package_code = 'PAR'
            kwargs = {}
        else:
            self.form.add_orders('Invalid Manifest Type')
            return []
        try:
            orders = CCAPI.get_orders_for_dispatch(**kwargs)
        except Exception:
            self.form.add_error(None, 'Error retriving orders.')
        else:
            return orders

    def get_spreadsheet_rows(self, orders):
        rows = []
        for order in orders:
            rows += self.get_rows_for_order(order)
        return rows

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

    def get_country_code(self, country_code, address):
        if country_code in self.country_codes:
            return self.country_codes[country_code]
        else:
            try:
                return pycountry.countries.get(name=address.country).alpha_2
            except KeyError:
                self.add_error('Missing Country Code: {}'.format(country_code))

    def get_state(self, state):
        if state.strip().lower() in self.state_codes:
            return self.state_codes[state.strip().lower()]
        if len(state) < 4:
            return state.upper()
        return state

    def clean_address_line(self, address):
        if len(address) <= 40:
            return [address]
        split_index = address[:40].rfind(' ')
        return [address[:split_index], address[split_index + 1:]]

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

    def get_rows_for_order(self, order):
        address = self.get_delivery_address(order)
        try:
            clean_address = self.clean_address(address)
        except AddressError as e:
            self.add_error(
                'Address line too long for order {}'.format(order.order_id))
            clean_address = ['', '', '']
        price = self.get_order_value(order)
        rows = []
        for product in order.products:
            data = {
                'Version #': '3.0',
                'Shipper ID': self.shipper_id,
                'Package ID': order.order_id,
                'Weight': round(order.predicted_order_weight / 1000, 3),
                'Ship From Attn': '',
                'Ship From Name': '',
                'Ship From Address 1': '',
                'Ship From Address 2': '',
                'Ship From City': '',
                'Ship From State': '',
                'Ship From Zip5': '',
                'Ship From Country Code': '',
                'Ship To Attn': address.delivery_name,
                'Ship To Name': address.delivery_name,
                'Ship To Address 1': clean_address[0],
                'Ship To Address 2': clean_address[1],
                'Ship To Address 3': clean_address[2],
                'Ship To City': address.town_city,
                'Ship To State': self.get_state(address.county_region),
                'Ship To Postal Code': address.post_code,
                'Ship To Country Code': self.get_country_code(
                    order.delivery_country_code, address),
                'Recipient Phone Nbr': self.get_phone_number(address.tel_no),
                'Recipient Email': '',
                'Shipment Reference1': '',
                'Shipment Reference2': '',
                'Packaging Type': 105,
                'Declared Value': price,
                'Service Code': self.package_code,
                'Length': '',
                'Width': '',
                'Height': '',
                'Line Item Quantity': product.quantity,
                'Line Item Code': product.sku,
                'Line Item Description': product.product_name,
                'Line Item  Quantity Unit': 'PCE',
                'Unit Price': product.price,
                'Item Weight': product.per_item_weight / 1000,
                'Weight Unit': 'KG',
                'Price': product.price * product.quantity,
                'HS Code': '',
                'Country Of Manufacture': 'CN',
                'Currency Code': 'GBP',
            }
            rows.append([data[key] for key in self.spreadsheet_header])
        return rows


class AddressError(Exception):
    pass
