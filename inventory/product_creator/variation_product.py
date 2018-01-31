from datetime import datetime

from ccapi import CCAPI

from inventory.models import get_barcode

from .new_product import NewProduct
from .new_range import NewRange
from .new_variation import NewVariation


class VariationProduct(NewProduct):

    def load_from_form(self, forms):
        self.forms = [form for form in forms]
        self.setup_data = self.forms[0].cleaned_data
        self.variation_data = self.forms[1].cleaned_data
        self.name = self.setup_data['title']
        self.description = self.setup_data['description']
        self.department = self.setup_data['department']
        self.supplier = self.setup_data['supplier']
        self.brand = self.setup_data['brand']
        self.manufacturer = self.setup_data['manufacturer']
        self.amazon_bullets = self.setup_data['amazon_bullet_points']
        self.amazon_search_terms = self.setup_data['amazon_search_terms']

    def get_products(self):
        self.products = []
        for index, data in enumerate(self.variation_data):
            if data['DELETE'] is True:
                continue
            options = self.options[index]
            product = self.get_variation(data, options)
            self.products.append(product)
        return self.products

    def get_variable_value(self, key, data):
        if key in data:
            return data[key]
        return self.setup_data[key]

    def get_variation(self, data, options):
        barcode = data['barcode'] or get_barcode()
        vat_rate = int(self.get_variable_value('vat_rate', data))
        weight = self.get_variable_value('weight', data)
        height = self.get_variable_value('height', data)
        length = self.get_variable_value('length', data)
        width = self.get_variable_value('width', data)
        stock_level = self.get_variable_value('stock_level', data)
        price = self.get_variable_value('price', data)
        package_type = self.get_variable_value('package_type', data)
        large_letter_compatible = package_type == 'Large Letter'
        bay_name = self.get_variable_value('location', data)
        product = NewVariation(
            product_range=self.product_range,
            barcode=barcode,
            description=self.description,
            vat_rate=vat_rate,
            weight=weight,
            height=height,
            length=length,
            width=width,
            large_letter_compatible=large_letter_compatible,
            stock_level=stock_level,
            price=price,
            bay_name=bay_name,
            department=self.department,
            options=options)
        return product

    def create_range(self):
        return NewRange(
            self.name, self.range_options,
            drop_down_options=self.drop_down_options).create()

    def get_options(self):
        self.options = [
            self.get_options_for_product(data) for data in self.variation_data]
        self.range_options = ['Incomplete']
        self.drop_down_options = [
            key.replace('opt_', '') for key, value in self.setup_data.items()
            if key.startswith('opt_') and value[0] == 'variation']
        for option in self.options:
            for key in option.keys():
                if key not in self.range_options:
                    self.range_options.append(key)

    def get_options_for_product(self, variation_data):
        package_type = self.get_variable_value(
            'package_type', variation_data)
        if package_type in ('Heavy and Large', 'Courier'):
            international_shipping = 'Express'
        else:
            international_shipping = 'Standard'
        required_options = {
            'Date Created': datetime.today().strftime('%Y-%m-%d'),
            'Department': self.department,
            'Brand': self.brand,
            'Supplier SKU': self.get_variable_value(
                'supplier_SKU', variation_data),
            'Manufacturer': self.manufacturer,
            'Supplier': self.supplier,
            'Package Type': package_type,
            'Purchase Price': self.get_variable_value(
                'purchase_price', variation_data),
            'International Shipping': international_shipping}
        gender = self.get_variable_value('gender', variation_data)
        if gender:
            required_options['Gender'] = gender
        optional_options = {}
        for key, option_settings in self.setup_data.items():
            if key.startswith('opt_'):
                use = option_settings[0]
                if use == 'unused':
                    continue
                if use == 'single':
                    value = option_settings[1]
                else:
                    value = variation_data[key]
                if len(value) > 0:
                    optional_options[key.replace('opt_', '')] = value
        if len(self.amazon_bullets) > 1:
            optional_options['Amazon Bullets'] = self.amazon_bullets
        if len(self.amazon_search_terms) > 1:
            optional_options['Amazon Search Terms'] = self.amazon_search_terms
        options = {**required_options, **optional_options}
        return options
