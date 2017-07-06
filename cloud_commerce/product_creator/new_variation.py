

class NewVariation:

    name = None
    description = None
    vat_rate_id = None
    weight = None
    height = None
    length = None
    large_letter_compatible = None
    stock_level = None
    price = None
    bay_id = None
    options = {}

    def __init__(
            self, product_range, name=None, barcode=None, description=None,
            vat_rate_id=None, weight=None, height=None, length=None,
            width=None, large_letter_compatible=None, stock_level=None,
            price=None, bay_id=None, options={}):
        self.product_range = product_range
        self.name = name
        self.barcode = barcode
        self.description = description
        self.vat_rate_id = vat_rate_id
        self.weight = weight
        self.height = height
        self.length = length
        self.width = width
        self.large_letter_compatible = large_letter_compatible
        self.stock_level = stock_level
        self.price = price
        self.bay_id = bay_id
        self.options = options

    def create(self):
        if self.name is None:
            self.name = self.product_range.name
        if self.description is None or self.description == '':
            self.description = self.name

        product = self.product_range.add_product(
            self.name, self.barcode, description=self.description,
            vat_rate_id=self.vat_rate_id)
        product.set_product_scope(
            self.weight, self.height, self.length, self.width,
            self.large_letter_compatible)
        product.set_stock_level(self.stock_level)
        product.set_handling_time(1)
        product.set_base_price(self.price)
        if self.bay_id is not None:
            product.add_bay(self.bay_id)
        for option, value in self.options.items():
            if len(value) > 0:
                product.set_option_value(option, value, create=True)
        return product
