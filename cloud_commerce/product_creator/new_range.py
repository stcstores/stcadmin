import time

from ccapi import CCAPI


class NewRange:

    def __init__(self, range_name, options=None):
        self.range_name = range_name
        self.options = options

    def create(self):
        range_id = CCAPI.create_range(self.range_name)
        time.sleep(1)
        product_range = CCAPI.get_range(range_id)
        while product_range.id == 0:
            time.sleep(1)
            product_range = CCAPI.get_range(range_id)
        product_range = CCAPI.get_range(range_id)
        for option in self.options:
            product_range.add_product_option(option)
        return product_range
