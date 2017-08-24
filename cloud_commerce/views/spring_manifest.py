import ftplib
import io
import os

from ccapi import CCAPI
from cloud_commerce.forms import SpringManifestForm
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from stcadmin import settings

from . views import CloudCommerceUserMixin


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
        '118': 'IE',
        '153': 'MX',
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
        manifest_file = io.BytesIO(manifest.encode('utf8'))
        ftp = self.get_ftp()
        if ftp is not None:
            try:
                ftp.cwd(self.ftp_dir)
            except Exception:
                self.add_error('Error getting FTP Directory')
                return
            try:
                ftp.storbinary(
                    'STOR {}'.format(self.ftp_filename()), manifest_file)
            except Exception:
                self.add_error('Error saveing file to FTP Server')

    def save_manifest(self, manifest):
        filepath = os.path.join(self.save_path(), self.save_name())
        try:
            with open(filepath, 'w', encoding='utf8') as f:
                f.write(manifest)
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
        manifest_rows = [self.write_header]
        manifest_rows += self.get_spreadsheet_rows(orders)
        manifest_string = '\n'.join(
            [','.join([str(cell) for cell in row]) for row in manifest_rows])
        return manifest_string

    def add_error(self, message, field=None):
        self.form.add_error(field, message)

    def get_orders(self):
        try:
            orders = CCAPI.get_orders_for_dispatch()
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
            addresses = CCAPI.get_order_addresses(
                order.order_id, order.customer_id).delivery_address
        except Exception:
            self.add_error('Error getting addresses for order {}'.format(
                order.order_id))
        else:
            return addresses

    def get_country_code(self, country_code):
        try:
            return self.country_codes[country_code]
        except KeyError:
            self.add_error('Missing Country Code: {}'.format(country_code))

    def get_state(self, state):
        if state.strip().lower() in self.state_codes:
            return self.state_codes[state.strip().lower()]
        if len(state) < 4:
            return state.upper()
        return state

    def get_rows_for_order(self, order):
        address = self.get_delivery_address(order)
        price = self.get_order_value(order)
        rows = []
        for product in order.products:
            data = {
                'Version #': 3,
                'Shipper ID': self.shipper_id,
                'Package ID': order.order_id,
                'Weight': order.predicted_order_weight / 1000,
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
                'Ship To Address 1': address.address[0],
                'Ship To Address 2': address.address[1],
                'Ship To Address 3': '',
                'Ship To City': address.town_city,
                'Ship To State': self.get_state(address.county_region),
                'Ship To Postal Code': address.post_code,
                'Ship To Country Code': self.get_country_code(
                    order.country_code),
                'Recipient Phone Nbr': self.get_phone_number(address.tel_no),
                'Recipient Email': '',
                'Shipment Reference1': '',
                'Shipment Reference2': '',
                'Packaging Type': 105,
                'Declared Value': price,
                'Service Code': 'PAK',
                'Length': '',
                'Width': '',
                'Height': '',
                'Line Item Quantity': product.quantity,
                'Line Item Code': product.sku,
                'Line Item Description': product.product_name,
                'Line Item  Quantity Unit': 'PCE',
                'Unit Price': product.price,
                'Item Weight': product.per_item_weight,
                'Weight Unit': 'G',
                'Price': product.price * product.quantity,
                'HS Code': '',
                'Country Of Manufacture': 'CN',
                'Currency Code': 'GB',
            }
            rows.append([data[key] for key in self.spreadsheet_header])
        return rows
