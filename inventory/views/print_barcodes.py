from ccapi import CCAPI
from django.views.generic.base import TemplateView

from .views import InventoryUserMixin


class PrintBarcodeLabels(InventoryUserMixin, TemplateView):
    template_name = 'inventory/print_barcodes.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        product_range = CCAPI.get_range(
            self.kwargs.get('range_id'))
        for product in product_range.products:
            product.option_text = product.full_name.replace(
                '{} - '.format(product.name), '')
        context['product_range'] = product_range
        return context
