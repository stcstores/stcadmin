from . new_product import NewProduct
from . new_range import NewRange
from . new_variation import NewVariation


class SingleProduct(NewProduct):

    def load_from_form(self, data):
        self.data = data
        self.name = data['title']
        self.barcode = data['barcode']
        self.description = data['description']
        self.vat_rate_id = int(data['vat_rate'])
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
        self.package_type = data['package_type']
        if len(data['location']) > 0:
            self.bay_id = self.get_bay_id(data['location'], self.department)
        else:
            self.bay_id = None

    def create_range(self):
        return NewRange(self.name, self.range_options).create()

    def get_products(self):
        product = NewVariation(
            product_range=self.product_range,
            barcode=self.barcode,
            description=self.description,
            vat_rate_id=self.vat_rate_id,
            weight=self.weight,
            height=self.height,
            length=self.length,
            width=self.width,
            large_letter_compatible=self.large_letter_compatible,
            stock_level=self.stock_level,
            price=self.price,
            bay_id=self.bay_id,
            options=self.options)
        return [product]

    def get_options(self):
        required_options = {
            'Department': self.department,
            'Brand': self.brand,
            'Supplier SKU': self.supplier_SKU,
            'Manufacturer': self.manufacturer,
            'Supplier': self.supplier,
            'Purchase Price': self.purchase_price,
            'Package Type': self.package_type}
        optional_options = {
            key.replace('opt_', ''): value for key, value in
            self.data.items() if key.startswith('opt_') and
            len(value) > 0}
        self.options = {**required_options, **optional_options}
        self.range_options = self.options.keys()
