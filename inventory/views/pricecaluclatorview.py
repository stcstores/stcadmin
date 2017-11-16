from ccapi import CCAPI
from django.views.generic.base import TemplateView
from inventory import models

from .views import InventoryUserMixin


class RangePriceCalculatorView(InventoryUserMixin, TemplateView):
    template_name = 'inventory/range_price_calculator.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        product_range = CCAPI.get_range(
            self.kwargs.get('range_id'))
        product_range.products = [
            CCAPI.get_product(p.id) for p in product_range.products]
        context_data['product_range'] = product_range
        context_data['countries'] = models.DestinationCountry.objects.all()
        return context_data
