from ccapi import CCAPI


class NewProduct:

    def __init__(self, data):
        self.load_from_form(data)
        self.get_options()
        self.product_range = self.create_range()
        self.products = self.get_products()
        for product in self.products:
            product.create()
