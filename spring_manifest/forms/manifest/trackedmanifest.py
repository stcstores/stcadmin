import os

from spring_manifest import models

from .errors import AddressError
from .locationcodes import get_state
from .springmanifest import SpringManifest


class TrackedManifest(SpringManifest):

    name = 'Tracked'

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

    @property
    def ftp_filename(self):
        return 'STCManifest_{}_{}.csv'.format(
            self.name, self.get_date_string())

    def get_orders(self):
        self.tracked_orders = self.get_tracked_orders()
        self.heavy_orders = self.get_heavy_orders()
        return self.tracked_orders + self.heavy_orders

    def get_tracked_orders(self):
        return self.request_orders(courier_rule_id=9590)

    def get_heavy_orders(self):
        return self.request_orders(courier_rule_id=9596)

    def file_manifest(self):
        if len(self.rows) > 0:
            self.saved_file = self.save_manifest()
            self.ftp_manifest(self.saved_file)
            self.save_orders()

    def ftp_manifest(self, filename):
        file_path = os.path.join(self.save_path, filename)
        with open(file_path, 'rb') as upload_file:
            ftp = self.get_ftp()
            if ftp is not None:
                try:
                    ftp.cwd(self.ftp_dir)
                except Exception:
                    self.add_error('Error getting FTP Directory')
                    return
                try:
                    ftp.storbinary(
                        'STOR {}'.format(self.ftp_filename), upload_file)
                except Exception:
                    self.add_error('Error saving file to FTP Server')

    def get_spreadsheet_rows(self, orders):
        rows = []
        for order in orders:
            rows += self.get_rows_for_order(order)
        return rows

    def save_manifest(self):
        return self.save_csv()

    def get_country_code(self, order, address):
        country = self.get_country(order, address)
        if country is None:
            return 'ERROR'
        return country.iso_code

    def get_order_address(self, order):
        address = self.get_delivery_address(order)
        try:
            address.clean_address = self.clean_address(address)
        except AddressError as e:
            self.add_error(
                'Address line too long for order {}'.format(order.order_id))
            address.clean_address = ['', '', '']
        return address

    def get_rows_for_order(self, order):
        address = self.get_order_address(order)
        country = self.get_country(order, address)
        price = self.get_order_value(order)
        if order in self.tracked_orders:
            package_code = 'PAT'
        else:
            package_code = 'PAR'
        rows = []
        for product in order.products:
            data = {}
            data['Version #'] = '3.0'
            data['Shipper ID'] = self.shipper_id
            data['Package ID'] = order.order_id
            data['Weight'] = round(order.predicted_order_weight / 1000, 3)
            data['Ship From Attn'] = ''
            data['Ship From Name'] = ''
            data['Ship From Address 1'] = ''
            data['Ship From Address 2'] = ''
            data['Ship From City'] = ''
            data['Ship From State'] = ''
            data['Ship From Zip5'] = ''
            data['Ship From Country Code'] = ''
            data['Ship To Attn'] = address.delivery_name
            data['Ship To Name'] = address.delivery_name
            data['Ship To Address 1'] = address.clean_address[0]
            data['Ship To Address 2'] = address.clean_address[1]
            data['Ship To Address 3'] = address.clean_address[2]
            data['Ship To City'] = address.town_city
            data['Ship To State'] = get_state(address.county_region)
            data['Ship To Postal Code'] = address.post_code
            if country is not None:
                data['Ship To Country Code'] = country.iso_code
            else:
                data['Ship To Country Code'] = 'ERROR'
            data['Recipient Phone Nbr'] = self.get_phone_number(address.tel_no)
            data['Recipient Email'] = ''
            data['Shipment Reference1'] = ''
            data['Shipment Reference2'] = ''
            data['Packaging Type'] = 105
            data['Declared Value'] = price
            data['Service Code'] = package_code
            data['Length'] = ''
            data['Width'] = ''
            data['Height'] = ''
            data['Line Item Quantity'] = product.quantity
            data['Line Item Code'] = product.sku
            data['Line Item Description'] = product.product_name
            data['Line Item  Quantity Unit'] = 'PCE'
            data['Unit Price'] = product.price
            data['Item Weight'] = product.per_item_weight / 1000
            data['Weight Unit'] = 'KG'
            data['Price'] = product.price * product.quantity
            data['HS Code'] = ''
            data['Country Of Manufacture'] = 'CN'
            data['Currency Code'] = 'GBP'
            rows.append([data[key] for key in self.spreadsheet_header])
            manifested_order = models.ManifestedOrder(
                order_id=order.order_id, country=country,
                service_code=package_code)
            self.manifested_orders.append(manifested_order)
        return rows
