from ccapi import CCAPI


class NewVariation:

    def __init__(
            self, product_range, name=None, barcode=None, description=None,
            vat_rate=None, weight='', height='', length='',
            width='', large_letter_compatible=False, stock_level=None,
            price=None, bay_name=None, department=None, options={}):
        self.product_range = product_range
        self.name = name
        self.barcode = barcode
        self.description = description
        self.vat_rate = vat_rate
        self.weight = weight
        self.height = height
        self.length = length
        self.width = ''
        self.width = width
        self.width
        self.large_letter_compatible = large_letter_compatible
        self.stock_level = stock_level
        self.price = price
        self.bay_name = bay_name
        self.department = department
        self.options = options

    def create(self):
        if self.name is None:
            self.name = self.product_range.name
        if self.description is None or self.description == '':
            self.description = self.name

        if len(self.bay_name) > 0:
            self.bay_id = CCAPI.get_bay_id(
                self.bay_name, self.department, create=True)
        else:
            self.bay_id = CCAPI.get_bay_id(self.department, self.department)

        product = self.product_range.add_product(
            self.name, self.barcode, description=self.description,
            vat_rate=self.vat_rate)
        product.set_stock_level(self.stock_level)
        product.set_product_scope(
            weight=self.weight, height=self.height, length=self.length,
            width=self.width,
            large_letter_compatible=self.large_letter_compatible)
        product.set_handling_time(1)
        product.set_base_price(self.price)
        if self.bay_id is not None:
            product.add_bay(self.bay_id)
        for option, value in self.options.items():
            if len(value) > 0:
                product.set_option_value(option, value, create=True)
        factories = CCAPI.get_factories()
        factory = factories.names[self.options['Supplier']]
        CCAPI.update_product_factory_link(
            product_id=product.id, factory_id=factory.id,
            supplier_sku=self.options['Supplier SKU'],
            price=self.options['Purchase Price'])
        return product
