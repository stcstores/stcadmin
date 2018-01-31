from datetime import datetime

from ccapi import CCAPI

from inventory.models import get_barcode

from .new_product import NewProduct
from .new_range import NewRange
from .new_variation import NewVariation


class SingleProduct(NewProduct):

    def load_from_form(self, data):
        self.data = data
        self.name = data['title']
        self.barcode = data['barcode'] or get_barcode()
        self.description = data['description']
        self.vat_rate = int(data['vat_rate'])
        self.weight = data['weight']
        self.height = data['height']
        self.length = data['length']
        self.width = data['width']
        self.stock_level = data['stock_level']
        self.price = data['price']
        self.large_letter_compatible = data['package_type'] == 'Large Letter'
        self.department = data['department']
        self.brand = data['brand']
        self.supplier_SKU = data['supplier_SKU']
        self.manufacturer = data['manufacturer']
        self.supplier = data['supplier']
        self.purchase_price = data['purchase_price']
        self.amazon_bullets = data['amazon_bullet_points']
        self.amazon_search_terms = data['amazon_search_terms']
        self.package_type = data['package_type']
        self.gender = data['gender']
        self.bay_name = data['location']
        if self.package_type in ('Heavy and Large', 'Courier'):
            self.international_shipping = 'Express'
        else:
            self.international_shipping = 'Standard'

    def create_range(self):
        return NewRange(self.name, self.range_options).create()

    def get_products(self):
        product = NewVariation(
            product_range=self.product_range,
            barcode=self.barcode,
            description=self.description,
            vat_rate=self.vat_rate,
            weight=self.weight,
            height=self.height,
            length=self.length,
            width=self.width,
            large_letter_compatible=self.large_letter_compatible,
            stock_level=self.stock_level,
            price=self.price,
            bay_name=self.bay_name,
            department=self.department,
            options=self.options)
        return [product]

    def get_options(self):
        required_options = {
            'Date Created': datetime.today().strftime('%Y-%m-%d'),
            'Department': self.department,
            'Brand': self.brand,
            'Supplier SKU': self.supplier_SKU,
            'Manufacturer': self.manufacturer,
            'Supplier': self.supplier,
            'Purchase Price': self.purchase_price,
            'Package Type': self.package_type,
            'International Shipping': self.international_shipping}
        if self.gender:
            required_options['Gender'] = self.gender
        optional_options = {
            key.replace('opt_', ''): value for key, value in
            self.data.items() if key.startswith('opt_') and
            len(value) > 0}
        if len(self.amazon_bullets) > 1:
            optional_options['Amazon Bullets'] = self.amazon_bullets
        if len(self.amazon_search_terms) > 1:
            optional_options['Amazon Search Terms'] = self.amazon_search_terms
        self.options = {**required_options, **optional_options}
        self.range_options = list(self.options.keys()) + ['Incomplete']
