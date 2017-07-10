import time

from ccapi import CCAPI


class NewRange:

    def __init__(self, range_name, options=None, drop_down_options=[]):
        self.range_name = range_name
        self.options = options
        self.drop_down_options = drop_down_options

    def create(self):
        range_id = CCAPI.create_range(self.range_name)
        time.sleep(1)
        product_range = CCAPI.get_range(range_id)
        while product_range.id == 0:
            time.sleep(1)
            product_range = CCAPI.get_range(range_id)
        product_range = CCAPI.get_range(range_id)
        for option in self.options:
            drop_down = option in self.drop_down_options
            product_range.add_product_option(option, drop_down=drop_down)
        return product_range
