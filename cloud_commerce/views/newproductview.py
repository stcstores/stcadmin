from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from ccapi import CCAPI
import time


class NewProductView(FormView):
    success_url = reverse_lazy('cloud_commerce:index')

    def create_range(self, range_name, options):
        range_id = CCAPI.create_range(range_name)
        time.sleep(1)
        self.range = CCAPI.get_range(range_id)
        while self.range.id == 0:
            time.sleep(1)
            self.range = CCAPI.get_range(range_id)
        self.range = CCAPI.get_range(range_id)
        self.range.id = range_id
        for option in options:
            self.range.add_product_option(option)

    def create_product(
            self, name, barcode, description, vat_rate_id, weight, height,
            length, width, large_letter_compatible, stock_level, price,
            options):
        if len(description) == 0:
            description = name
        product = self.range.add_product(
            name, barcode, description=description, vat_rate_id=vat_rate_id)
        product.set_product_scope(
            weight, height, length, width, large_letter_compatible)
        product.set_stock_level(stock_level)
        product.set_handling_time(1)
        product.set_base_price(price)
        for option, value in options.items():
            if len(value) > 0:
                product.set_option_value(option, value, create=True)
        return product
